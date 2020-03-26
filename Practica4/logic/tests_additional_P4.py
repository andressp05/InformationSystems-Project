"""
@author: Alfonso
"""

from django.core.exceptions import ValidationError

from datamodel import tests
from datamodel.models import Game, GameStatus, Move


class AdditionalTests(tests.BaseModelTest):
    def setUp(self):
        super().setUp()
        self.game = Game.objects.create(
            cat_user=self.users[0], mouse_user=self.users[1],
            status=GameStatus.ACTIVE)

    def test1(self):
        """ Gatos no pueden mover hacia detras """
        moves = [
            {"origin": 0, "target": 9},
            {"origin": 59, "target": 50},
            {"origin": 9, "target": 0}
        ]
        cat_user = self.users[0]
        mouse_user = self.users[1]
        Move.objects.create(
            game=self.game, player=cat_user,
            origin=moves[0]["origin"], target=moves[0]["target"])
        Move.objects.create(
            game=self.game, player=mouse_user,
            origin=moves[1]["origin"], target=moves[1]["target"])
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
            Move.objects.create(
                game=self.game, player=cat_user,
                origin=moves[2]["origin"], target=moves[2]["target"])

    def test2(self):
        """ Gatos no pueden sobreponerse """
        moves = [
            {"origin": 0, "target": 9},
            {"origin": 59, "target": 50},
            {"origin": 2, "target": 9}
        ]
        cat_user = self.users[0]
        mouse_user = self.users[1]
        Move.objects.create(
            game=self.game, player=cat_user,
            origin=moves[0]["origin"], target=moves[0]["target"])
        Move.objects.create(
            game=self.game, player=mouse_user,
            origin=moves[1]["origin"], target=moves[1]["target"])
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
            Move.objects.create(
                game=self.game, player=cat_user,
                origin=moves[2]["origin"], target=moves[2]["target"])


