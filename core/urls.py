from django.urls import path
from .views import (
    post_login_redirect,
    editar_usuario,
    reporte_dispersiones,
    reporte_detalle_dispersiones,
    panel_cliente,
    dispersiones_cliente,
    reporte_detalle_cliente
)

urlpatterns = [
    path('enrok/', post_login_redirect, name='enrok'),
    path('usuario/', editar_usuario, name='usuario'),
    path('cliente/panel/', panel_cliente, name='panel_cliente'),

    # 📊 Rutas del reporte mensual de dispersiones
    path('reporte_dispersiones/', reporte_dispersiones, name='reporte_dispersiones'),
    path('reporte_dispersiones/detalle/', reporte_detalle_dispersiones, name='reporte_detalle_dispersiones'),

    # Reportes cliente
    path('dispersiones/cliente/', dispersiones_cliente, name='dispersiones_cliente'),
    path('detalle/cliente/', reporte_detalle_cliente, name='detalle_cliente'),

]