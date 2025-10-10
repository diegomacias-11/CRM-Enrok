from django.urls import path
from .views import post_login_redirect

urlpatterns = [
    path('enrok/', post_login_redirect, name='enrok'),
]