from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import GeneroLiterario, Libro

# valor que recibe el select -> (campo real de orden, etiqueta visible)
ORDENES = {
    "titulo_asc": ("titulo", "Título (A-Z)"),
    "titulo_desc": ("-titulo", "Título (Z-A)"),
    "precio_asc": ("precio", "Precio (menor a mayor)"),
    "precio_desc": ("-precio", "Precio (mayor a menor)"),
}

ORDEN_POR_DEFECTO = "titulo_asc"


def lista_libros(request):
    busqueda = request.GET.get("q", "").strip()
    genero_slug = request.GET.get("genero", "").strip()
    orden = request.GET.get("orden", ORDEN_POR_DEFECTO)

    # Evita que se pueda ordenar por un campo arbitrario desde la URL.
    if orden not in ORDENES:
        orden = ORDEN_POR_DEFECTO

    libros = (
        Libro.objects.filter(activo=True)
        .select_related("genero")
    )

    # Buscador multicampo.
    # En tu modelo "descripcion" corresponde al campo "sinopsis".
    if busqueda:
        libros = libros.filter(
            Q(titulo__icontains=busqueda)
            | Q(codigo__icontains=busqueda)
            | Q(sinopsis__icontains=busqueda)
            | Q(autor__icontains=busqueda)
        )

    # Filtro por género.
    if genero_slug:
        libros = libros.filter(genero__slug=genero_slug)

    # Ordenamiento.
    campo_orden = ORDENES[orden][0]
    libros = libros.order_by(campo_orden)

    # Paginación: 12 libros por página.
    paginador = Paginator(libros, 12)
    page_obj = paginador.get_page(request.GET.get("page"))

    generos = GeneroLiterario.objects.filter(activo=True)

    contexto = {
        "page_obj": page_obj,
        "generos": generos,
        "busqueda": busqueda,
        "genero_actual": genero_slug,
        "orden_actual": orden,
        "ordenes": [
            (clave, etiqueta)
            for clave, (_, etiqueta) in ORDENES.items()
        ],
    }

    return render(request, "catalogo/lista.html", contexto)

def detalle_libro(request, slug):
    libro = get_object_or_404(
        Libro.objects.select_related("genero"),
        slug=slug,
        activo=True,
    )

    libros_relacionados = (
        Libro.objects.filter(
            activo=True,
            genero=libro.genero,
        )
        .exclude(pk=libro.pk)
        .select_related("genero")
        .order_by("-destacado", "-fecha_creacion")[:5]
    )

    return render(
        request,
        "catalogo/detalle.html",
        {
            "libro": libro,
            "libros_relacionados": libros_relacionados,
        },
    )