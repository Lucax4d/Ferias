from django.db import models
from django.conf import settings
from django.db import models
from feria.models import Ubicacion

class Evento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    fecha = models.DateTimeField()
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.PROTECT, related_name="eventos")

    def __str__(self):
        return self.nombre

class Asistencia(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="asistencias")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["evento", "user"], name="una_asistencia_por_usuario")
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.evento.nombre}"