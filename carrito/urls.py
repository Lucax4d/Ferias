from django.urls import path

from . import pagos, views

urlpatterns = [
    path('', views.ver_carrito, name='ver_carrito'),
    path('agregar/<int:producto_id>/', views.agregar, name='agregar_al_carrito'),
    path('mas/<int:item_id>/', views.incrementar_item, name='incrementar_item'),
    path('menos/<int:item_id>/', views.disminuir_item, name='disminuir_item'),
    path('quitar/<int:item_id>/', views.quitar, name='quitar_del_carrito'),
    path('ordenar/', views.crear_orden, name='crear_orden'),
    path('ordenes/', views.orden_lista, name='orden_lista'),
    path('ordenes/<int:pk>/', views.orden_detalle, name='orden_detalle'),
    path('pago/<int:pk>/iniciar/', pagos.iniciar_pago, name='iniciar_pago'),
    path('pago/retorno/', pagos.retorno, name='webpay_retorno'),
    path('pago/<int:pk>/resultado/', pagos.resultado, name='pago_resultado'),
]
