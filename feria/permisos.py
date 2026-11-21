from usuarios.models import Perfil
from usuarios.roles import rol_de

from .models import Producto, Puesto


def puestos_gestionables(user):
    rol = rol_de(user)
    if rol == Perfil.ADMIN:
        return Puesto.objects.all()
    if rol == Perfil.VENDEDOR:
        return Puesto.objects.filter(vendedor__user=user)
    return Puesto.objects.none()


def productos_gestionables(user):
    rol = rol_de(user)
    if rol == Perfil.ADMIN:
        return Producto.objects.all()
    if rol == Perfil.VENDEDOR:
        return Producto.objects.filter(puesto__vendedor__user=user)
    return Producto.objects.none()