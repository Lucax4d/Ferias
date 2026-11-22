from django import forms

from .models import Puesto


class PuestoForm(forms.ModelForm):
    class Meta:
        model = Puesto
        fields = ('vendedor', 'ubicacion', 'nombre', 'numero')

    def __init__(self, *args, es_admin=False, **kwargs):
        super().__init__(*args, **kwargs)
        if not es_admin:
            del self.fields['vendedor']