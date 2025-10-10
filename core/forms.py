from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "Usuario o contraseña incorrectos.",
    }
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={
            "class": "input",
            "placeholder": "Usuario",
            "autofocus": "autofocus",
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "input",
            "placeholder": "••••••••",
        })
    )