from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from eventos.models import Evento
from usuarios.models import Perfil

from feria.models import Producto, Puesto, Ubicacion, Vendedor


class Command(BaseCommand):
    help = 'Carga datos de ejemplo para la demostración. Se puede ejecutar varias veces.'

    def add_arguments(self, parser):
        parser.add_argument('--password', default='clave12345',
                            help='Contraseña de los usuarios de ejemplo (solo para pruebas)')

    @transaction.atomic
    def handle(self, *args, **opciones):
        clave = opciones['password']

        def usuario(nombre, rol, superusuario=False):
            user, creado = User.objects.get_or_create(
                username=nombre,
                defaults={'is_staff': superusuario, 'is_superuser': superusuario},
            )
            if creado:
                user.set_password(clave)
                user.save()
            perfil, _ = Perfil.objects.get_or_create(user=user)
            perfil.rol = rol
            perfil.save()
            return user

        usuario('admin', Perfil.ADMIN, superusuario=True)
        usuario('cliente1', Perfil.GENERAL)

        feria = Ubicacion.objects.get_or_create(
            nombre='Feria Dominical', defaults={'direccion': 'Dirección de ejemplo 123, Arica'}
        )[0]
        agro = Ubicacion.objects.get_or_create(
            nombre='Agroferia Azapa', defaults={'direccion': 'Dirección de ejemplo 456, Arica'}
        )[0]

        datos = [
            ('vendedor1', 'Frutas del Valle', feria, 1, 'Frutas',
             [('Manzanas', 1500, 30), ('Naranjas', 1200, 40), ('Paltas', 3500, 15)]),
            ('vendedor2', 'Verduras Azapa', agro, 1, 'Verduras',
             [('Lechugas', 800, 25), ('Tomates', 1800, 20)]),
        ]
        for nombre_usuario, comercial, ubicacion, numero, nombre_puesto, productos in datos:
            user = usuario(nombre_usuario, Perfil.VENDEDOR)
            vendedor = Vendedor.objects.get_or_create(
                user=user, defaults={'nombre_comercial': comercial}
            )[0]
            puesto = Puesto.objects.get_or_create(
                ubicacion=ubicacion, numero=numero,
                defaults={'vendedor': vendedor, 'nombre': nombre_puesto},
            )[0]
            for nombre, precio, stock in productos:
                Producto.objects.get_or_create(
                    puesto=puesto, nombre=nombre, defaults={'precio': precio, 'stock': stock}
                )

        Evento.objects.get_or_create(
            nombre='Día de la Feria',
            defaults={
                'descripcion': 'Actividades para toda la familia.',
                'fecha': timezone.now() + timedelta(days=7),
                'ubicacion': feria,
            },
        )
        self.stdout.write(self.style.SUCCESS(
            f'Datos cargados. Usuarios: admin, vendedor1, vendedor2, cliente1 (contraseña: {clave})'
        ))
