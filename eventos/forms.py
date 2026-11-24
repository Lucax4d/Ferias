from django import forms

from .models import Evento


class EventoForm(forms.ModelForm):
    fecha = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Evento
        fields = ('nombre', 'descripcion', 'fecha', 'ubicacion')
