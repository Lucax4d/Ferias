from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from usuarios.models import Perfil

from .models import Puesto, Ubicacion, Vendedor


class PuestoPermisosTests(TestCase):
    def crear_vendedor(self, nombre):
        user = User.objects.create_user(nombre, password='clave12345')
        user.perfil.rol = Perfil.VENDEDOR
        user.perfil.save()
        return Vendedor.objects.create(user=user, nombre_comercial=nombre)

    def setUp(self):
        self.ubicacion = Ubicacion.objects.create(nombre='Feria Dominical', direccion='Av. Ejemplo 123')
        self.v1 = self.crear_vendedor('vendedor1')
        self.v2 = self.crear_vendedor('vendedor2')
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