from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from feria.models import Producto, Puesto, Ubicacion, Vendedor

from .models import Carrito, ItemCarrito


class BotonesCarritoTests(TestCase):
    def setUp(self):
        ubicacion = Ubicacion.objects.create(nombre='Feria', direccion='Av. Ejemplo 123')
        dueno = User.objects.create_user('dueno', password='clave12345')
        vendedor = Vendedor.objects.create(user=dueno, nombre_comercial='Dueno')
        puesto = Puesto.objects.create(vendedor=vendedor, ubicacion=ubicacion, nombre='Frutas', numero=1)
        self.producto = Producto.objects.create(puesto=puesto, nombre='Manzanas', precio=1000, stock=3)
        self.ana = User.objects.create_user('ana', password='clave12345')
        self.beto = User.objects.create_user('beto', password='clave12345')
        carrito = Carrito.objects.create(user=self.ana)
        self.item = ItemCarrito.objects.create(carrito=carrito, producto=self.producto, cantidad=1)

    def fijar(self, cantidad):
        self.item.cantidad = cantidad
        self.item.save()

    def test_anonimo_va_al_login(self):
        r = self.client.post(reverse('incrementar_item', args=[self.item.pk]))
        self.assertEqual(r.status_code, 302)

    def test_exige_post(self):
        self.client.force_login(self.ana)
        r = self.client.get(reverse('incrementar_item', args=[self.item.pk]))
        self.assertEqual(r.status_code, 405)

    def test_mas_suma_uno(self):
        self.client.force_login(self.ana)
        self.client.post(reverse('incrementar_item', args=[self.item.pk]))
        self.item.refresh_from_db()
        self.assertEqual(self.item.cantidad, 2)

    def test_mas_no_supera_el_stock(self):
        self.fijar(3)
        self.client.force_login(self.ana)
        self.client.post(reverse('incrementar_item', args=[self.item.pk]))
        self.item.refresh_from_db()
        self.assertEqual(self.item.cantidad, 3)

    def test_menos_resta_uno(self):
        self.fijar(2)
        self.client.force_login(self.ana)
        self.client.post(reverse('disminuir_item', args=[self.item.pk]))
        self.item.refresh_from_db()
        self.assertEqual(self.item.cantidad, 1)

    def test_menos_no_baja_de_uno(self):
        self.client.force_login(self.ana)
        self.client.post(reverse('disminuir_item', args=[self.item.pk]))
        self.item.refresh_from_db()
        self.assertEqual(self.item.cantidad, 1)

    def test_no_modifica_item_ajeno(self):
        self.client.force_login(self.beto)
        r = self.client.post(reverse('incrementar_item', args=[self.item.pk]))
        self.assertEqual(r.status_code, 404)
        self.item.refresh_from_db()
        self.assertEqual(self.item.cantidad, 1)
