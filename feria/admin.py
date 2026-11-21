from django.contrib import admin
from .models import Ubicacion, Vendedor, Puesto, Producto

admin.site.register(Ubicacion)
admin.site.register(Vendedor)
admin.site.register(Puesto)
admin.site.register(Producto)