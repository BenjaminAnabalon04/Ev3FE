from django.shortcuts import render

from apps.catalogo.models import Libro


def inicio(request):
    libros_destacados = list(
        Libro.objects.filter(
            activo=True,
            destacado=True,
            genero__activo=True,
        )
        .select_related("genero")
        .order_by("-fecha_creacion")[:3]
    )

    return render(
        request,
        "core/inicio.html",
        {"libros_destacados": libros_destacados},
    )
