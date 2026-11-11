from django.urls import path

from . import views

app_name = "catalogo"

urlpatterns = [
    path("", views.lista_libros, name="lista"),
    path("gestion/libros/nuevo/", views.crear_libro, name="crear_libro"),
    path(
        "gestion/libros/<slug:slug>/editar/",
        views.editar_libro,
        name="editar_libro",
    ),
    path(
        "gestion/libros/<slug:slug>/desactivar/",
        views.desactivar_libro,
        name="desactivar_libro",
    ),
    path("gestion/generos/", views.lista_generos, name="lista_generos"),
    path("gestion/generos/nuevo/", views.crear_genero, name="crear_genero"),
    path(
        "gestion/generos/<int:pk>/editar/",
        views.editar_genero,
        name="editar_genero",
    ),
    path("<slug:slug>/", views.detalle_libro, name="detalle"),
]