from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from usuarios.models import Perfil

from .models import Producto, Puesto, Ubicacion, Vendedor


def crear_vendedor(nombre):
    user = User.objects.create_user(nombre, password='clave12345')
    user.perfil.rol = Perfil.VENDEDOR
    user.perfil.save()
    return Vendedor.objects.create(user=user, nombre_comercial=nombre)


class PuestoPermisosTests(TestCase):
    def setUp(self):
        self.ubicacion = Ubicacion.objects.create(nombre='Feria Dominical', direccion='Av. Ejemplo 123')
        self.v1 = crear_vendedor('vendedor1')
        self.v2 = crear_vendedor('vendedor2')
        self.puesto1 = Puesto.objects.create(vendedor=self.v1, ubicacion=self.ubicacion, nombre='Frutas', numero=1)
        self.puesto2 = Puesto.objects.create(vendedor=self.v2, ubicacion=self.ubicacion, nombre='Verduras', numero=2)
        self.general = User.objects.create_user('general', password='clave12345')
        self.admin = User.objects.create_superuser('admin', password='clave12345')

    def test_lista_es_publica(self):
        self.assertEqual(self.client.get(reverse('puesto_lista')).status_code, 200)

    def test_anonimo_va_al_login(self):
        r = self.client.get(reverse('puesto_editar', args=[self.puesto1.pk]))
        self.assertEqual(r.status_code, 302)

    def test_general_recibe_403(self):
        self.client.force_login(self.general)
        r = self.client.get(reverse('puesto_editar', args=[self.puesto1.pk]))
        self.assertEqual(r.status_code, 403)

    def test_vendedor_edita_su_puesto(self):
        self.client.force_login(self.v1.user)
        r = self.client.get(reverse('puesto_editar', args=[self.puesto1.pk]))
        self.assertEqual(r.status_code, 200)

    def test_vendedor_no_edita_puesto_ajeno(self):
        self.client.force_login(self.v1.user)
        r = self.client.get(reverse('puesto_editar', args=[self.puesto2.pk]))
        self.assertEqual(r.status_code, 404)

    def test_vendedor_no_elimina_puesto_ajeno(self):
        self.client.force_login(self.v1.user)
        r = self.client.post(reverse('puesto_eliminar', args=[self.puesto2.pk]))
        self.assertEqual(r.status_code, 404)
        self.assertTrue(Puesto.objects.filter(pk=self.puesto2.pk).exists())

    def test_admin_edita_cualquiera(self):
        self.client.force_login(self.admin)
        r = self.client.get(reverse('puesto_editar', args=[self.puesto2.pk]))
        self.assertEqual(r.status_code, 200)

    def test_vendedor_crea_puesto_a_su_nombre(self):
        self.client.force_login(self.v1.user)
        r = self.client.post(reverse('puesto_crear'), {
            'ubicacion': self.ubicacion.pk, 'nombre': 'Quesos', 'numero': 3,
        })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Puesto.objects.get(nombre='Quesos').vendedor, self.v1)

    def test_numero_repetido_en_ubicacion_se_rechaza(self):
        self.client.force_login(self.v1.user)
        r = self.client.post(reverse('puesto_crear'), {
            'ubicacion': self.ubicacion.pk, 'nombre': 'Otro', 'numero': 1,
        })
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Puesto.objects.filter(nombre='Otro').exists())


class ProductoPermisosTests(TestCase):
    def setUp(self):
        ubicacion = Ubicacion.objects.create(nombre='Feria Dominical', direccion='Av. Ejemplo 123')
        self.v1 = crear_vendedor('vendedor1')
        self.v2 = crear_vendedor('vendedor2')
        self.puesto1 = Puesto.objects.create(vendedor=self.v1, ubicacion=ubicacion, nombre='Frutas', numero=1)
        self.puesto2 = Puesto.objects.create(vendedor=self.v2, ubicacion=ubicacion, nombre='Verduras', numero=2)
        self.prod1 = Producto.objects.create(puesto=self.puesto1, nombre='Manzanas', precio=1500, stock=10)
        self.prod2 = Producto.objects.create(puesto=self.puesto2, nombre='Lechugas', precio=800, stock=5)
        self.inactivo = Producto.objects.create(
            puesto=self.puesto1, nombre='Peras', precio=1200, stock=0, activo=False
        )
        self.general = User.objects.create_user('general', password='clave12345')
        self.admin = User.objects.create_superuser('admin', password='clave12345')

    def test_lista_publica_solo_muestra_activos(self):
        r = self.client.get(reverse('producto_lista'))
        self.assertContains(r, 'Manzanas')
        self.assertNotContains(r, 'Peras')

    def test_vendedor_ve_sus_productos_inactivos(self):
        self.client.force_login(self.v1.user)
        self.assertContains(self.client.get(reverse('producto_lista')), 'Peras')

    def test_general_recibe_403_al_crear(self):
        self.client.force_login(self.general)
        self.assertEqual(self.client.get(reverse('producto_crear')).status_code, 403)

    def test_vendedor_crea_producto_en_su_puesto(self):
        self.client.force_login(self.v1.user)
        r = self.client.post(reverse('producto_crear'), {
            'puesto': self.puesto1.pk, 'nombre': 'Naranjas', 'precio': 1000, 'stock': 20, 'activo': 'on',
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Producto.objects.filter(nombre='Naranjas', puesto=self.puesto1).exists())

    def test_vendedor_no_crea_producto_en_puesto_ajeno(self):
        self.client.force_login(self.v1.user)
        r = self.client.post(reverse('producto_crear'), {
            'puesto': self.puesto2.pk, 'nombre': 'Intruso', 'precio': 1000, 'stock': 1, 'activo': 'on',
        })
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Producto.objects.filter(nombre='Intruso').exists())

    def test_vendedor_no_edita_producto_ajeno(self):
        self.client.force_login(self.v1.user)
        r = self.client.get(reverse('producto_editar', args=[self.prod2.pk]))
        self.assertEqual(r.status_code, 404)

    def test_vendedor_no_elimina_producto_ajeno(self):
        self.client.force_login(self.v1.user)
        r = self.client.post(reverse('producto_eliminar', args=[self.prod2.pk]))
        self.assertEqual(r.status_code, 404)
        self.assertTrue(Producto.objects.filter(pk=self.prod2.pk).exists())

    def test_admin_edita_cualquier_producto(self):
        self.client.force_login(self.admin)
        r = self.client.get(reverse('producto_editar', args=[self.prod2.pk]))
        self.assertEqual(r.status_code, 200)

    def test_precio_negativo_se_rechaza(self):
        self.client.force_login(self.v1.user)
        r = self.client.post(reverse('producto_crear'), {
            'puesto': self.puesto1.pk, 'nombre': 'Gratis', 'precio': -5, 'stock': 1, 'activo': 'on',
        })
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Producto.objects.filter(nombre='Gratis').exists())