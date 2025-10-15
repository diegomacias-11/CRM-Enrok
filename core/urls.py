from django.urls import path
from .views import post_login_redirect
from core import views

urlpatterns = [
    path('enrok/', post_login_redirect, name='enrok'),
    path('usuario/', views.editar_usuario, name='usuario'),

    # 📊 Rutas del reporte mensual de dispersiones
    path('reporte_dispersiones/', views.reporte_dispersiones, name='reporte_dispersiones'),
    path('reporte_dispersiones/detalle/', views.reporte_detalle_dispersiones, name='reporte_detalle_dispersiones'),
]