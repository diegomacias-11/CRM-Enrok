from django.urls import path
from . import views

urlpatterns = [
    path('listar/', views.lista_dispersiones, name='dispersiones_listar'),  # <--- aquí
    path('agregar/', views.agregar_dispersion, name='dispersiones_agregar'),
    path('editar/<int:pk>/', views.editar_dispersion, name='dispersiones_editar'),
    path('eliminar/<int:pk>/', views.dispersiones_eliminar, name='dispersiones_eliminar'),
    path('actualizar-estatus-dispersion/', views.actualizar_estatus_dispersion, name='actualizar_estatus_dispersion'),

]
