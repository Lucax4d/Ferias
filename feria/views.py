from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.decorators import admin_o_vendedor
from usuarios.models import Perfil
from usuarios.roles import rol_de

from .forms import PuestoForm
from .models import Producto, Puesto, Vendedor
from .permisos import puestos_gestionables


def inicio(request):
    productos = Producto.objects.filter(activo=True).select_related('puesto')[:12]
    return render(request, 'feria/inicio.html', {'productos': productos})


def puesto_lista(request):
    puestos = Puesto.objects.select_related('vendedor', 'ubicacion')
    gestionables = set(puestos_gestionables(request.user).values_list('pk', flat=True))
    return render(request, 'feria/puesto_lista.html', {
        'puestos': puestos,
        'gestionables': gestionables,
        'puede_crear': rol_de(request.user) in (Perfil.ADMIN, Perfil.VENDEDOR),
    })


@admin_o_vendedor
def puesto_crear(request):
    es_admin = rol_de(request.user) == Perfil.ADMIN
    vendedor = Vendedor.objects.filter(user=request.user).first()
    if not es_admin and vendedor is None:
        messages.error(request, 'Tu usuario aún no tiene un registro de vendedor.')
        return redirect('puesto_lista')
    if request.method == 'POST':
        form = PuestoForm(request.POST, es_admin=es_admin)
        if form.is_valid():
            puesto = form.save(commit=False)
            if not es_admin:
                puesto.vendedor = vendedor
            puesto.save()
            messages.success(request, 'Puesto creado.')
            return redirect('puesto_lista')
    else:
        form = PuestoForm(es_admin=es_admin)
    return render(request, 'feria/puesto_form.html', {'form': form, 'titulo': 'Nuevo puesto'})


@admin_o_vendedor
def puesto_editar(request, pk):
    es_admin = rol_de(request.user) == Perfil.ADMIN
    puesto = get_object_or_404(puestos_gestionables(request.user), pk=pk)
    if request.method == 'POST':
        form = PuestoForm(request.POST, instance=puesto, es_admin=es_admin)
        if form.is_valid():
            form.save()
            messages.success(request, 'Puesto actualizado.')
            return redirect('puesto_lista')
    else:
        form = PuestoForm(instance=puesto, es_admin=es_admin)
    return render(request, 'feria/puesto_form.html', {'form': form, 'titulo': 'Editar puesto'})


@admin_o_vendedor
def puesto_eliminar(request, pk):
    puesto = get_object_or_404(puestos_gestionables(request.user), pk=pk)
    if request.method == 'POST':
        puesto.delete()
        messages.success(request, 'Puesto eliminado.')
        return redirect('puesto_lista')
    return render(request, 'feria/puesto_confirmar_eliminar.html', {'puesto': puesto})