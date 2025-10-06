from django.urls import path
from . import views

urlpatterns = [
    path('agregar/', views.agregar_cliente, name='clientes_agregar'),
    path('exito/', views.clientes_exito, name='clientes_exito'),
    path('listar/', views.listar_clientes, name='clientes_listar'),
    path('editar/<int:id>/', views.editar_cliente, name='clientes_editar'),
    path('eliminar/<int:id>/', views.clientes_eliminar, name='clientes_eliminar'),
]