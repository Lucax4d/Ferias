from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from usuarios.decorators import solo_admin
from usuarios.models import Perfil
from usuarios.roles import rol_de

from .forms import EventoForm
from .models import Asistencia, Evento


def evento_lista(request):
    eventos = Evento.objects.select_related('ubicacion').annotate(
        total=Count('asistencias')
    ).order_by('fecha')
    asistire = set()
    if request.user.is_authenticated:
        asistire = set(
            Asistencia.objects.filter(user=request.user).values_list('evento_id', flat=True)
        )
    return render(request, 'eventos/evento_lista.html', {
        'eventos': eventos,
        'asistire': asistire,
        'es_admin': rol_de(request.user) == Perfil.ADMIN,
    })


@solo_admin
def evento_crear(request):
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento creado.')
            return redirect('evento_lista')
    else:
        form = EventoForm()
    return render(request, 'eventos/evento_form.html', {'form': form, 'titulo': 'Nuevo evento'})


@solo_admin
def evento_editar(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento actualizado.')
            return redirect('evento_lista')
    else:
        form = EventoForm(instance=evento)
    return render(request, 'eventos/evento_form.html', {'form': form, 'titulo': 'Editar evento'})


@solo_admin
def evento_eliminar(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if request.method == 'POST':
        evento.delete()
        messages.success(request, 'Evento eliminado.')
        return redirect('evento_lista')
    return render(request, 'eventos/evento_confirmar_eliminar.html', {'evento': evento})


@login_required
@require_POST
def asistir(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    Asistencia.objects.get_or_create(evento=evento, user=request.user)
    messages.success(request, f'Quedaste inscrito en {evento.nombre}.')
    return redirect('evento_lista')


@login_required
@require_POST
def cancelar_asistencia(request, pk):
    Asistencia.objects.filter(evento_id=pk, user=request.user).delete()
    messages.info(request, 'Cancelaste tu asistencia.')
    return redirect('evento_lista')
