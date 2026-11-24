from django import forms
from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.decorators import solo_admin
from usuarios.models import Perfil
from usuarios.roles import rol_de

from .models import Ubicacion


class UbicacionForm(forms.ModelForm):
    class Meta:
        model = Ubicacion
        fields = ('nombre', 'direccion')


def ubicacion_lista(request):
    return render(request, 'feria/ubicacion_lista.html', {
        'ubicaciones': Ubicacion.objects.all(),
        'es_admin': rol_de(request.user) == Perfil.ADMIN,
    })


@solo_admin
def ubicacion_crear(request):
    if request.method == 'POST':
        form = UbicacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ubicación creada.')
            return redirect('ubicacion_lista')
    else:
        form = UbicacionForm()
    return render(request, 'feria/ubicacion_form.html', {'form': form, 'titulo': 'Nueva ubicación'})


@solo_admin
def ubicacion_editar(request, pk):
    ubicacion = get_object_or_404(Ubicacion, pk=pk)
    if request.method == 'POST':
        form = UbicacionForm(request.POST, instance=ubicacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ubicación actualizada.')
            return redirect('ubicacion_lista')
    else:
        form = UbicacionForm(instance=ubicacion)
    return render(request, 'feria/ubicacion_form.html', {'form': form, 'titulo': 'Editar ubicación'})


@solo_admin
def ubicacion_eliminar(request, pk):
    ubicacion = get_object_or_404(Ubicacion, pk=pk)
    if request.method == 'POST':
        try:
            ubicacion.delete()
        except ProtectedError:
            messages.error(request, 'No se puede eliminar: tiene puestos o eventos asociados.')
            return redirect('ubicacion_lista')
        messages.success(request, 'Ubicación eliminada.')
        return redirect('ubicacion_lista')
    return render(request, 'feria/ubicacion_confirmar_eliminar.html', {'ubicacion': ubicacion})
