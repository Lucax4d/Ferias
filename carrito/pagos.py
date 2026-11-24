from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.db.models.functions import Greatest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from feria.models import Producto

from . import webpay
from .models import ItemCarrito, Orden
from .views import _ordenes_visibles


@login_required
@require_POST
def iniciar_pago(request, pk):
    # Solo el dueño paga su orden (ni siquiera el administrador paga las ajenas).
    orden = get_object_or_404(Orden, pk=pk, user=request.user)
    if orden.estado != Orden.PENDIENTE:
        messages.error(request, 'Esta orden ya fue procesada.')
        return redirect('orden_detalle', pk=orden.pk)
    return_url = request.build_absolute_uri(reverse('webpay_retorno'))
    try:
        respuesta = webpay.crear_transaccion(orden, return_url)
    except Exception:
        messages.error(request, 'No pudimos conectar con Webpay. Intenta nuevamente.')
        return redirect('orden_detalle', pk=orden.pk)
    orden.token_webpay = respuesta['token']
    orden.save(update_fields=['token_webpay'])
    return render(request, 'carrito/pago_redireccion.html', {
        'url': respuesta['url'],
        'token': respuesta['token'],
    })


@csrf_exempt  # Transbank no puede enviar nuestro token CSRF; la autenticidad se valida con commit
def retorno(request):
    datos = request.POST if request.method == 'POST' else request.GET
    token = datos.get('token_ws')

    # Pago anulado, tiempo agotado o error en el formulario: no se confirma.
    if 'TBK_TOKEN' in datos or not token:
        orden = Orden.objects.filter(
            buy_order=datos.get('TBK_ORDEN_COMPRA', ''), estado=Orden.PENDIENTE
        ).first()
        if orden is None:
            return redirect('inicio')
        orden.estado = Orden.RECHAZADA
        orden.save(update_fields=['estado'])
        return redirect('pago_resultado', pk=orden.pk)

    orden = Orden.objects.filter(token_webpay=token).first()
    if orden is None:
        messages.error(request, 'Transacción desconocida.')
        return redirect('inicio')
    if orden.estado != Orden.PENDIENTE:
        return redirect('pago_resultado', pk=orden.pk)

    try:
        resp = webpay.confirmar(token)
    except Exception:
        messages.error(request, 'No pudimos confirmar el pago con Webpay.')
        return redirect('pago_resultado', pk=orden.pk)

    aprobado = (
        resp.get('status') == 'AUTHORIZED'
        and resp.get('response_code') == 0
        and resp.get('buy_order') == orden.buy_order
        and resp.get('amount') == orden.total
    )
    with transaction.atomic():
        orden = Orden.objects.select_for_update().get(pk=orden.pk)
        if orden.estado == Orden.PENDIENTE:
            if aprobado:
                orden.estado = Orden.PAGADA
                orden.codigo_autorizacion = str(resp.get('authorization_code', ''))[:20]
                orden.save(update_fields=['estado', 'codigo_autorizacion'])
                for d in orden.detalles.exclude(producto__isnull=True):
                    Producto.objects.filter(pk=d.producto_id).update(
                        stock=Greatest(F('stock') - d.cantidad, 0)
                    )
                ItemCarrito.objects.filter(carrito__user=orden.user).delete()
            else:
                orden.estado = Orden.RECHAZADA
                orden.save(update_fields=['estado'])
    return redirect('pago_resultado', pk=orden.pk)


@login_required
def resultado(request, pk):
    orden = get_object_or_404(_ordenes_visibles(request.user), pk=pk)
    return render(request, 'carrito/pago_resultado.html', {'orden': orden})
