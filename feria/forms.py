from django import forms

from .models import Producto, Puesto
from .permisos import puestos_gestionables


class PuestoForm(forms.ModelForm):
    class Meta:
        model = Puesto
        fields = ('vendedor', 'ubicacion', 'nombre', 'numero')

    def __init__(self, *args, es_admin=False, **kwargs):
        super().__init__(*args, **kwargs)
        if not es_admin:
            del self.fields['vendedor']


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ('puesto', 'nombre', 'descripcion', 'portada', 'precio', 'stock', 'activo')

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['puesto'].queryset = puestos_gestionables(user)
