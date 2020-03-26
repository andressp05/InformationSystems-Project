from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from datamodel.models import Game, GameStatus, Move, Counter
from logic.forms import UserForm, SignupForm, MoveForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from datamodel import constants
import json


# Author: Andres
# returns the landing page por the web
def landing(request):
    return render(request, 'mouse_cat/index.html')


# Author: Professor
def anonymous_required(f):
    def wrapped(request):
        if request.user.is_authenticated:
            return HttpResponseForbidden(
                errorHTTP(request,
                          exception="Action restricted to anonymous users"))
        else:
            return f(request)
    return wrapped


# Author: Professor
def errorHTTP(request, exception=None):
    if exception is None:
        msg = constants.INCORRECT_LOGIN
    else:
        msg = exception

    context_dict = {'msgs': json.dumps(msg)}
    return render(request, "mouse_cat/error.html", context_dict)


# Author: Andres
# returns the index page for the webpage
def index(request):
    return render(request, "mouse_cat/index.html")


# Author: Andres
# IN:   username
#       password
# Description:  if the request is a POST
#               Tries to login the user with username and password
#               If the user is logged in it does not allow it
#               If the user is not active it does not allow it
#
#               if the request is not a POST render the login form
@anonymous_required
def user_login(request):
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                request.session['counter'] = 0
                return redirect(reverse('index'))
            else:
                # An inactive account was used - no logging in!
                return HttpResponse(constants.ACCOUNT_DISABLED)
        else:
            # Bad login details were provided. So we can't log the user in.
            # user_form.add_error('username', 'Usuario/clave no válidos')
            # context_dict = {'message': "User or Password Incorrect"}
            context_dict = {'msgs': json.dumps(constants.INCORRECT_LOGIN),
                            'user_form': user_form}
            return render(request, "mouse_cat/login.html",
                          context_dict)
    return render(request, "mouse_cat/login.html", {'user_form': UserForm()})


# Author: Andres
# Description: logs the user out and redirects to the index page
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect(reverse('index'))


# Author: Andres
# Description:  renders the signup form
#               if the request is a POST validates the data and displays
#                   the corresponding errors
#               when the user signs up correctly, logs the user in and
#               renders the index page
@anonymous_required
def signup(request):
    if request.method == 'POST':
        signup_form = SignupForm(data=request.POST)
        signup_form.is_valid()
        # username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password != password2:
            context_dict = {'user_form': signup_form,
                            'msgs': json.dumps(constants.PSSWDS_DONT_MATCH)}
            # signup_form.add_error('password',
            # 'La clave y su repetición no coinciden')
            return render(request, "mouse_cat/signup.html",
                          context_dict)
        try:
            validate_password(password)
        except ValidationError:
            # err = '(?=.*too short)(?=.*at least 6 characters)(?=.*too common)'
            # signup_form.add_error('password', err)
            context_dict = {'user_form': signup_form,
                            'msgs': json.dumps(constants.PSSWD_TOO_SHORT)}
            # signup_form.errors['password'] = validerror.messages
            return render(request, "mouse_cat/signup.html",
                          context_dict)
        try:
            user = signup_form.save()
            user.set_password(user.password)
            user.save()
            login(request, user)
            return render(request, 'mouse_cat/index.html')
        except ValueError:
            # signup_form.add_error('username', 'Usuario duplicado')
            context_dict = {'user_form': signup_form,
                            'msgs': json.dumps(constants.USR_ALREADY_EXISTS)}
            return render(request, "mouse_cat/signup.html",
                          context_dict)
    else:
        signup_form = SignupForm()

    return render(request, 'mouse_cat/signup.html',
                  {'user_form': signup_form})


# Author: Alfonso
# Description:  creates the session counter if it doesn't exist
#               increments both the session counter and the global
#               counter
#               renders the counter page
def counter(request):
    # Obtenemos el counter de session y si no existe lo ponemos a 0
    if 'counter' not in request.session:
        request.session['counter'] = 0
    request.session['counter'] = request.session['counter'] + 1
    # incrementamos el counter global
    Counter.objects.inc()
    context_dict = {'counter_session': request.session['counter'],
                    'counter_global': Counter.objects.get_current_value()}

    return render(request, "mouse_cat/counter.html", context_dict)


# Author: Andres
# Description:  Creates a game and renders the new_game page with the
#               id of the created game and the name of the user
@login_required
def create_game(request):
    game = Game.objects.create(cat_user=request.user)
    context_dict = {'game': game}
    return render(request, "mouse_cat/new_game.html", context_dict)


