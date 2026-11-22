from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import RegistroForm


def registro(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cuenta creada. ¡Bienvenido!')
            return redirect('inicio')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})


def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    siguiente = request.POST.get('next') or request.GET.get('next') or ''
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if siguiente and url_has_allowed_host_and_scheme(
                siguiente, allowed_hosts={request.get_host()}
            ):
                return redirect(siguiente)
            return redirect('inicio')
    else:
        form = AuthenticationForm(request)
    return render(request, 'usuarios/login.html', {'form': form, 'next': siguiente})


@require_POST
def cerrar_sesion(request):
    logout(request)
    messages.info(request, 'Sesión cerrada.')
    return redirect('login')