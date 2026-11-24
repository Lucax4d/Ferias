from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from usuarios.models import Perfil

from .models import Producto, Puesto, Ubicacion, Vendedor


class CargarDatosTests(TestCase):
    def cargar(self):
        call_command('cargar_datos', stdout=StringIO())

    def test_es_idempotente(self):
        self.cargar()
        antes = (User.objects.count(), Puesto.objects.count(), Producto.objects.count(),
                 Ubicacion.objects.count(), Vendedor.objects.count())
        self.cargar()
        despues = (User.objects.count(), Puesto.objects.count(), Producto.objects.count(),
                   Ubicacion.objects.count(), Vendedor.objects.count())
        self.assertEqual(antes, despues)

    def test_crea_los_roles(self):
        self.cargar()
        roles = {u.username: u.perfil.rol for u in User.objects.all()}
        self.assertEqual(roles['admin'], Perfil.ADMIN)
        self.assertEqual(roles['vendedor1'], Perfil.VENDEDOR)
        self.assertEqual(roles['vendedor2'], Perfil.VENDEDOR)
        self.assertEqual(roles['cliente1'], Perfil.GENERAL)
