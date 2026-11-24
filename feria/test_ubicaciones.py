from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from usuarios.models import Perfil

from .models import Puesto, Ubicacion, Vendedor


class UbicacionTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', password='clave12345')
        self.general = User.objects.create_user('general', password='clave12345')
        user_vend = User.objects.create_user('vend', password='clave12345')
        user_vend.perfil.rol = Perfil.VENDEDOR
        user_vend.perfil.save()
        self.vendedor = Vendedor.objects.create(user=user_vend, nombre_comercial='Vend')
        self.ubicacion = Ubicacion.objects.create(nombre='Feria Dominical', direccion='Av. Ejemplo 123')

    def test_lista_publica(self):
        r = self.client.get(reverse('ubicacion_lista'))
        self.assertContains(r, 'Feria Dominical')

    def test_general_recibe_403_al_crear(self):
        self.client.force_login(self.general)
        self.assertEqual(self.client.get(reverse('ubicacion_crear')).status_code, 403)

    def test_vendedor_recibe_403_al_crear(self):
        self.client.force_login(self.vendedor.user)
        self.assertEqual(self.client.get(reverse('ubicacion_crear')).status_code, 403)

    def test_admin_crea_ubicacion(self):
        self.client.force_login(self.admin)
        r = self.client.post(reverse('ubicacion_crear'), {'nombre': 'Agroferia', 'direccion': 'Calle 1'})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Ubicacion.objects.filter(nombre='Agroferia').exists())

    def test_ubicacion_con_puestos_no_se_elimina(self):
        Puesto.objects.create(vendedor=self.vendedor, ubicacion=self.ubicacion, nombre='Frutas', numero=1)
        self.client.force_login(self.admin)
        self.client.post(reverse('ubicacion_eliminar', args=[self.ubicacion.pk]))
        self.assertTrue(Ubicacion.objects.filter(pk=self.ubicacion.pk).exists())

    def test_admin_elimina_ubicacion_sin_puestos(self):
        self.client.force_login(self.admin)
        self.client.post(reverse('ubicacion_eliminar', args=[self.ubicacion.pk]))
        self.assertFalse(Ubicacion.objects.filter(pk=self.ubicacion.pk).exists())
