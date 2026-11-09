from django.shortcuts import render


def login_view(request):
    """Muestra la interfaz de inicio de sesión.

    La autenticación y las validaciones se implementarán en la siguiente etapa.
    """
    return render(request, "usuarios/login.html")


def registro_view(request):
    """Muestra la interfaz de registro.

    La creación del usuario y las validaciones se implementarán en la siguiente etapa.
    """
    return render(request, "usuarios/registro.html")
