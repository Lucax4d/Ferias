from django.urls import path

from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('puestos/', views.puesto_lista, name='puesto_lista'),
    path('puestos/nuevo/', views.puesto_crear, name='puesto_crear'),
    path('puestos/<int:pk>/editar/', views.puesto_editar, name='puesto_editar'),
    path('puestos/<int:pk>/eliminar/', views.puesto_eliminar, name='puesto_eliminar'),
    path('productos/', views.producto_lista, name='producto_lista'),
    path('productos/nuevo/', views.producto_crear, name='producto_crear'),
    path('productos/<int:pk>/editar/', views.producto_editar, name='producto_editar'),
    path('productos/<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),
]
