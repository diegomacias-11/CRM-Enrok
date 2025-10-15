from django.urls import path
from .views import post_login_redirect
from core import views

urlpatterns = [
    path('enrok/', post_login_redirect, name='enrok'),
    path('usuario/', views.editar_usuario, name='usuario')
]