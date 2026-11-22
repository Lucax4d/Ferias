from django.shortcuts import render

from .models import Producto


def inicio(request):
    productos = Producto.objects.filter(activo=True).select_related('puesto')[:12]
    return render(request, 'feria/inicio.html', {'productos': productos})