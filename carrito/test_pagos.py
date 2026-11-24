from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from feria.models import Producto, Puesto, Ubicacion, Vendedor

from .models import Carrito, DetalleOrden, ItemCarrito, Orden

APROBADA = {
    'status': 'AUTHORIZED', 'response_code': 0, 'buy_order': 'FTEST',
    'amount': 2000, 'authorization_code': '1234',
}


class PagoWebpayTests(TestCase):
    def setUp(self):
        ubicacion = Ubicacion.objects.create(nombre='Feria', direccion='Av. Ejemplo 123')
        dueno = User.objects.create_user('dueno', password='clave12345')
        vendedor = Vendedor.objects.create(user=dueno, nombre_comercial='Dueno')
        puesto = Puesto.objects.create(vendedor=vendedor, ubicacion=ubicacion, nombre='Frutas', numero=1)
        self.producto = Producto.objects.create(puesto=puesto, nombre='Manzanas', precio=1000, stock=5)
        self.ana = User.objects.create_user('ana', password='clave12345')
        self.beto = User.objects.create_user('beto', password='clave12345')
        self.orden = Orden.objects.create(user=self.ana, buy_order='FTEST', total=2000)
        DetalleOrden.objects.create(
            orden=self.orden, producto=self.producto, nombre_producto='Manzanas',
            precio_unitario=1000, cantidad=2,
        )
        carrito = Carrito.objects.create(user=self.ana)
        ItemCarrito.objects.create(carrito=carrito, producto=self.producto, cantidad=2)

    def con_token(self):
        self.orden.token_webpay = 'tok123'
        self.orden.save()

    def test_iniciar_pago_exige_post(self):
        self.client.force_login(self.ana)
        r = self.client.get(reverse('iniciar_pago', args=[self.orden.pk]))
        self.assertEqual(r.status_code, 405)

    def test_no_se_paga_orden_ajena(self):
        self.client.force_login(self.beto)
        r = self.client.post(reverse('iniciar_pago', args=[self.orden.pk]))
        self.assertEqual(r.status_code, 404)

    @patch('carrito.pagos.webpay.crear_transaccion',
           return_value={'token': 'tok123', 'url': 'https://webpay.test/pagar'})
    def test_iniciar_guarda_token_y_envia_a_webpay(self, _crear):
        self.client.force_login(self.ana)
        r = self.client.post(reverse('iniciar_pago', args=[self.orden.pk]))
        self.assertContains(r, 'https://webpay.test/pagar')
        self.orden.refresh_from_db()
        self.assertEqual(self.orden.token_webpay, 'tok123')

    @patch('carrito.pagos.webpay.confirmar', return_value=APROBADA)
    def test_pago_aprobado_descuenta_stock_y_vacia_carrito(self, _confirmar):
        self.con_token()
        self.client.post(reverse('webpay_retorno'), {'token_ws': 'tok123'})
        self.orden.refresh_from_db()
        self.producto.refresh_from_db()
        self.assertEqual(self.orden.estado, Orden.PAGADA)
        self.assertEqual(self.orden.codigo_autorizacion, '1234')
        self.assertEqual(self.producto.stock, 3)
        self.assertFalse(ItemCarrito.objects.filter(carrito__user=self.ana).exists())

    @patch('carrito.pagos.webpay.confirmar', return_value={**APROBADA, 'amount': 1})
    def test_monto_distinto_se_rechaza(self, _confirmar):
        self.con_token()
        self.client.post(reverse('webpay_retorno'), {'token_ws': 'tok123'})
        self.orden.refresh_from_db()
        self.producto.refresh_from_db()
        self.assertEqual(self.orden.estado, Orden.RECHAZADA)
        self.assertEqual(self.producto.stock, 5)

    @patch('carrito.pagos.webpay.confirmar',
           return_value={**APROBADA, 'status': 'FAILED', 'response_code': -1})
    def test_rechazo_del_banco_no_toca_stock_ni_carrito(self, _confirmar):
        self.con_token()
        self.client.post(reverse('webpay_retorno'), {'token_ws': 'tok123'})
        self.orden.refresh_from_db()
        self.producto.refresh_from_db()
        self.assertEqual(self.orden.estado, Orden.RECHAZADA)
        self.assertEqual(self.producto.stock, 5)
        self.assertTrue(ItemCarrito.objects.filter(carrito__user=self.ana).exists())

    @patch('carrito.pagos.webpay.confirmar', return_value=APROBADA)
    def test_pago_no_se_procesa_dos_veces(self, confirmar):
        self.con_token()
        self.client.post(reverse('webpay_retorno'), {'token_ws': 'tok123'})
        self.client.get(reverse('webpay_retorno'), {'token_ws': 'tok123'})
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)
        confirmar.assert_called_once()

    @patch('carrito.pagos.webpay.confirmar')
    def test_pago_anulado_por_el_usuario(self, confirmar):
        self.con_token()
        self.client.post(reverse('webpay_retorno'), {
            'TBK_TOKEN': 'tok123', 'TBK_ORDEN_COMPRA': 'FTEST', 'TBK_ID_SESION': 's',
        })
        self.orden.refresh_from_db()
        self.assertEqual(self.orden.estado, Orden.RECHAZADA)
        confirmar.assert_not_called()

    @patch('carrito.pagos.webpay.confirmar')
    def test_token_desconocido_no_hace_nada(self, confirmar):
        self.client.post(reverse('webpay_retorno'), {'token_ws': 'inventado'})
        self.orden.refresh_from_db()
        self.assertEqual(self.orden.estado, Orden.PENDIENTE)
        confirmar.assert_not_called()

    def test_resultado_de_orden_ajena_da_404(self):
        self.client.force_login(self.beto)
        r = self.client.get(reverse('pago_resultado', args=[self.orden.pk]))
        self.assertEqual(r.status_code, 404)
