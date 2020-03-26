from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date


# Author: Alfonso
class GameStatus():
    CREATED = 0
    ACTIVE = 1
    FINISHED = 2


class Game(models.Model):
    DEF_CAT1 = 0
    DEF_CAT2 = 2
    DEF_CAT3 = 4
    DEF_CAT4 = 6
    DEF_MOUSE = 59
    BOARD_LEN = 8
    MIN_CELL = 0
    MAX_CELL = BOARD_LEN * BOARD_LEN - 1
    # related name sirve para el inverse key, para que no haya problemas
    cat_user = models.ForeignKey(User, null=False,
                                 on_delete=models.CASCADE,
                                 related_name='games_as_cat')
    mouse_user = models.ForeignKey(User, null=True, blank=True,
                                   on_delete=models.CASCADE,
                                   related_name='games_as_mouse')
    # vars cat --> posicion de los gatos, no pueden ser NULL
    cat1 = models.IntegerField(null=False, default=DEF_CAT1)
    cat2 = models.IntegerField(null=False, default=DEF_CAT2)
    cat3 = models.IntegerField(null=False, default=DEF_CAT3)
    cat4 = models.IntegerField(null=False, default=DEF_CAT4)
    # var mouse --> posicion del raton
    mouse = models.IntegerField(null=False, default=DEF_MOUSE)
    # true --> Mueve el gato (comienza el gato)
    # false --> Mueve el raton
    cat_turn = models.BooleanField(null=False, default=True)
    status = models.IntegerField(null=False, default=GameStatus.CREATED)

    mouse_wins = [i for i in range(0, BOARD_LEN) if i % 2 == 0]
    validPositions = []
    for i in range(0, BOARD_LEN):
        for j in range(0, BOARD_LEN):
            # fila par --> los pares son blancos
            if i % 2 == 0:
                if j % 2 == 0:
                    validPositions.append(i*BOARD_LEN + j)
            else:
                # fila impar --> los impares son blancos
                if j % 2 != 0:
                    validPositions.append(i*BOARD_LEN + j)

    # Author: Alfonso
    def positionsValid(self):
        positions = [self.cat1, self.cat2, self.cat3, self.cat4, self.mouse]
        for i in positions:
            if i not in self.validPositions:
                return False

        return True

    # Author: Alfonso
    # sobreescribiendo metodo de save
    def save(self, *args, **kwargs):
        # if there are invalid positions, don't save
        if self.positionsValid() is False:
            raise ValidationError("Invalid cell for a cat or the mouse",
                                  code='invalid cell')
        if self.status == GameStatus.CREATED and self.mouse_user is not None:
            self.status = GameStatus.ACTIVE
        if self.gameEnded() is True:
            self.status = GameStatus.FINISHED
        super(Game, self).save(*args, **kwargs)

    def gameEnded(self):
        if self.mouse in self.mouse_wins:
            return True

        # Mouse is trapped
        possibleTargets = [self.mouse + self.BOARD_LEN + 1,
                           self.mouse + self.BOARD_LEN - 1,
                           self.mouse - self.BOARD_LEN + 1,
                           self.mouse - self.BOARD_LEN - 1]
        validTargets = [i for i in possibleTargets if i in self.validPositions]
        cats = [self.cat1, self.cat2, self.cat3, self.cat4]

        finalTargets = [i for i in validTargets if i not in cats]

        if len(finalTargets) > 0:
            return False
        else:
            return True



    # Author: Alfonso
    def full_clean(self):
        # Por si acaso no se ha inicializado cat_user
        try:
            if self.cat_user is not None and self.positionsValid() is False:
                raise ValidationError("Invalid cell for a cat or the mouse",
                                      code='invalid')
        except AttributeError:
            raise ValidationError("No cat user", code='Missing Player 1')

        super(Game, self).full_clean()

    # Author: Alfonso
    def __str__(self):
        # Default assumes Cat Turn
        cat = 'Cat [X]'
        mouse = 'Mouse [ ]'
        current_status = self.status
        switch = {GameStatus.CREATED: 'Created', GameStatus.ACTIVE: 'Active',
                  GameStatus.FINISHED: 'Finished'}
        positions = '('+str(self.cat1)+', '+str(self.cat2)
        positions = positions + ', '+str(self.cat3)+', '+str(self.cat4)+')'
        if self.cat_turn is False:
            cat = 'Cat [ ]'
            mouse = 'Mouse [X]'

        retStr = '(' + str(self.id) + ', ' + switch[current_status] + ')'
        retStr = retStr + "\t" + cat + ' ' + str(self.cat_user) + positions
        # if current_status != GameStatus.ACTIVE:
        if self.mouse_user is None:
            return retStr
        else:
            retStr = retStr+" --- "+mouse+" "
        return retStr+str(self.mouse_user)+'('+str(self.mouse) + ')'


