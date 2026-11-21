from django.contrib import admin
from django.contrib import admin
from .models import Carrito, ItemCarrito, Orden, DetalleOrden

admin.site.register(Carrito)
admin.site.register(ItemCarrito)
admin.site.register(Orden)
admin.site.register(DetalleOrden)