from django.conf import settings
from django.db import models

class Ubicacion(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

class Vendedor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vendedor"
    )
    nombre_comercial = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nombre_comercial

class Puesto(models.Model):
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, related_name="puestos")
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.PROTECT, related_name="puestos")
    nombre = models.CharField(max_length=100)
    numero = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["ubicacion", "numero"], name="puesto_unico_por_ubicacion")
        ]

    def __str__(self):
        return f"{self.nombre} (N° {self.numero})"

class Producto(models.Model):
    puesto = models.ForeignKey(Puesto, on_delete=models.CASCADE, related_name="productos")
    nombre = models.CharField(max_length=100)
    precio = models.PositiveIntegerField()  # CLP, sin decimales
    stock = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre