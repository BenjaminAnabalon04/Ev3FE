from django.shortcuts import render

from apps.catalogo.models import Libro


def inicio(request):
    libros_destacados = list(
        Libro.objects.filter(activo=True, destacado=True)
        .select_related("genero")
        .order_by("-fecha_creacion")[:3]
    )

    if not libros_destacados:
        libros_destacados = list(
            Libro.objects.filter(activo=True)
            .select_related("genero")
            .order_by("-fecha_creacion")[:3]
        )

    return render(
        request,
        "core/inicio.html",
        {"libros_destacados": libros_destacados},
    )
