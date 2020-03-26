"""
@author: rlatorre
"""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from datamodel import tests
from datamodel.models import Game, Move

GameStatus = Game.GameStatus

try:
    from .models import Counter

    FIRST_WEEK_ONLY = False
except ImportError:
    print("Counter variable has not been implemented"
          "Assuming first week test")
    FIRST_WEEK_ONLY = True


# ----  DO  NOT MODIFY THE FILE BELOW THIS LINE ----
class GameModelTests(tests.BaseModelTest):
    def setUp(self):
        super().setUp()

    def test1(self):
        """ Create Game with test. Test default values for
        cats, mouse and status"""
        game = Game(cat_user=self.users[0])
        game.full_clean()  # this function force validation to execute
        # very likely is not important at this step
        # reinforce constrains defined for forms
        game.save()
        self.assertIsNone(game.mouse_user)
        self.assertEqual(self.get_array_positions(game), [0, 2, 4, 6, 59])
        self.assertTrue(game.cat_turn)
        self.assertEqual(game.status, GameStatus.CREATED)

    def test2(self):
        """ OPTIONAL: If game is created with both cat user and
        mouse user then status=activated game"""
        game = Game(cat_user=self.users[0], mouse_user=self.users[1])
        game.save()
        self.assertEqual(self.get_array_positions(game), [0, 2, 4, 6, 59])
        self.assertTrue(game.cat_turn)
        self.assertEqual(game.status, GameStatus.ACTIVE)

    def test3(self):
        """ OPTIONAL: If mouse_user is added to a CREATED game
        then sttus became ACTIVE"""
        game = Game(cat_user=self.users[0])
        game.save()
        self.assertEqual(game.status, GameStatus.CREATED)
        game.mouse_user = self.users[1]
        game.save()
        self.assertEqual(game.status, GameStatus.ACTIVE)

    def test4(self):
        """Test status attribute"""
        """ROB note valid is never used"""
        states = [
            {"status": GameStatus.ACTIVE, "valid": True},
            {"status": GameStatus.FINISHED, "valid": True}
        ]

        for state in states:
            game = Game(cat_user=self.users[0],
                        mouse_user=self.users[1],
                        status=state["status"])
            game.full_clean()
            game.save()
            self.assertEqual(game.status, state["status"])

    def test5(self):
        """It is possible to create a game using only the cat user
        and the status"""
        states = [
            {"status": GameStatus.CREATED, "valid": True},
            {"status": GameStatus.ACTIVE, "valid": False},
            {"status": GameStatus.FINISHED, "valid": False}
        ]

        for state in states:
            try:
                game = Game(cat_user=self.users[0], status=state["status"])
                game.full_clean()
                game.save()
                self.assertEqual(game.status, state["status"])
            except ValidationError as err:
                with self.assertRaisesRegex(ValidationError,
                                            tests.MSG_ERROR_GAMESTATUS):
                    if not state["valid"]:
                        raise err

    def test6(self):
        """ It is not valid to create a game
        without the cat player"""
        for status in [GameStatus.CREATED, GameStatus.ACTIVE,
                       GameStatus.FINISHED]:
            with self.assertRaises(ValidationError):
                game = Game(mouse_user=self.users[1], status=status)
                game.full_clean()

    def test7(self):
        """
        # check board limits, notice that all
        # cats should not be in the same possition
        # varaibles Game.MIN_CELL and game.MAX_CELL
        # should be defined.

        This test may fail if code to reinforce
        constrain cat1 != cat2 is implemented
        """
        for id_cell in [Game.MIN_CELL, Game.MAX_CELL]:
            game = Game(
                cat_user=self.users[0],
                cat1=id_cell, cat2=id_cell,
                cat3=id_cell, cat4=id_cell, mouse=id_cell)
            game.full_clean()  # force Django validation Code
            game.save()

    def test8(self):
        """ Check if it is possible to place a cat/mouse out of
        the board. Creation must return an exception.
        That is, models should check if cat is in a valid square.
        """
        for id_cell in [Game.MIN_CELL - 1, Game.MAX_CELL + 1]:
            with self.assertRaises(ValidationError):
                game = Game(cat_user=self.users[0],
                            mouse_user=self.users[1], cat1=id_cell)
                game.full_clean()
                game.save()
            with self.assertRaises(ValidationError):
                game = Game(cat_user=self.users[0],
                            mouse_user=self.users[1], cat2=id_cell)
                game.full_clean()
                game.save()
            with self.assertRaises(ValidationError):
                game = Game(cat_user=self.users[0],
                            mouse_user=self.users[1], cat3=id_cell)
                game.full_clean()
                game.save()
            with self.assertRaises(ValidationError):
                game = Game(cat_user=self.users[0],
                            mouse_user=self.users[1], cat4=id_cell)
                game.full_clean()
                game.save()
            with self.assertRaises(ValidationError):
                game = Game(cat_user=self.users[0],
                            mouse_user=self.users[1], mouse=id_cell)
                game.full_clean()
                game.save()

    def test9(self):
        """Check use of "related_name" attribute in  model definition.
         The inverse relation name should be games_as_cat and
         games_as_mouse"""
        self.assertEqual(self.users[0].games_as_cat.count(), 0)
        self.assertEqual(self.users[1].games_as_mouse.count(), 0)
        self.assertEqual(
            User.objects.filter(
                games_as_cat__cat_user__username=self.
                users[0].username).count(), 0)
        self.assertEqual(User.objects.filter(
            games_as_mouse__mouse_user__username=self.
            users[1].username).count(), 0)

        game = Game(cat_user=self.users[0], mouse_user=self.users[1])
        game.save()
        self.assertEqual(self.users[0].games_as_cat.count(), 1)
        self.assertEqual(self.users[1].games_as_mouse.count(), 1)
        self.assertEqual(
            User.objects.filter(
                games_as_cat__cat_user__username=self.
                users[0].username).count(), 1)
        self.assertEqual(
            User.objects.filter(
                games_as_mouse__mouse_user__username=self.
                users[1].username).count(), 1)

        game = Game(cat_user=self.users[0])
        game.save()
        self.assertEqual(self.users[0].games_as_cat.count(), 2)
        self.assertEqual(self.users[1].games_as_mouse.count(), 1)
        self.assertEqual(
            User.objects.filter(
                games_as_cat__cat_user__username=self.
                users[0].username).count(), 2)
        self.assertEqual(
            User.objects.filter(
                games_as_mouse__mouse_user__username=self.
                users[1].username).count(), 1)

    def test10(self):
        """ OPTIONAL: Check if it is possible to place a cat/mouse
        in a black square. Creation must return an exception.
        That is, models should check if cat is in a valid square.
        """
        # 26, 44, 62, 7, 56 = black cells
        with self.assertRaisesRegex(ValidationError,
                                    tests.MSG_ERROR_INVALID_CELL):
            game = Game(cat_user=self.users[0], cat1=26)
            game = Game(cat_user=self.users[0],
                        mouse_user=self.users[1], cat1=26)
            game.full_clean()
            game.save()
        with self.assertRaisesRegex(ValidationError,
                                    tests.MSG_ERROR_INVALID_CELL):
            game = Game(cat_user=self.users[0], cat2=44)
            game.full_clean()
            game.save()
        with self.assertRaisesRegex(ValidationError,
                                    tests.MSG_ERROR_INVALID_CELL):
            game = Game(cat_user=self.users[0], cat3=62)
            game.full_clean()
            game.save()
        with self.assertRaisesRegex(ValidationError,
                                    tests.MSG_ERROR_INVALID_CELL):
            game = Game(cat_user=self.users[0], cat4=7)
            game.full_clean()
            game.save()
        with self.assertRaisesRegex(ValidationError,
                                    tests.MSG_ERROR_INVALID_CELL):
            game = Game(cat_user=self.users[0], mouse=56)
            game.full_clean()
            game.save()

    def test11(self):
        """ Check if __str__ function is available.
            If Game created (but not active) only cat information is printed
            If game is actived then cat and mouse position are given
            [X] vs [ ] report if it is the cat/mouse player turn.
        """
        game = Game(id=0, cat_user=self.users[0])
        self.assertEqual(str(game), "(0, Created)\tCat [X]"
                                    " cat_user_test(0, 2, 4, 6)")

        game.mouse_user = self.users[1]
        game.status = GameStatus.ACTIVE
        game.save()
        self.assertEqual(
            str(game),
            "(0, Active)\tCat [X] cat_user_test(0, 2, 4, 6)"
            " --- Mouse [ ] mouse_user_test(59)")
        game.cat_turn = False
        self.assertEqual(
            str(game),
            "(0, Active)\tCat [ ] "
            "cat_user_test(0, 2, 4, 6) --- Mouse [X] mouse_user_test(59)")

        game.status = GameStatus.FINISHED
        game.save()
        self.assertEqual(
            str(game),
            "(0, Finished)\tCat [ ]"
            " cat_user_test(0, 2, 4, 6) --- Mouse [X] mouse_user_test(59)"
        )