# Author: Andres
# Description:  joins the user to the game with the greatest ID
#               renders the join_game page with the name of the user that has
#               joined the game and the ID of the game that was joined
@login_required
def join_game(request=None, game_id=None):
    if game_id is not None:
        request.session[constants.GAME_SELECTED_SESSION_ID] = game_id
        try:
            game = Game.objects.get(id=game_id)
            game.mouse_user = request.user
            game.status = GameStatus.ACTIVE
            game.cat_turn = True
            game.save()
        except Game.DoesNotExist:
            return HttpResponseNotFound('')

        if game.status == GameStatus.CREATED:
            return HttpResponseNotFound('')

        if game.status == GameStatus.FINISHED:
            return HttpResponseNotFound('')

        if game.cat_user == request.user:
            return HttpResponseNotFound('')

        # return render(request, "mouse_cat/index.html")
        return show_game(request)

    if request.method == 'GET':
        game_created = Game.objects.filter(status=GameStatus.CREATED).order_by('-id')
        game_mouse = game_created.filter(mouse_user=None).order_by('-id')
        if not game_mouse:
            context_dict = {}
            context_dict['msg_error'] = "No hay juegos disponibles"
            return render(request, "mouse_cat/join_game.html", context_dict)
        game_cat = game_mouse.exclude(cat_user=request.user).order_by('-id')
        if not game_cat:
            context_dict = {}
            context_dict['msg_error'] = constants.NO_GAMES_AVAILABLE
            return render(request, "mouse_cat/join_game.html", context_dict)
        context_dict = {'game_cat': game_cat}
        return render(request, "mouse_cat/join_game.html", context_dict)
    else:
        return render(request, "mouse_cat/error.html")


# Author: Alfonso
# Description:  If the request is a GET
#                   displays all the games that the user can join
#               If the request is a POST
#                   the ID of the game that has been selected is passed by
#                   argument is request. The user is redirected to the index
#                   page of the web
@login_required
def select_game(request=None, game_id=None):
    if game_id is not None:
        request.session[constants.GAME_SELECTED_SESSION_ID] = game_id
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return HttpResponseNotFound('')

        if game.status == GameStatus.CREATED:
            return join_game(request, game_id)

        if game.status == GameStatus.FINISHED:
            #return replay_game(request, game_id)
            return replay_game(request)

        if game.mouse_user != request.user and game.cat_user != request.user:
            return HttpResponseNotFound('')

        # return render(request, "mouse_cat/game.html"
        return show_game(request)

    if request.method == 'GET':
        user = request.user
        # No se pueden seleccionar juegos que hayan terminado
        as_cat = Game.objects.filter(cat_user=user).order_by('id')
        as_cat = as_cat.exclude(status=GameStatus.FINISHED)
        as_cat = as_cat.exclude(status=GameStatus.CREATED)
        as_mouse = Game.objects.filter(mouse_user=user).order_by('id')
        as_mouse = as_mouse.exclude(status=GameStatus.FINISHED)
        as_mouse = as_mouse.exclude(status=GameStatus.CREATED)
        to_join = Game.objects.filter(status=GameStatus.CREATED).order_by('id')
        to_join = to_join.filter(mouse_user=None).order_by('id')
        to_join = to_join.exclude(cat_user=request.user).order_by('id')
        as_cat_finished = Game.objects.filter(cat_user=user).order_by('id')
        as_cat_finished = as_cat_finished.exclude(status=GameStatus.CREATED)
        as_cat_finished = as_cat_finished.exclude(status=GameStatus.ACTIVE)
        as_mouse_finished = Game.objects.filter(mouse_user=user).order_by('id')
        as_mouse_finished = as_mouse_finished.exclude(status=GameStatus.CREATED)
        as_mouse_finished = as_mouse_finished.exclude(status=GameStatus.ACTIVE)
        context_dict = {'as_cat': as_cat, 'as_mouse': as_mouse,
                        'to_join': to_join, 'as_cat_finished': as_cat_finished,
                        'as_mouse_finished': as_mouse_finished}
        return render(request, "mouse_cat/select_game.html", context_dict)
    else:
        return render(request, "mouse_cat/error.html")

# Author: Alfonso
# Description:  if the user has selected a game then it creates the board
#               the game ID should be saved in session
#               if there has been no game selected then it renders an error
#
#               In the board,   the cat positions are represented by a 1
#                               the mouse positions by -1 and the rest by a 0
#               The board is rendered and the Move Form is included to allow
#               the user to move
@login_required
def show_game(request):
    try:
        game_id = request.session[constants.GAME_SELECTED_SESSION_ID]
    except KeyError:
        return render(request, "mouse_cat/error.html")
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return HttpResponseNotFound('')

    tablero = ([0] * (Game.MAX_CELL - Game.MIN_CELL + 1))
    tablero[game.mouse] = -1
    tablero[game.cat1] = tablero[game.cat2] = 1
    tablero[game.cat3] = tablero[game.cat4] = 1
    # Only the user that has lost will reach this point
    if game.status == GameStatus.FINISHED:
        context_dict = {'msgs': json.dumps(constants.LOSER)}
        if game.cat_user == request.user:
            context_dict['img'] = '/static/images/mouse_wins.jpg'
        else:
            context_dict['img'] = '/static/images/cat_wins.png'
        return render(request, "mouse_cat/loser.html", context_dict)

    move_form = MoveForm()

    context_dict = {'game': game, 'board': tablero, 'move_form': move_form}
    return render(request, "mouse_cat/game.html", context_dict)