class GameEndTests(tests.BaseModelTest):
    def setUp(self):
        super().setUp()
        self.game = Game.objects.create(
            cat_user=self.users[0], mouse_user=self.users[1],
            status=GameStatus.ACTIVE)

    def test1(self):
        """ Juego acaba cuando el raton llega al final y no antes """
        moves = [
            {"origin": 0, "target": 9},
            {"origin": 59, "target": 50},
            {"origin": 9, "target": 18},
            {"origin": 50, "target": 41},
            {"origin": 18, "target": 27},
            {"origin": 41, "target": 32},
            {"origin": 27, "target": 36},
            {"origin": 32, "target": 25},
            {"origin": 36, "target": 45},
            {"origin": 25, "target": 16},
            {"origin": 45, "target": 54},
            {"origin": 16, "target": 9},
            {"origin": 54, "target": 61}
        ]
        cat_user = self.users[0]
        mouse_user = self.users[1]
        # create the moves up until the end of the game
        i = 0
        for mov in moves:
            if i % 2 == 0:
                Move.objects.create(
                    game=self.game, player=cat_user,
                    origin=mov["origin"], target=mov["target"])
            else:
                Move.objects.create(
                    game=self.game, player=mouse_user,
                    origin=mov["origin"], target=mov["target"])
            i += 1

        self.assertEqual(self.game.status, GameStatus.ACTIVE)
        # Create the final move
        Move.objects.create(
            game=self.game, player=mouse_user,
            origin=9, target=0)

        self.assertEqual(self.game.status, GameStatus.FINISHED)

    def test2(self):
        """ Juego acaba correctamente cuando el raton es atrapado y no antes"""
        moves = [
            {"origin": 0, "target": 9},
            {"origin": 59, "target": 50},
            {"origin": 2, "target": 11},
            {"origin": 50, "target": 41},
            {"origin": 11, "target": 18},
            {"origin": 41, "target": 32},
            {"origin": 6, "target": 13},
            {"origin": 32, "target": 25},
            {"origin": 13, "target": 22},
            {"origin": 25, "target": 16}
        ]
        cat_user = self.users[0]
        mouse_user = self.users[1]
        # create the moves up until the end of the game
        i = 0
        for mov in moves:
            if i % 2 == 0:
                Move.objects.create(
                    game=self.game, player=cat_user,
                    origin=mov["origin"], target=mov["target"])
            else:
                Move.objects.create(
                    game=self.game, player=mouse_user,
                    origin=mov["origin"], target=mov["target"])
            i += 1

        self.assertEqual(self.game.status, GameStatus.ACTIVE)
        # Create the final move
        Move.objects.create(
            game=self.game, player=cat_user,
            origin=18, target=25)

        self.assertEqual(self.game.status, GameStatus.FINISHED)

    def test3(self):
        """ Juego no permite realizar movimientos una vez terminado cat wins """
        moves = [
            {"origin": 0, "target": 9},
            {"origin": 59, "target": 50},
            {"origin": 2, "target": 11},
            {"origin": 50, "target": 41},
            {"origin": 11, "target": 18},
            {"origin": 41, "target": 32},
            {"origin": 6, "target": 13},
            {"origin": 32, "target": 25},
            {"origin": 13, "target": 22},
            {"origin": 25, "target": 16},
            {"origin": 18, "target": 25}
        ]
        cat_user = self.users[0]
        mouse_user = self.users[1]
        # create the moves up until the end of the game
        i = 0
        for mov in moves:
            if i % 2 == 0:
                Move.objects.create(
                    game=self.game, player=cat_user,
                    origin=mov["origin"], target=mov["target"])
            else:
                Move.objects.create(
                    game=self.game, player=mouse_user,
                    origin=mov["origin"], target=mov["target"])
            i += 1

        self.assertEqual(self.game.status, GameStatus.FINISHED)

        # Mouse User First
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
            Move.objects.create(
                game=self.game, player=mouse_user,
                origin=16, target=9)

        # Now Cat User
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
            Move.objects.create(
                game=self.game, player=cat_user,
                origin=25, target=34)
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
            Move.objects.create(
                game=self.game, player=cat_user,
                origin=22, target=29)
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
            Move.objects.create(
                game=self.game, player=cat_user,
                origin=9, target=18)
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
            Move.objects.create(
                game=self.game, player=cat_user,
                origin=4, target=11)

    def test4(self):
        """ Juego no permite realizar movimientos una vez terminado mouse wins"""
        moves = [
            {"origin": 0, "target": 9},
            {"origin": 59, "target": 50},
            {"origin": 2, "target": 11},
            {"origin": 50, "target": 41},
            {"origin": 11, "target": 18},
            {"origin": 41, "target": 34},
            {"origin": 6, "target": 13},
            {"origin": 34, "target": 27},
            {"origin": 13, "target": 22},
            {"origin": 27, "target": 20},
            {"origin": 18, "target": 25},
            {"origin": 20, "target": 11},
            {"origin": 25, "target": 34},
            {"origin": 11, "target": 2}
        ]
        cat_user = self.users[0]
        mouse_user = self.users[1]
        # create the moves up until the end of the game
        i = 0
        for mov in moves:
            if i % 2 == 0:
                Move.objects.create(
                    game=self.game, player=cat_user,
                    origin=mov["origin"], target=mov["target"])
            else:
                Move.objects.create(
                    game=self.game, player=mouse_user,
                    origin=mov["origin"], target=mov["target"])
            i += 1

        self.assertEqual(self.game.status, GameStatus.FINISHED)

        # Mouse User First
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
            Move.objects.create(
                game=self.game, player=mouse_user,
                origin=16, target=9)

        # Now Cat User
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
            Move.objects.create(
                game=self.game, player=cat_user,
                origin=25, target=34)
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
            Move.objects.create(
                game=self.game, player=cat_user,
                origin=22, target=29)
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
            Move.objects.create(
                game=self.game, player=cat_user,
                origin=9, target=18)
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
            Move.objects.create(
                game=self.game, player=cat_user,
                origin=4, target=11)