class MoveModelTests(tests.BaseModelTest):
    def setUp(self):
        super().setUp()

    def test1(self):
        """
        check basic move creation with default date
        default=timezone.now should initialize the date
        variable properlly.
        """
        game = Game.objects.create(
            cat_user=self.users[0], mouse_user=self.users[1],
            status=GameStatus.ACTIVE)
        moves = [
            {"player": self.users[0], "origin": 0, "target": 9},
            {"player": self.users[1], "origin": 59, "target": 50},
            {"player": self.users[0], "origin": 2, "target": 11},
        ]

        n_moves = 0
        for move in moves:
            Move.objects.create(
                game=game, player=move["player"],
                origin=move["origin"], target=move["target"])
            n_moves += 1
            self.assertEqual(game.moves.count(), n_moves)

    def test2(self):
        """ check if moves are possible in non active games"""
        game = Game(cat_user=self.users[0])
        game.save()
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
            Move.objects.create(game=game, player=self.users[0],
                                origin=0, target=9)


class CounterModelTests(TestCase):
    """This code check Counter implementation"""

    def setUp(self):
        # This should have no effect unless
        # counter class is badly implemented
        Counter.objects.all().delete()

    def test1(self):
        # create object
        # and search for it
        # it should exists and have id=1
        c = Counter()
        c.save()
        try:
            Counter.objects.get(pk=1)
            self.assertTrue(True)
        except Counter.DoesNotExist:
            self.assertTrue(False, "counter has id !=1")

        # create object with id = 7
        # and search for it
        # it should not exist
        c = Counter(id=7)
        c.save()
        try:
            Counter.objects.get(id=7)  # this counter should not exist
            self.assertTrue(False, "counter has id ==7")
        except Counter.DoesNotExist:
            self.assertTrue(True)

    def test2(self):
        # create counter
        # set it to zero
        # increment it
        c = Counter()  # value = 0
        c.inc()  # value = 1
        c.inc()  # value = 2
        c.save()
        self.assertEqual(2, c.get_value(),
                         "inc function does not work properlly)")

    def test3(self):
        # test get and set value
        c = Counter()
        c.set_value(5)
        c.inc()
        self.assertEqual(c.get_value(), 6)

    def test4(self):
        # define two Counter
        # since this is a solitom, both should be the same object
        c1 = Counter()
        c2 = Counter()
        c1.set_value(1)
        c2.set_value(2)
        self.assertEqual(c1.get_value(), 2)
        self.assertEqual(c2.get_value(), c1.get_value())
