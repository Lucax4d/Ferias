from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .decorators import rol_requerido
from .models import Perfil


@rol_requerido(Perfil.ADMIN)
def vista_admin(request):
    return HttpResponse('ok')


class RolesTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.general = User.objects.create_user('ana', password='clave12345')
        self.admin = User.objects.create_superuser('root', password='clave12345')

    def pedir(self, user):
        request = self.factory.get('/prueba/')
        request.user = user
        return vista_admin(request)

    def test_perfil_se_crea_solo(self):
        self.assertEqual(self.general.perfil.rol, Perfil.GENERAL)
        self.assertEqual(self.admin.perfil.rol, Perfil.ADMIN)

    def test_general_no_entra(self):
        with self.assertRaises(PermissionDenied):
            self.pedir(self.general)

    def test_admin_entra(self):
        self.assertEqual(self.pedir(self.admin).status_code, 200)

    def test_anonimo_va_a_login(self):
        self.assertEqual(self.pedir(AnonymousUser()).status_code, 302)