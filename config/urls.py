"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from core.forms import LoginForm
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- Autenticación principal ---
    path(
        'accounts/login/',
        LoginView.as_view(template_name='auth/login.html', authentication_form=LoginForm),
        name='login'
    ),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),

    # --- Rutas integradas de Django (cambio de contraseña, reset, etc.) ---
    path('accounts/', include('django.contrib.auth.urls')),  # 👈 Esta es la clave

    # --- Core (redirección post-login) ---
    path('', include('core.urls')),

    # --- Apps del sistema ---
    path('clientes/', include('clientes.urls')),
    path('dispersiones/', include('dispersiones.urls')),
    path('comisiones/', include('comisiones.urls')),
    path('materialidad/', include('materialidad.urls')),
    path('activacion/', include('activacion.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)