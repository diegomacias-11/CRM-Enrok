from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.materialidad_listar, name='materialidad_listar'),
    path('cliente/<int:cliente_id>/', views.materialidad_detalle, name='materialidad_detalle'),
    path('agregar/', views.materialidad_agregar, name='materialidad_agregar'),
    path('editar/<int:pk>/', views.materialidad_editar, name='materialidad_editar'),
    path("cliente/<int:cliente_id>/historial/<str:tipo_documento>/", views.materialidad_historial, name="materialidad_historial"),

]