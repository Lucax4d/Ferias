from django.db import models

from django.conf import settings
from django.db import models
from feria.models import Producto

class Carrito(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carrito"
    )
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.user.username}"

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["carrito", "producto"], name="producto_unico_por_carrito")
        ]

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

class Orden(models.Model):
    PENDIENTE = "pendiente"
    PAGADA = "pagada"
    RECHAZADA = "rechazada"
    ESTADOS = [
        (PENDIENTE, "Pendiente"),
        (PAGADA, "Pagada"),
        (RECHAZADA, "Rechazada"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="ordenes"
    )
    estado = models.CharField(max_length=10, choices=ESTADOS, default=PENDIENTE)
    total = models.PositiveIntegerField(default=0)
    buy_order = models.CharField(max_length=26, unique=True)  # límite de Webpay
    token_webpay = models.CharField(max_length=100, blank=True)
    codigo_autorizacion = models.CharField(max_length=20, blank=True)
    creada = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Orden {self.buy_order} ({self.get_estado_display()})"

class DetalleOrden(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    nombre_producto = models.CharField(max_length=100)
    precio_unitario = models.PositiveIntegerField()
    cantidad = models.PositiveIntegerField()

    def subtotal(self):
        return self.precio_unitario * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.nombre_producto}"