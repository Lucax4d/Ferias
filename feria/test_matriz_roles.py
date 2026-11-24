from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Producto, Puesto

# url, anónimo, usuario general, vendedor, administrador
MATRIZ = [
    ('/', 200, 200, 200, 200),
    ('/puestos/', 200, 200, 200, 200),
    ('/puestos/nuevo/', 302, 403, 200, 200),
    ('/productos/', 200, 200, 200, 200),
    ('/productos/nuevo/', 302, 403, 200, 200),
    ('/ubicaciones/', 200, 200, 200, 200),
    ('/ubicaciones/nueva/', 302, 403, 403, 200),
    ('/eventos/', 200, 200, 200, 200),
    ('/eventos/nuevo/', 302, 403, 403, 200),
    ('/carrito/', 302, 200, 200, 200),
    ('/carrito/ordenes/', 302, 200, 200, 200),
    ('/admin/', 302, 302, 302, 200),
]


class MatrizRolesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('cargar_datos', stdout=StringIO())

    def recorrer(self, nombre_usuario, columna):
        self.client.logout()
        if nombre_usuario:
            self.client.force_login(User.objects.get(username=nombre_usuario))
        for fila in MATRIZ:
            with self.subTest(usuario=nombre_usuario or 'anonimo', url=fila[0]):
                self.assertEqual(self.client.get(fila[0]).status_code, fila[columna])

    def test_anonimo(self):
        self.recorrer(None, 1)

    def test_usuario_general(self):
        self.recorrer('cliente1', 2)

    def test_vendedor(self):
        self.recorrer('vendedor1', 3)

    def test_administrador(self):
        self.recorrer('admin', 4)

    def test_vendedor_no_toca_lo_ajeno_por_url_directa(self):
        self.client.force_login(User.objects.get(username='vendedor1'))
        ajeno = Puesto.objects.get(vendedor__user__username='vendedor2')
        producto = Producto.objects.filter(puesto=ajeno).first()
        urls = [
            reverse('puesto_editar', args=[ajeno.pk]),
            reverse('puesto_eliminar', args=[ajeno.pk]),
            reverse('producto_editar', args=[producto.pk]),
            reverse('producto_eliminar', args=[producto.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)
