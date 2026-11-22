import uuid
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from feria.models import Producto
from usuarios.models import Perfil
from usuarios.roles import rol_de

from .models import Carrito, DetalleOrden, ItemCarrito, Orden


def _carrito_de(user):
    carrito, _ = Carrito.objects.get_or_create(user=user)
    return carrito


def _ordenes_visibles(user):
    if rol_de(user) == Perfil.ADMIN:
        return Orden.objects.all()
    return Orden.objects.filter(user=user)


@login_required
def ver_carrito(request):
    carrito = _carrito_de(request.user)
    items = list(carrito.items.select_related('producto__puesto'))
    for item in items:
        item.subtotal = item.producto.precio * item.cantidad
    total = sum(item.subtotal for item in items)
    return render(request, 'carrito/carrito.html', {'items': items, 'total': total})


@login_required
@require_POST
def agregar(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id, activo=True)
    if producto.stock < 1:
        messages.error(request, f'{producto.nombre} no tiene stock.')
        return redirect('producto_lista')
    item, creado = ItemCarrito.objects.get_or_create(
        carrito=_carrito_de(request.user), producto=producto
    )
    if creado:
        messages.success(request, f'{producto.nombre} agregado al carrito.')
    elif item.cantidad >= producto.stock:
        messages.warning(request, f'No hay más stock de {producto.nombre}.')
    else:
        item.cantidad += 1
        item.save()
        messages.success(request, f'{producto.nombre} agregado al carrito.')
    return redirect('ver_carrito')


@login_required
@require_POST
def quitar(request, item_id):
    item = get_object_or_404(ItemCarrito, pk=item_id, carrito__user=request.user)
    item.delete()
    messages.info(request, 'Producto quitado del carrito.')
    return redirect('ver_carrito')


@login_required
@require_POST
def crear_orden(request):
    carrito = _carrito_de(request.user)
    items = list(carrito.items.select_related('producto'))
    if not items:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('ver_carrito')
    for item in items:
        if not item.producto.activo or item.cantidad > item.producto.stock:
            messages.error(request, f'No hay stock suficiente de {item.producto.nombre}.')
            return redirect('ver_carrito')
    with transaction.atomic():
        orden = Orden.objects.create(
            user=request.user,
            buy_order='F' + uuid.uuid4().hex[:20],
            total=sum(i.producto.precio * i.cantidad for i in items),
        )
        DetalleOrden.objects.bulk_create([
            DetalleOrden(
                orden=orden,
                producto=i.producto,
                nombre_producto=i.producto.nombre,
                precio_unitario=i.producto.precio,
                cantidad=i.cantidad,
            )
            for i in items
        ])
    messages.success(request, 'Orden creada. Queda pendiente de pago.')
    return redirect('orden_detalle', pk=orden.pk)


@login_required
def orden_lista(request):
    ordenes = _ordenes_visibles(request.user).select_related('user').order_by('-creada')
    return render(request, 'carrito/orden_lista.html', {'ordenes': ordenes})


@login_required
def orden_detalle(request, pk):
    orden = get_object_or_404(_ordenes_visibles(request.user), pk=pk)
    return render(request, 'carrito/orden_detalle.html', {
        'orden': orden,
        'detalles': orden.detalles.all(),
    })
