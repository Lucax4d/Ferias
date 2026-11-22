from django.urls import path

from . import views

urlpatterns = [
    path('', views.ver_carrito, name='ver_carrito'),
    path('agregar/<int:producto_id>/', views.agregar, name='agregar_al_carrito'),
    path('quitar/<int:item_id>/', views.quitar, name='quitar_del_carrito'),
    path('ordenar/', views.crear_orden, name='crear_orden'),
    path('ordenes/', views.orden_lista, name='orden_lista'),
    path('ordenes/<int:pk>/', views.orden_detalle, name='orden_detalle'),
]
