import json
import random
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseServerError, HttpResponseBadRequest

# Create your views here.
from .models import Room, Game

def IndexView(request):
    list_of_rooms = Room.objects.all()
    context = {'list_of_rooms': list_of_rooms}
    return render(request, 'poker/index.html', context)

def GameView(request, pk):
    return render(request, 'poker/game.html', {'pk': pk})


def GameData(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)

        game = Game.objects.get(room_id=json_data['room'])
        
        player_list = list(filter(None, game.players.split(',')))
        index = player_list.index(json_data['nick'])

        game_data = json.loads(game.game)
        players = {}
        for i in range(len(player_list)):
            value = i - index
            if value < 0:
                value += 9
            players[value] = {
                    'dealer': game_data['players'][str(i)]['dealer'],
                    'playername': game_data['players'][str(i)]['playername'],
                    'playerbalance': game_data['players'][str(i)]['playerbalance'],
                    'playerbet': game_data['players'][str(i)]['playerbet'],
                    'playerbetvalue': game_data['players'][str(i)]['playerbetvalue'],
                    'playerbetcolor': game_data['players'][str(i)]['playerbetcolor'],
                    'card1': game_data['players'][str(i)]['card1'],
                    'card2': game_data['players'][str(i)]['card2'],
                    'winner': game_data['players'][str(i)]['winner'],
                }
        game_data['players'] = players
                


        return JsonResponse(game_data)
        

        
