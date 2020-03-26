from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from datamodel.models import Game, GameStatus, Move
from operator import attrgetter


class QueryTests(TestCase):
    def test1(self):
        try:
            user1 = User.objects.get(id=10)
        except User.DoesNotExist:
            user1 = User.objects.create_user(id=10, username="test1")
        self.assertEqual(user1.id, 10)

        try:
            user2 = User.objects.get(id=11)
        except User.DoesNotExist:
            user2 = User.objects.create_user(id=11, username="test2")
        self.assertEqual(user2.id, 11)

        game = Game(cat_user=user1)
        game.full_clean()
        game.save()
        self.assertEqual(game.cat_user.id, 10)

        gamelist = []
        gamelisttemp = Game.objects.all()
        for game in gamelisttemp:
            if (game.mouse_user is None):
                gamelist.append(game)
        print(gamelist)

        playedgame = min(gamelist,key=attrgetter('id'))
        playedgame.mouse_user=user2
        game.full_clean()
        game.save()
        print(playedgame)

        move1 = Move.objects.create(game=playedgame, player=user1, origin=2, target=11)
        print(playedgame)
        self.assertEqual(game.cat2, 11)

        move2 = Move.objects.create(game=playedgame, player=user2, origin=59, target=52)
        print(playedgame)
        self.assertEqual(game.mouse, 52)
