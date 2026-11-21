from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from .models import Perfil
from .roles import rol_de


def rol_requerido(*roles_permitidos):
    def decorador(vista):
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if rol_de(request.user) not in roles_permitidos:
                raise PermissionDenied
            return vista(request, *args, **kwargs)
        return envoltura
    return decorador


solo_admin = rol_requerido(Perfil.ADMIN)
admin_o_vendedor = rol_requerido(Perfil.ADMIN, Perfil.VENDEDOR)