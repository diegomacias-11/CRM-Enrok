from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    """
    Middleware global:
    - Obliga a iniciar sesión en todas las vistas (excepto login/logout/reset).
    - Si el usuario pertenece al grupo 'Cliente', solo puede acceder a su panel,
      dispersión y materialidad.
    - Evita redirecciones infinitas o forzadas al detalle de materialidad.
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
        allowed_client_prefixes = [
            reverse('panel_cliente'),          # Panel principal del cliente
            reverse('dispersiones_cliente'),   # Reporte de dispersión
            reverse('detalle_cliente'),        # Detalle de dispersión
            '/materialidad/cliente/',          # Sección de materialidad
            reverse('materialidad_agregar'),
            '/media/',      # 👈 permite archivos subidos
            '/static/',     
        ]

        # 1️⃣ Si el usuario NO está autenticado → redirigir a login
        if not request.user.is_authenticated:
            if not any(path.startswith(prefix) for prefix in reset_prefixes) and path not in exempt_urls:
                return redirect('login')

        # 2️⃣ Si el usuario pertenece al grupo "Cliente"
        elif request.user.groups.filter(name='Cliente').exists():
            # Si intenta acceder a algo fuera de su área permitida
            if not any(path.startswith(p) for p in allowed_client_prefixes):
                cliente = getattr(request.user, 'cliente_asociado', None)
                # Redirigir correctamente a su panel (no al detalle)
                if cliente:
                    return redirect('panel_cliente')
                else:
                    return redirect('login')

        # 3️⃣ Continuar con la ejecución normal
        return self.get_response(request)
