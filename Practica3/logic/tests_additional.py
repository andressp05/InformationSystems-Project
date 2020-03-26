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
