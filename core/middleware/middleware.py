# core/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    """
    Middleware global que exige login para todas las vistas,
    excepto las rutas explícitamente exentas.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # 🔓 Rutas públicas (sin login)
        exempt_urls = [
            reverse('login'),
            reverse('logout'),
        ]

        # Estas rutas no tienen reverse dinámico (por los kwargs), así que mejor las chequeamos con startswith:
        reset_prefixes = [
            '/reset/',  # password_reset_confirm
        ]

        # Si el usuario no está autenticado y no está en las rutas exentas → redirigir a login
        if not request.user.is_authenticated:
            if not any(path.startswith(prefix) for prefix in reset_prefixes) and path not in exempt_urls:
                return redirect('login')

        # Continuar normalmente
        return self.get_response(request)
