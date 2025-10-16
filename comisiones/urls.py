from django.urls import path
from . import views

urlpatterns = [
    path('listar/', views.listar_comisiones, name='comisiones_listar'),
    path('detalle/<str:comisionista>/', views.detalle_comisiones, name='comisiones_detalle'),
    path('registrar_pago/<str:comisionista>/', views.registrar_pago, name='registrar_pago'),
    path('editar_pago/<str:comisionista>/<int:pago_id>/', views.editar_pago, name='editar_pago'),
]