from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from feria.models import Ubicacion

from .models import Asistencia, Evento


class EventoTests(TestCase):
    def setUp(self):
        self.ubicacion = Ubicacion.objects.create(nombre='Feria Dominical', direccion='Av. Ejemplo 123')
        self.evento = Evento.objects.create(
            nombre='Dia de la feria', fecha=timezone.now() + timedelta(days=7), ubicacion=self.ubicacion
        )
        self.admin = User.objects.create_superuser('admin', password='clave12345')
        self.ana = User.objects.create_user('ana', password='clave12345')
        self.beto = User.objects.create_user('beto', password='clave12345')

    def test_lista_publica(self):
        self.assertContains(self.client.get(reverse('evento_lista')), 'Dia de la feria')

    def test_anonimo_va_al_login_al_crear(self):
        self.assertEqual(self.client.get(reverse('evento_crear')).status_code, 302)

    def test_general_recibe_403_al_crear(self):
        self.client.force_login(self.ana)
        self.assertEqual(self.client.get(reverse('evento_crear')).status_code, 403)

    def test_admin_crea_evento(self):
        self.client.force_login(self.admin)
        r = self.client.post(reverse('evento_crear'), {
            'nombre': 'Nuevo', 'descripcion': '', 'fecha': '2026-12-20T10:00',
            'ubicacion': self.ubicacion.pk,
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Evento.objects.filter(nombre='Nuevo').exists())

    def test_asistir_exige_post(self):
        self.client.force_login(self.ana)
        r = self.client.get(reverse('asistir', args=[self.evento.pk]))
        self.assertEqual(r.status_code, 405)

    def test_asistir_exige_login(self):
        r = self.client.post(reverse('asistir', args=[self.evento.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Asistencia.objects.exists())

    def test_asistir_no_duplica(self):
        self.client.force_login(self.ana)
        url = reverse('asistir', args=[self.evento.pk])
        self.client.post(url)
        self.client.post(url)
        self.assertEqual(Asistencia.objects.filter(evento=self.evento, user=self.ana).count(), 1)

    def test_cancela_su_asistencia(self):
        Asistencia.objects.create(evento=self.evento, user=self.ana)
        self.client.force_login(self.ana)
        self.client.post(reverse('cancelar_asistencia', args=[self.evento.pk]))
        self.assertFalse(Asistencia.objects.filter(user=self.ana).exists())

    def test_no_cancela_asistencia_ajena(self):
        Asistencia.objects.create(evento=self.evento, user=self.ana)
        self.client.force_login(self.beto)
        self.client.post(reverse('cancelar_asistencia', args=[self.evento.pk]))
        self.assertTrue(Asistencia.objects.filter(user=self.ana).exists())

    def test_admin_elimina_evento(self):
        self.client.force_login(self.admin)
        self.client.post(reverse('evento_eliminar', args=[self.evento.pk]))
        self.assertFalse(Evento.objects.filter(pk=self.evento.pk).exists())
