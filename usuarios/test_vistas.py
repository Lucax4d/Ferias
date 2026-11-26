from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Perfil


class AutenticacionTests(TestCase):
    def setUp(self):
        self.ana = User.objects.create_user('ana', password='clave12345')

    def test_pagina_de_login_se_muestra_con_estilo(self):
        r = self.client.get(reverse('login'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'form-control')

    def test_pagina_de_registro_se_muestra_con_estilo(self):
        r = self.client.get(reverse('registro'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'form-control')

    def test_registro_crea_usuario_general_aunque_envien_otro_rol(self):
        r = self.client.post(reverse('registro'), {
            'username': 'nuevo',
            'email': 'nuevo@example.cl',
            'password1': 'ClaveSegura#2026',
            'password2': 'ClaveSegura#2026',
            'rol': 'admin',
        })
        self.assertEqual(r.status_code, 302)
        nuevo = User.objects.get(username='nuevo')
        self.assertEqual(nuevo.perfil.rol, Perfil.GENERAL)
        self.assertFalse(nuevo.is_superuser)

    def test_login_correcto_redirige_al_inicio(self):
        r = self.client.post(reverse('login'), {'username': 'ana', 'password': 'clave12345'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r['Location'], reverse('inicio'))

    def test_login_no_redirige_a_sitios_externos(self):
        r = self.client.post(
            reverse('login') + '?next=https://sitio-malicioso.example',
            {'username': 'ana', 'password': 'clave12345'},
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r['Location'], reverse('inicio'))