class Move(models.Model):
    origin = models.IntegerField(null=False)
    target = models.IntegerField(null=False)
    game = models.ForeignKey(Game, null=False, related_name="moves",
                             on_delete=models.CASCADE)
    player = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    date = models.DateField(null=False,
                            default=date.today().strftime("%Y-%m-%d"))

    # Author: Alfonso
    def save(self, *args, **kwargs):
        if self.game.status != GameStatus.ACTIVE:
            raise ValidationError("Move not allowed",
                                  code='invalid move in inactive game')
        catPositions = [self.game.cat1, self.game.cat2,
                        self.game.cat3, self.game.cat4]
        flake = self.game.cat_turn
        if self.player == self.game.cat_user and self.game.cat_turn is True:

            # gatos solo pueden moverse hacia abajo
            possibleTargets = [self.origin + self.game.BOARD_LEN + 1,
                               self. origin + self.game.BOARD_LEN - 1]
            if self.game.mouse in possibleTargets:
                possibleTargets.remove(self.game.mouse)
            if self.origin not in catPositions:
                raise ValidationError("Move not allowed",
                                      code='invalid cat origin')
            elif self.target in catPositions:
                raise ValidationError("Move not allowed",
                                      code='invalid cat target')
            elif self.target not in self.game.validPositions:
                raise ValidationError("Move not allowed",
                                      code='invalid cat target')
            # if target no es valido --> gato ha movido mal eg. 2 filas
            elif self.target not in [cell for cell in possibleTargets
                                     if cell in self.game.validPositions]:
                raise ValidationError("Move not allowed",
                                      code='invalid cat target')

            # realizar el movimiento
            elif self.origin == self.game.cat1:
                self.game.cat1 = self.target
            elif self.origin == self.game.cat2:
                self.game.cat2 = self.target
            elif self.origin == self.game.cat3:
                self.game.cat3 = self.target
            else:
                self.game.cat4 = self.target
            self.game.cat_turn = not self.game.cat_turn
            super(Move, self).save(*args, **kwargs)
            self.game.save()

        # mueve raton
        elif self.player == self.game.mouse_user and flake is not True:
            # raton se puede mover hacia arriba o abajo
            possibleTargets = [self.origin + self.game.BOARD_LEN + 1,
                               self.origin + self.game.BOARD_LEN - 1,
                               self.origin - self.game.BOARD_LEN + 1,
                               self.origin - self.game.BOARD_LEN - 1]
            if self.origin != self.game.mouse:
                raise ValidationError("Move not allowed",
                                      code='invalid mouse origin')
            elif self.target in catPositions:
                raise ValidationError("Move not allowed",
                                      code='invalid mouse target')
            elif self.target not in self.game.validPositions:
                raise ValidationError("Move not allowed",
                                      code='invalid mouse target')
            elif self.target not in [cell for cell in possibleTargets
                                     if cell in self.game.validPositions]:
                raise ValidationError("Move not allowed",
                                      code='invalid mouse target')
            else:
                self.game.mouse = self.target
                self.game.cat_turn = not self.game.cat_turn
                super(Move, self).save(*args, **kwargs)
                self.game.save()

        else:
            raise ValidationError("Move not allowed", code='invalid player')

    # Author: Alfonso
    def __str__(self):
        move1 = "MOVE:\n\tOrigin: "+str(self.origin)+"\n\tTarget: "+str(self.target)
        move2 = "\n\tGame: "+str(self.player) + "\n\tPlayer: " + "\n\tDate: "
        return move1 + move2 + str(self.date)


class CounterManager(models.Manager):
    # Author: Andres
    def inc(self):
        objects = self.get_queryset()

        if len(objects) != 0:
            counter = objects[0]
        else:
            counter = self.loadCounter()

        value = self.get_current_value()
        counter.value = value + 1
        super(Counter, counter).save()
        return value+1

    # Author: Andres
    def get_current_value(self):
        objects = self.get_queryset()
        if len(objects) != 0:
            return objects[0].value
        else:
            return 0

    # Author: Andres
    def loadCounter(self):
        counter = Counter(value=0)
        super(Counter, counter).save()
        return counter


class Counter(models.Model):
    value = models.IntegerField(null=True)
    objects = CounterManager()

    # Author: Andres
    def save(self, *args, **kwargs):
        raise ValidationError("Insert not allowed|Inseción no permitida",
                              code='invalid second creation of a singleton')
