from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.usuarios.models import PerfilUsuario

from .forms import GeneroForm, LibroForm
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
        "es_administrador": es_administrador(request.user),
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
            "es_administrador": es_administrador(request.user),
        },
    )


def es_administrador(user):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    perfil = getattr(user, "perfil", None)
    return perfil is not None and perfil.rol == PerfilUsuario.Rol.ADMINISTRADOR


def puede_gestionar(user):
    return user.is_staff and es_administrador(user)


@login_required
@user_passes_test(puede_gestionar)
def crear_libro(request):
    form = LibroForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        libro = form.save()
        messages.success(
            request,
            f'El libro "{libro.titulo}" fue creado correctamente.',
        )

        if libro.activo:
            return redirect("catalogo:detalle", slug=libro.slug)

        return redirect("catalogo:lista")

    return render(
        request,
        "catalogo/gestion/libro_form.html",
        {"form": form},
    )


@login_required
@user_passes_test(puede_gestionar)
def crear_genero(request):
    form = GeneroForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        genero = form.save()
        messages.success(
            request,
            f'El género "{genero.nombre}" fue creado correctamente.',
        )
        return redirect("catalogo:lista")

    return render(
        request,
        "catalogo/gestion/genero_form.html",
        {"form": form},
    )


@login_required
@user_passes_test(puede_gestionar)
def editar_libro(request, slug):
    libro = get_object_or_404(Libro, slug=slug)
    form = LibroForm(
        request.POST or None,
        request.FILES or None,
        instance=libro,
    )

    if request.method == "POST" and form.is_valid():
        libro = form.save()
        messages.success(
            request,
            f'El libro "{libro.titulo}" fue actualizado correctamente.',
        )

        if libro.activo:
            return redirect("catalogo:detalle", slug=libro.slug)

        return redirect("catalogo:lista")

    return render(
        request,
        "catalogo/gestion/libro_form.html",
        {
            "form": form,
            "libro": libro,
        },
    )


@login_required
@user_passes_test(puede_gestionar)
def desactivar_libro(request, slug):
    libro = get_object_or_404(Libro, slug=slug)

    if request.method == "POST":
        libro.activo = False
        libro.save(update_fields=["activo", "fecha_actualizacion"])
        messages.success(
            request,
            f'El libro "{libro.titulo}" fue dado de baja del catálogo.',
        )
        return redirect("catalogo:lista")

    return render(
        request,
        "catalogo/gestion/libro_confirmar_baja.html",
        {"libro": libro},
    )


@login_required
@user_passes_test(puede_gestionar)
def lista_generos(request):
    generos = (
        GeneroLiterario.objects.annotate(libros_count=Count("libros"))
        .order_by("nombre")
    )

    return render(
        request,
        "catalogo/gestion/genero_lista.html",
        {"generos": generos},
    )


@login_required
@user_passes_test(puede_gestionar)
def editar_genero(request, pk):
    genero = get_object_or_404(GeneroLiterario, pk=pk)
    form = GeneroForm(request.POST or None, instance=genero)

    if request.method == "POST" and form.is_valid():
        genero = form.save()
        messages.success(
            request,
            f'El género "{genero.nombre}" fue actualizado correctamente.',
        )
        return redirect("catalogo:lista_generos")

    return render(
        request,
        "catalogo/gestion/genero_form.html",
        {
            "form": form,
            "genero": genero,
        },
    )