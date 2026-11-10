from django.urls import path

from . import views

app_name = "catalogo"

urlpatterns = [
    path("", views.lista_libros, name="lista"),
    path("<slug:slug>/", views.detalle_libro, name="detalle"),
]