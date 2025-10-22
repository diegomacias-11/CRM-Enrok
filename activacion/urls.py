from django.urls import path
from . import views

urlpatterns = [
    path('listar/', views.activacion_listar, name='activacion_listar'),
    path('cliente/<int:cliente_id>/', views.activacion_detalle, name='activacion_detalle'),
    path('agregar/', views.activacion_agregar, name='activacion_agregar'),
    path('editar/<int:pk>/', views.activacion_editar, name='activacion_editar'),
    path('historial/<int:cliente_id>/<str:tipo_documento>/', views.activacion_historial, name='activacion_historial'),
]
