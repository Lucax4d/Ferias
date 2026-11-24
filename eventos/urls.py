from django.urls import path

from . import views

urlpatterns = [
    path('', views.evento_lista, name='evento_lista'),
    path('nuevo/', views.evento_crear, name='evento_crear'),
    path('<int:pk>/editar/', views.evento_editar, name='evento_editar'),
    path('<int:pk>/eliminar/', views.evento_eliminar, name='evento_eliminar'),
    path('<int:pk>/asistir/', views.asistir, name='asistir'),
    path('<int:pk>/cancelar/', views.cancelar_asistencia, name='cancelar_asistencia'),
]
