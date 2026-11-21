from django.conf import settings
from django.db import models

class Perfil(models.Model):
    ADMIN = "admin"
    GENERAL = "general"
    VENDEDOR = "vendedor"
    ROLES = [
        (ADMIN, "Administrador"),
        (GENERAL, "Usuario General"),
        (VENDEDOR, "Vendedor"),
    ]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil"
    )
    rol = models.CharField(max_length=10, choices=ROLES, default=GENERAL)

    def __str__(self):
        return f"{self.user.username} ({self.get_rol_display()})"