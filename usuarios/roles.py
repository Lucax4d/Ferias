from .models import Perfil


def rol_de(user):
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return Perfil.ADMIN
    perfil, _ = Perfil.objects.get_or_create(user=user)
    return perfil.rol