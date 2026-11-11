from django.urls import path

from . import views

app_name = "pedidos"

urlpatterns = [
    path("", views.ver_reserva, name="reserva"),
    path("agregar/<int:libro_id>/", views.agregar_al_carrito, name="agregar"),
    path("confirmar/", views.confirmar_reserva, name="confirmar"),
    path("comprobante/", views.ver_comprobante, name="comprobante"),
]
