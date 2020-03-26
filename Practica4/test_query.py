"""
@author: Alfonso Carvajal
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'ratonGato.settings')
django.setup()
from django.contrib.auth.models import User
from datamodel.models import Game, Move


# consulta 1 --> comprobar si existe user con id=10, si no, crearlo
print("\nConsulta 1")
id_1 = 10
username_1 = 'andres'
user1 = User.objects.get_or_create(id=id_1)[0]
# si crea el user, su username esta vacio
if user1.username == '':
    print('No existe el usuario: creando usuario con id: ', id_1)
    user1.username = username_1
    user1.password = username_1
else:
    print('Existe usuario con id ' + str(user1.id))
user1.save()
print('User con id: ' + str(user1.id) + ', Nombre: ' + user1.username)

# consulta 2 --> comprobar si existe user con id=11, si no, crearlo
print("\nConsulta 2")
id_2 = 11
username_2 = 'victoria'
user2 = User.objects.get_or_create(id=id_2)[0]
if user2.username == '':
    print('No existe el usuario: creando usuario con id: ', id_2)
    user2.username = username_2
    user2.password = username_2
else:
    print('Existe usuario con id ' + str(user2.id))
user2.save()
print('User con id: ' + str(user2.id) + ', Nombre: ' + user2.username)

# crear juego y asignar a user con id=10
print("\nConsulta 3")
game1 = Game.objects.create(cat_user=user1)
game1.save()
print('Game con id: ' + str(game1.id) + ' creado')

print("\nConsulta 4")
# Buscar todos los juegos con 1 solo usuario asignado
# 1 solo usuario asignado =>
# que no tiene mouse_user porque cat_user tiene que existir
g = Game.objects.filter(mouse_user=None).order_by('id')
print('Hay ' + str(len(g)) + ' games con solo 1 usuario')
print(g)

# unimos al usuario con id=11 al game con menor id
print("\nConsulta 5")
g[0].mouse_user = user2
g[0].save()
print(g[0])

# Mover el gato pasando de la posicion 2 a la 11
print("\nConsulta 6")
move1 = Move.objects.create(game=g[0], origin=2,
                            target=11, player=g[0].cat_user)
print(g[0])
g[0].save()

# Mover el mouse pasando de la posicion 59 a la 52
print("\nConsulta 7")
move2 = Move.objects.create(game=g[0], origin=59,
                            target=52, player=g[0].mouse_user)
print(g[0])
g[0].save()
