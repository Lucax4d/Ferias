import tempfile
from io import BytesIO

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.messages import constants as message_constants
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from usuarios.models import Perfil

from .models import Producto, Puesto, Ubicacion, Vendedor


def png_de_prueba():
    buffer = BytesIO()
    Image.new('RGB', (10, 10), 'green').save(buffer, format='PNG')
    return buffer.getvalue()


def crear_vendedor_con_puesto():
    ubicacion = Ubicacion.objects.create(nombre='Feria Dominical', direccion='Av. Ejemplo 123')
    user = User.objects.create_user('vend', password='clave12345')
    user.perfil.rol = Perfil.VENDEDOR
    user.perfil.save()
    vendedor = Vendedor.objects.create(user=user, nombre_comercial='Frutas del Valle')
    puesto = Puesto.objects.create(vendedor=vendedor, ubicacion=ubicacion, nombre='Frutas', numero=1)
    return user, puesto


class CatalogoTests(TestCase):
    def setUp(self):
        self.user_vendedor, self.puesto = crear_vendedor_con_puesto()
        self.activo = Producto.objects.create(
            puesto=self.puesto, nombre='Manzanas', precio=1500, stock=5,
            descripcion='Manzanas frescas del valle.',
        )
        self.inactivo = Producto.objects.create(
            puesto=self.puesto, nombre='Peras', precio=1200, stock=5, activo=False,
        )
        self.cliente = User.objects.create_user('cliente', password='clave12345')

    def test_catalogo_es_publico_y_solo_muestra_activos(self):
        r = self.client.get(reverse('producto_catalogo'))
        self.assertContains(r, 'Manzanas')
        self.assertNotContains(r, 'Peras')

    def test_sin_portada_usa_la_imagen_por_defecto(self):
        r = self.client.get(reverse('producto_catalogo'))
        self.assertContains(r, 'imagen_por_defecto')

    def test_detalle_de_producto_activo(self):
        r = self.client.get(reverse('producto_detalle', args=[self.activo.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Manzanas frescas del valle.')
        self.assertContains(r, 'Frutas del Valle')

    def test_detalle_de_producto_inactivo_da_404(self):
        r = self.client.get(reverse('producto_detalle', args=[self.inactivo.pk]))
        self.assertEqual(r.status_code, 404)

    def test_boton_agregar_solo_con_sesion(self):
        url = reverse('agregar_al_carrito', args=[self.activo.pk])
        self.assertNotContains(self.client.get(reverse('producto_catalogo')), url)
        self.client.force_login(self.cliente)
        self.assertContains(self.client.get(reverse('producto_catalogo')), url)

    def test_los_errores_se_muestran_en_rojo(self):
        self.assertEqual(settings.MESSAGE_TAGS[message_constants.ERROR], 'danger')


class ImagenesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        cls._override = override_settings(MEDIA_ROOT=cls._tmp.name)
        cls._override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._override.disable()
        cls._tmp.cleanup()
        super().tearDownClass()

    def setUp(self):
        user, self.puesto = crear_vendedor_con_puesto()
        self.client.force_login(user)

    def datos(self, **extra):
        base = {'puesto': self.puesto.pk, 'nombre': 'Naranjas', 'precio': 1000, 'stock': 10, 'activo': 'on'}
        base.update(extra)
        return base

    def test_crea_producto_con_imagen(self):
        foto = SimpleUploadedFile('foto.png', png_de_prueba(), content_type='image/png')
        r = self.client.post(reverse('producto_crear'), self.datos(portada=foto))
        self.assertEqual(r.status_code, 302)
        producto = Producto.objects.get(nombre='Naranjas')
        self.assertTrue(producto.portada.name.startswith('portadas/'))

    def test_rechaza_archivo_que_no_es_imagen(self):
        falso = SimpleUploadedFile('virus.png', b'esto no es una imagen', content_type='image/png')
        r = self.client.post(reverse('producto_crear'), self.datos(portada=falso))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Producto.objects.filter(nombre='Naranjas').exists())
