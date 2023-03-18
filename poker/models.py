import datetime
import json
from itertools import combinations
from collections import defaultdict
from django.db import models
from django.utils import timezone
# Create your models here.


class Room(models.Model):
    room_name = models.CharField(max_length=40)
    current_players = models.IntegerField(default=0)


class Game(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    players = models.CharField(max_length=200)
    current_pot = models.IntegerField(default=0)
    game = models.CharField(max_length=1000)

    def CheckWinner(self):
        game_data = json.loads(self.game)
        game_data['winner'] = 'true'
        winner_hand = 0
        for index in game_data['players']:
            if game_data['players'][str(index)]['playerbet'] != 'Folded':
                hand = [
                    game_data['board']['1'],
                    game_data['board']['2'],
                    game_data['board']['3'],
                    game_data['board']['4'],
                    game_data['board']['5'],
                    game_data['players'][str(index)]['card1'],
                    game_data['players'][str(index)]['card2'],
                    ]
                maos_possiveis = combinations(hand, 5)
                for mao in maos_possiveis:
                    hand_value = self.CheckHand(mao)
                    if hand_value > game_data['players'][str(index)]['best_hand']:
                        game_data['players'][str(index)]['best_hand'] = hand_value
                        if hand_value > winner_hand:
                            winner_hand = hand_value
        winners =0
        for index in game_data['players']:
            if game_data['players'][str(index)]['playerbet'] != 'Folded':
                if winner_hand == game_data['players'][str(index)]['best_hand']:
                    game_data['players'][str(index)]['winner'] = 'true'
                    game_data['winner'] = 'true'
                    winners += 1
        if winners > 1:
            winner_points = 0
            card_order_dict = {"2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "1":10,"j":11, "q":12, "k":13, "a":14}
            for index in game_data['players']:
                if game_data['players'][str(index)]['winner'] == 'true':
                    game_data['players'][str(index)]['winner_points'] = card_order_dict[game_data['players'][str(index)]['card1'][1]] + card_order_dict[game_data['players'][str(index)]['card2'][1]]
                    winner_points = max(winner_points, game_data['players'][str(index)]['winner_points'])
            for index in game_data['players']:
                if game_data['players'][str(index)]['winner'] == 'true':
                    if winner_points != game_data['players'][str(index)]['winner_points']:
                        game_data['players'][str(index)]['winner'] = 'false'
                    else:
                        game_data['players'][str(index)]['playerbalance'] += int(game_data['pot']['totalpot'])
        else:
            for index in game_data['players']:
                if game_data['players'][str(index)]['winner'] == 'true':
                    game_data['players'][str(index)]['playerbalance'] += int(game_data['pot']['totalpot'])

                        
            


        return json.dumps(game_data)

    def CheckHand(self, hand):
        if self.CheckStraightFlush(hand):
            return 9
        if self.CheckFourOfAKind(hand):
            return 8
        if self.CheckFullHouse(hand):
            return 7
        if self.CheckFlush(hand):
            return 6
        if self.CheckStraight(hand):
            return 5
        if self.CheckThreeOfAKind(hand):
            return 4
        if self.CheckTwoPairs(hand):
            return 3
        if self.CheckPair(hand):
            return 2
        return 1
        
        
        
    def CheckStraightFlush(self, hand):
        if self.CheckFlush(hand) and self.CheckStraight(hand):
            return True
        else:
            return False
        
    def CheckFourOfAKind(self, hand):
        values = [i[1] for i in hand]
        value_counts = defaultdict(lambda:0)
        for v in values:
            value_counts[v]+=1
        if sorted(value_counts.values()) == [1,4]:
            return True
        return False
        
    def CheckFullHouse(self, hand):
        values = [i[1] for i in hand]
        value_counts = defaultdict(lambda:0)
        for v in values:
            value_counts[v]+=1
        if sorted(value_counts.values()) == [2,3]:
            return True
        return False
        
    def CheckFlush(self, hand):
        suits = [i[0] for i in hand]
        if len(set(suits))==1:
            return True
        else:
            return False

    def CheckStraight(self, hand):
        card_order_dict = {"2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "1":10,"j":11, "q":12, "k":13, "a":14}
        values = [i[1] for i in hand]
        value_counts = defaultdict(lambda:0)
        for v in values:
            value_counts[v] += 1
        rank_values = [card_order_dict[i] for i in values]
        value_range = max(rank_values) - min(rank_values)
        if len(set(value_counts.values())) == 1 and (value_range==4):
            return True
        else:
            if set(values) == set(["a", "2", "3", "4", "5"]):
                return True
            return False

    def CheckThreeOfAKind(self, hand):
        values = [i[1] for i in hand]
        value_counts = defaultdict(lambda:0)
        for v in values:
            value_counts[v]+=1
        if set(value_counts.values()) == set([3,1]):
            return True
        else:
            return False

    def CheckTwoPairs(self, hand):
        values = [i[1] for i in hand]
        value_counts = defaultdict(lambda:0)
        for v in values:
            value_counts[v]+=1
        if sorted(value_counts.values())==[1,2,2]:
            print(values)
            return True
        else:
            return False

    def CheckPair(self, hand):
        values = [i[1] for i in hand]
        value_counts = defaultdict(lambda:0)
        for v in values:
            value_counts[v]+=1
        if 2 in value_counts.values():
            return True
        else:
            return False
