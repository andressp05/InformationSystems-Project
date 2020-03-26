from django import forms
from django.contrib.auth.models import User
from datamodel.models import Move, Game


# Author: Andres
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password')


# Author: Andres
class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password')


# Author: Alfonso
class MoveForm(forms.ModelForm):
    origin = forms.IntegerField(min_value=Game.MIN_CELL,
                                max_value=Game.MAX_CELL)
    target = forms.IntegerField(min_value=Game.MIN_CELL,
                                max_value=Game.MAX_CELL)

    class Meta:
        model = Move
        fields = ('origin', 'target')