# Author: Alfonso
# Description:  This function only allows for POSTs
#               With the data from the move form, tries to create a Move
#               if the move is valid, the game is updated and the new board
#               is shown.
#               if the move is invalid, the user is prompted to move again
@login_required
def move(request):
    if request.method == 'POST':
        player = request.user
        try:
            game_id = request.session[constants.GAME_SELECTED_SESSION_ID]
        except KeyError:
            return HttpResponseNotFound('')
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return HttpResponseNotFound('')

        move_form = MoveForm(data=request.POST)
        origin = int(request.POST.get('origin'))
        target = int(request.POST.get('target'))
        context_dict = {}
        try:
            Move.objects.create(
                game=game, player=player, origin=origin, target=target)
        except ValidationError:
            # move_form.add_error('target', 'Invalid Move: Try again')
            context_dict['msgs'] = json.dumps(constants.INVALID_MOVE)
            # return render(request, "mouse_cat/game.html", context_dict)

        tablero = ([0] * (Game.MAX_CELL - Game.MIN_CELL + 1))
        tablero[game.mouse] = -1
        tablero[game.cat1] = tablero[game.cat2] = 1
        tablero[game.cat3] = tablero[game.cat4] = 1
        context_dict['game'] = game
        context_dict['board'] = tablero
        if game.status == GameStatus.FINISHED:
            context_dict['msgs'] = json.dumps(constants.WINNER)
            if game.cat_user == request.user:
                context_dict['img'] = '/static/images/cat_wins.png'
            else:
                context_dict['img'] = '/static/images/mouse_wins.jpg'
            return render(request, "mouse_cat/loser.html", context_dict)

        move_form = MoveForm()
        context_dict['move_form'] = move_form
        return render(request, "mouse_cat/game.html", context_dict)
    else:
        return HttpResponseNotFound('')


@login_required
def replay_game_menu(request=None, game_id=None):
    if request.method == 'GET':
        user = request.user
        as_cat_finished = Game.objects.filter(cat_user=user).order_by('id')
        as_cat_finished = as_cat_finished.exclude(status=GameStatus.CREATED)
        as_cat_finished = as_cat_finished.exclude(status=GameStatus.ACTIVE)
        as_mouse_finished = Game.objects.filter(mouse_user=user).order_by('id')
        as_mouse_finished = as_mouse_finished.exclude(status=GameStatus.CREATED)
        as_mouse_finished = as_mouse_finished.exclude(status=GameStatus.ACTIVE)
        context_dict = {'as_cat_finished': as_cat_finished,
                        'as_mouse_finished': as_mouse_finished}
        return render(request, "mouse_cat/replay_menu.html", context_dict)
    else:
        return render(request, "mouse_cat/error.html")
# Author: Alfonso
# Description:  if the user has selected a game then it creates the board
#               the game ID should be saved in session
#               if there has been no game selected then it renders an error
#
#               In the board,   the cat positions are represented by a 1
#                               the mouse positions by -1 and the rest by a 0
#               The board is rendered and the Move Form is included to allow
#               the user to move
@login_required
def replay_game(request, game_id=None):
    if game_id is None:
        return render(request, "mouse_cat/error.html")
    else:
        try:
            request.session[constants.GAME_SELECTED_SESSION_ID] = game_id
        except KeyError:
            return render(request, "mouse_cat/error.html")
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return HttpResponseNotFound('')

        tablero = ([0] * (Game.MAX_CELL - Game.MIN_CELL + 1))
        tablero[game.DEF_MOUSE] = -1
        tablero[game.DEF_CAT1] = tablero[game.DEF_CAT2] = 1
        tablero[game.DEF_CAT3] = tablero[game.DEF_CAT4] = 1
        request.session[constants.GAME_MOVE_NUMBER] = 0
        context_dict = {'game': game, 'board': tablero}
        return render(request, "mouse_cat/replay.html", context_dict)

@login_required
def get_move(request):
    if request.method == 'POST':
        try:
            game_id = request.session[constants.GAME_SELECTED_SESSION_ID]
        except KeyError:
            return HttpResponseNotFound('')
        try:
            move_number = request.session[constants.GAME_MOVE_NUMBER]
        except KeyError:
            move_number = 0
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return HttpResponseNotFound('')

        moves = Move.objects.filter(game=game)
        # print(moves)
        if move_number > len(moves):
            return HttpResponseNotFound('')

        next_move = int(request.POST.get('shift'))
        # print("\nTRICK NEXT MOVE === ", next_move)
        # print("\nTRICK NEXT MOVE == 1 == ", next_move == 1)
        # print("\nTRICK MOVE NUMBER === ", move_number)
        # user has clicked next Move
        return_data = {}
        if next_move == 1:
            current_move = moves[move_number]
            return_data['origin'] = current_move.origin
            return_data['target'] = current_move.target
            return_data['previous'] = True
            return_data['next'] = len(moves) > move_number + 1
        # user has clicked prev Move
        else:
            current_move = moves[move_number - 1]
            return_data['origin'] = current_move.target
            return_data['target'] = current_move.origin
            return_data['previous'] = move_number > 1
            return_data['next'] = True

        move_number += next_move
        request.session[constants.GAME_MOVE_NUMBER] = move_number

        return JsonResponse(return_data, status=200)
    else:
        return HttpResponseNotFound('')