def RegisterPlayer(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        room = Room.objects.get(pk=json_data['room'])
        game, created = Game.objects.get_or_create(room_id=json_data['room'])


        
        player_list = list(filter(None, game.players.split(',')))
        if json_data['nick'] in player_list:
            return HttpResponseBadRequest()
        
        game.players += ',' + json_data['nick'] + ','
        game.save()

        if game.game:
            game_data = json.loads(game.game)
        else:
            game_data = {
                'players': {}, 
                'board': {
                    1: 'none',
                    2: 'none',
                    3: 'none',
                    4: 'none',
                    5: 'none'
                }, 
                'pot': {
                    'currentpot': 0, 
                    'pottext': 'Total: R$0'
                },
                'round_player': 0,
                'game_started': 'false',
                'winner': 'false',
            }
    
        player_list = list(filter(None, game.players.split(',')))
        for i in range(len(player_list)):
            dealer = ''
            if i == 0:
                dealer = 'true'
            else:
                dealer = 'false'
            game_data['players'][i] = {
                    'dealer': dealer,
                    'playername': player_list[i],
                    'playerbalance': 500,
                    'playerbet': 0,
                    'playerbetvalue': 0,
                    'playerbetcolor': 'black',
                    'card1': 'cardback',
                    'card2': 'cardback',
                    'best_hand': 0,
                    'winner': 'false',
                    'winner_points': 0,
                }
        
        game.game = json.dumps(game_data)
        game.save()


        room.current_players = len(player_list)
        room.save()
        return JsonResponse({
            'success': 'true'
        })



def StartGame(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        game = Game.objects.get(room_id=json_data['room'])
        game_data = json.loads(game.game)

        game_data['game_started'] = 'true'
        dealer_index = 0
        cards = ['ca','c2','c3','c4','c5','c6','c7','c8','c9','c10','cj','cq','ck','da','d2','d3','d4','d5','d6','d7','d8','d9','d10','dj','dq','dk','ha','h2','h3','h4','h5','h6','h7','h8','h9','h10','hj','hq','hk','sa','s2','s3','s4','s5','s6','s7','s8','s9','s10','sj','sq','sk']
        for index in range(1,6):
            game_data['board'][str(index)] = random.choice(cards)
        for index in game_data['players']:
            
            game_data['players'][str(index)]['playerbet'] = 0
            game_data['players'][str(index)]['playerbetvalue'] = 0
            game_data['players'][str(index)]['playerbetcolor'] = 'black'
            game_data['players'][str(index)]['best_hand'] = 0
            game_data['players'][str(index)]['winner'] = 'false'
            game_data['players'][str(index)]['winner_points'] = 0
            game_data['players'][str(index)]['card1'] = random.choice(cards)
            game_data['players'][str(index)]['card2'] = random.choice(cards)

            if game_data['players'][str(index)]['dealer'] == 'true':
                dealer_index = index
        game_data['players'][str(int(dealer_index) + 1)]['playerbalance'] -= 10
        game_data['players'][str(int(dealer_index) + 1)]['playerbet'] = 10
        game_data['players'][str(int(dealer_index) + 1)]['playerbetvalue'] = 10
        game_data['players'][str(int(dealer_index) + 1)]['playerbetcolor'] = 'lawngreen'
        game_data['players'][str(int(dealer_index) + 2)]['playerbalance'] -= 20
        game_data['players'][str(int(dealer_index) + 2)]['playerbet'] = 20
        game_data['players'][str(int(dealer_index) + 2)]['playerbetvalue'] = 20
        game_data['players'][str(int(dealer_index) + 2)]['playerbetcolor'] = 'lawngreen'
        game_data['pot']['currentpot'] = 20
        game_data['pot']['totalpot'] = 30
        game_data['pot']['pottext'] = 'Total: R$30'
        game_data['winner'] = 'false'
        player_list = list(filter(None, game.players.split(',')))
        value = int(dealer_index) + 3
        if value >= len(player_list):
            value = 0
        game_data['round_player'] = value
        game_data['round_player_nick'] = player_list[value]
        game_data['last_player'] = int(dealer_index) + 2
        game_data['last_player_nick'] = player_list[int(dealer_index) + 2]
        game_data['game_round'] = 0
        game.game = json.dumps(game_data)
        game.save()

        return JsonResponse({
            'success': 'true'
        })


def Fold(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        game = Game.objects.get(room_id=json_data['room'])
        game_data = json.loads(game.game)

        for index in game_data['players']:
            if game_data['players'][str(index)]['playername'] == json_data['nick']:
                game_data['players'][str(index)]['playerbet'] = 'Folded'
                game_data['players'][str(index)]['playerbetvalue'] = 0
                game_data['players'][str(index)]['playerbetcolor'] = 'black'
        
        player_list = list(filter(None, game.players.split(',')))
        index = player_list.index(json_data['nick'])
        value = int(index) + 1
        if value == len(player_list):
            value = 0
        while game_data['players'][str(value)]['playerbet'] == 'Folded':    
            value += 1
            if value == len(player_list):
                value = 0

        game_data['round_player'] = value
        game_data['round_player_nick'] = player_list[value]
        
        if game_data['last_player_nick'] == json_data['nick']:
            restart_round = False
            for index in game_data['players']:
                if game_data['players'][str(index)]['playerbet'] != 'Folded':
                    if game_data['players'][str(index)]['playerbetvalue'] != game_data['pot']['currentpot']:
                        restart_round = True
            if not restart_round:
                game_data['game_round'] += 1


        if game_data['last_player_nick'] == json_data['nick']:
            value = int(game_data['last_player'])
            while game_data['players'][str(value)]['playerbet'] == 'Folded':    
                value -= 1
                if value < 0:
                    value = len(player_list) - 1
            game_data['last_player'] = value
            game_data['last_player_nick'] = player_list[value]
        game.game = json.dumps(game_data)
        game.save()

        if game_data['game_round'] == 4:
            game.game = game.CheckWinner()
        game.save()

        return JsonResponse({
            'success': 'true'
        })


def Check(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        game = Game.objects.get(room_id=json_data['room'])
        game_data = json.loads(game.game)
        
        player_list = list(filter(None, game.players.split(',')))
        index = player_list.index(json_data['nick'])
        value = int(index) + 1
        if value == len(player_list):
            value = 0
        while game_data['players'][str(value)]['playerbet'] == 'Folded':    
            value += 1
            if value == len(player_list):
                value = 0

        game_data['round_player'] = value
        game_data['round_player_nick'] = player_list[value]
        
        if game_data['last_player_nick'] == json_data['nick']:
            restart_round = False
            for index in game_data['players']:
                if game_data['players'][str(index)]['playerbet'] != 'Folded':
                    if game_data['players'][str(index)]['playerbetvalue'] != game_data['pot']['currentpot']:
                        restart_round = True
            if not restart_round:
                game_data['game_round'] += 1
        game.game = json.dumps(game_data)
        game.save()
        if game_data['game_round'] == 4:
            game.game = game.CheckWinner()
        game.save()


        return JsonResponse({
            'success': 'true'
        })


def Bet(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        game = Game.objects.get(room_id=json_data['room'])
        game_data = json.loads(game.game)
        
        for index in game_data['players']:
            if game_data['players'][str(index)]['playername'] == json_data['nick']:
                game_data['players'][str(index)]['playerbalance'] -= int(json_data['value'])
                game_data['players'][str(index)]['playerbetvalue'] += int(json_data['value'])
                game_data['players'][str(index)]['playerbet'] = game_data['players'][str(index)]['playerbetvalue']
                game_data['players'][str(index)]['playerbetcolor'] = 'lawngreen'
                game_data['pot']['currentpot'] = max(game_data['pot']['currentpot'], game_data['players'][str(index)]['playerbetvalue'])
        game_data['pot']['totalpot'] += int(json_data['value'])
        game_data['pot']['pottext'] = 'Total: R$' + str(game_data['pot']['totalpot'])
        
        player_list = list(filter(None, game.players.split(',')))
        index = player_list.index(json_data['nick'])
        value = int(index) + 1
        if value == len(player_list):
            value = 0
        while game_data['players'][str(value)]['playerbet'] == 'Folded':    
            value += 1
            if value == len(player_list):
                value = 0

        game_data['round_player'] = value
        game_data['round_player_nick'] = player_list[value]
        
        if game_data['last_player_nick'] == json_data['nick']:
            restart_round = False
            for index in game_data['players']:
                if game_data['players'][str(index)]['playerbet'] != 'Folded':
                    if game_data['players'][str(index)]['playerbetvalue'] != game_data['pot']['currentpot']:
                        restart_round = True
            if not restart_round:
                game_data['game_round'] += 1


        game.game = json.dumps(game_data)
        game.save()

        if game_data['game_round'] == 4:
            game.game = game.CheckWinner()

        game.save()

        return JsonResponse({
            'success': 'true'
        })

