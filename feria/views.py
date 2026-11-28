from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.decorators import admin_o_vendedor
from usuarios.models import Perfil
from usuarios.roles import rol_de

from .forms import ProductoForm, PuestoForm
from .models import Producto, Puesto, Vendedor
from .permisos import productos_gestionables, puestos_gestionables


def inicio(request):
    productos = Producto.objects.filter(activo=True).select_related('puesto__vendedor', 'puesto__ubicacion')[:12]
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


def producto_lista(request):
    propios = productos_gestionables(request.user)
    productos = Producto.objects.filter(
        Q(activo=True) | Q(pk__in=propios.values('pk'))
    ).select_related('puesto__vendedor')
    return render(request, 'feria/producto_lista.html', {
        'productos': productos,
        'gestionables': set(propios.values_list('pk', flat=True)),
        'puede_crear': rol_de(request.user) in (Perfil.ADMIN, Perfil.VENDEDOR),
    })


@admin_o_vendedor
def producto_crear(request):
    if not puestos_gestionables(request.user).exists():
        messages.error(request, 'Primero necesitas un puesto para agregar productos.')
        return redirect('puesto_lista')
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado.')
            return redirect('producto_lista')
    else:
        form = ProductoForm(user=request.user)
    return render(request, 'feria/producto_form.html', {'form': form, 'titulo': 'Nuevo producto'})


@admin_o_vendedor
def producto_editar(request, pk):
    producto = get_object_or_404(productos_gestionables(request.user), pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado.')
            return redirect('producto_lista')
    else:
        form = ProductoForm(instance=producto, user=request.user)
    return render(request, 'feria/producto_form.html', {'form': form, 'titulo': 'Editar producto'})


@admin_o_vendedor
def producto_eliminar(request, pk):
    producto = get_object_or_404(productos_gestionables(request.user), pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado.')
        return redirect('producto_lista')
    return render(request, 'feria/producto_confirmar_eliminar.html', {'producto': producto})


def producto_catalogo(request):
    productos = Producto.objects.filter(activo=True).select_related(
        'puesto__vendedor', 'puesto__ubicacion'
    )
    return render(request, 'feria/producto_catalogo.html', {'productos': productos})


def producto_detalle(request, pk):
    producto = get_object_or_404(
        Producto.objects.select_related('puesto__vendedor', 'puesto__ubicacion'),
        pk=pk,
        activo=True,
    )
    return render(request, 'feria/producto_detalle.html', {'producto': producto})
