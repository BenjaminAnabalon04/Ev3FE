from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import LoginForm, RegistroForm

User = get_user_model()


def registro_view(request):
    if request.user.is_authenticated:
        return redirect("core:inicio")

    form = RegistroForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tu cuenta fue creada correctamente.")
        return redirect("usuarios:login")

    return render(request, "usuarios/registro.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:inicio")

    form = LoginForm(request.POST or None)
    next_url = request.POST.get("next") or request.GET.get("next")

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"].strip().lower()
        password = form.cleaned_data["password"]
        usuario = (
            User.objects.filter(email__iexact=email)
            .only("username")
            .first()
        )

        user = None
        if usuario is not None:
            user = authenticate(
                request,
                username=usuario.username,
                password=password,
            )

        if user is not None:
            login(request, user)

            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)

            # Cuando exista la URL del catálogo, puedes cambiarlo por
            # "catalogo:lista".
            return redirect("core:inicio")

        messages.error(request, "Correo o contraseña incorrectos.")

    return render(
        request,
        "usuarios/login.html",
        {
            "form": form,
            "next": next_url or "",
        },
    )


@require_POST
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect("core:inicio")