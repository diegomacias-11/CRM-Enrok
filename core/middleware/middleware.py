from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    """
    Middleware global:
    - Obliga a iniciar sesión en todas las vistas (excepto login/logout/reset).
    - Si el usuario pertenece al grupo 'Cliente', solo puede acceder a su panel,
      dispersión, materialidad y activación.
    - Evita redirecciones infinitas o errores por falta de argumentos.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # 🔓 URLs exentas de autenticación
        exempt_urls = [
            reverse('login'),
            reverse('logout'),
        ]

        # 🔄 Prefijos permitidos para recuperación de contraseña u otros
        reset_prefixes = ['/reset/']

        # ✅ Prefijos accesibles para usuarios del grupo "Cliente"
        # ⚠️ No uses reverse() con URLs que requieren argumentos
        allowed_client_prefixes = [
            reverse('panel_cliente'),
            reverse('dispersiones_cliente'),
            reverse('detalle_cliente'),
            '/materialidad/cliente/',
            '/activacion/cliente/',
            reverse('materialidad_agregar'),
            reverse('activacion_agregar'),
            '/media/',
            '/static/',
        ]

        # 1️⃣ Si el usuario NO está autenticado → redirigir a login
        if not request.user.is_authenticated:
            if not any(path.startswith(prefix) for prefix in reset_prefixes) and path not in exempt_urls:
                return redirect('login')

        # 2️⃣ Si el usuario pertenece al grupo "Cliente"
        elif request.user.groups.filter(name='Cliente').exists():
            if not any(path.startswith(p) for p in allowed_client_prefixes):
                cliente = getattr(request.user, 'cliente_asociado', None)
                # Si tiene cliente asociado, redirigir al panel
                if cliente:
                    return redirect('panel_cliente')
                # Si no tiene cliente asociado, redirigir al login
                return redirect('login')

        # 3️⃣ Continuar con la ejecución normal
        return self.get_response(request)
