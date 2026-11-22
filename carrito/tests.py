from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from feria.models import Producto, Puesto, Ubicacion, Vendedor

from .models import Carrito, ItemCarrito, Orden


class CarritoOrdenesTests(TestCase):
    def setUp(self):
        ubicacion = Ubicacion.objects.create(nombre='Feria Dominical', direccion='Av. Ejemplo 123')
        dueno = User.objects.create_user('dueno', password='clave12345')
        vendedor = Vendedor.objects.create(user=dueno, nombre_comercial='Dueno')
        puesto = Puesto.objects.create(vendedor=vendedor, ubicacion=ubicacion, nombre='Frutas', numero=1)
        self.manzanas = Producto.objects.create(puesto=puesto, nombre='Manzanas', precio=1500, stock=3)
        self.peras = Producto.objects.create(puesto=puesto, nombre='Peras', precio=1200, stock=5, activo=False)
        self.kiwis = Producto.objects.create(puesto=puesto, nombre='Kiwis', precio=900, stock=0)
        self.ana = User.objects.create_user('ana', password='clave12345')
        self.beto = User.objects.create_user('beto', password='clave12345')
        self.admin = User.objects.create_superuser('admin', password='clave12345')

    def orden_de(self, user):
        return Orden.objects.create(user=user, buy_order=f'T{user.pk}ORDEN', total=1500)

    def test_anonimo_va_al_login(self):
        self.assertEqual(self.client.get(reverse('ver_carrito')).status_code, 302)

    def test_agregar_exige_post(self):
        self.client.force_login(self.ana)
        r = self.client.get(reverse('agregar_al_carrito', args=[self.manzanas.pk]))
        self.assertEqual(r.status_code, 405)

    def test_agrega_y_suma_cantidad(self):
        self.client.force_login(self.ana)
        url = reverse('agregar_al_carrito', args=[self.manzanas.pk])
        self.client.post(url)
        self.client.post(url)
        item = ItemCarrito.objects.get(carrito__user=self.ana, producto=self.manzanas)
        self.assertEqual(item.cantidad, 2)

    def test_no_supera_el_stock(self):
        self.client.force_login(self.ana)
        url = reverse('agregar_al_carrito', args=[self.manzanas.pk])
        for _ in range(6):
            self.client.post(url)
        item = ItemCarrito.objects.get(carrito__user=self.ana, producto=self.manzanas)
        self.assertEqual(item.cantidad, 3)

    def test_no_agrega_producto_inactivo(self):
        self.client.force_login(self.ana)
        r = self.client.post(reverse('agregar_al_carrito', args=[self.peras.pk]))
        self.assertEqual(r.status_code, 404)

    def test_no_agrega_producto_sin_stock(self):
        self.client.force_login(self.ana)
        self.client.post(reverse('agregar_al_carrito', args=[self.kiwis.pk]))
        self.assertFalse(ItemCarrito.objects.filter(producto=self.kiwis).exists())

    def test_no_quita_item_ajeno(self):
        carrito = Carrito.objects.create(user=self.ana)
        item = ItemCarrito.objects.create(carrito=carrito, producto=self.manzanas, cantidad=1)
        self.client.force_login(self.beto)
        r = self.client.post(reverse('quitar_del_carrito', args=[item.pk]))
        self.assertEqual(r.status_code, 404)
        self.assertTrue(ItemCarrito.objects.filter(pk=item.pk).exists())

    def test_orden_con_carrito_vacio_no_se_crea(self):
        self.client.force_login(self.ana)
        self.client.post(reverse('crear_orden'))
        self.assertFalse(Orden.objects.exists())

    def test_orden_copia_nombre_y_precio_de_la_base(self):
        self.client.force_login(self.ana)
        self.client.post(reverse('agregar_al_carrito', args=[self.manzanas.pk]))
        self.client.post(reverse('agregar_al_carrito', args=[self.manzanas.pk]))
        self.client.post(reverse('crear_orden'))
        orden = Orden.objects.get(user=self.ana)
        self.assertEqual(orden.total, 3000)
        self.assertEqual(orden.estado, Orden.PENDIENTE)
        self.assertLessEqual(len(orden.buy_order), 26)
        detalle = orden.detalles.get()
        self.assertEqual(detalle.nombre_producto, 'Manzanas')
        self.assertEqual(detalle.precio_unitario, 1500)
        self.assertEqual(detalle.cantidad, 2)

    def test_usuario_no_ve_orden_ajena(self):
        orden = self.orden_de(self.ana)
        self.client.force_login(self.beto)
        r = self.client.get(reverse('orden_detalle', args=[orden.pk]))
        self.assertEqual(r.status_code, 404)

    def test_admin_ve_cualquier_orden(self):
        orden = self.orden_de(self.ana)
        self.client.force_login(self.admin)
        r = self.client.get(reverse('orden_detalle', args=[orden.pk]))
        self.assertEqual(r.status_code, 200)

    def test_lista_muestra_solo_ordenes_propias(self):
        propia = self.orden_de(self.beto)
        ajena = self.orden_de(self.ana)
        self.client.force_login(self.beto)
        r = self.client.get(reverse('orden_lista'))
        self.assertContains(r, propia.buy_order)
        self.assertNotContains(r, ajena.buy_order)
