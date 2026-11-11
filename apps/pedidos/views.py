from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.catalogo.models import Libro

from .carrito import (
    ENVIO_RETIRO,
    calcular_totales,
    formato_clp,
    guardar_carrito,
    guardar_envio,
    obtener_carrito,
    obtener_envio,
    obtener_items,
)


def ver_reserva(request):
    carrito = obtener_carrito(request)

    if request.method == "POST":
        if "vaciar" in request.POST:
            guardar_carrito(request, {})
            messages.success(request, "La reserva fue vaciada.")
            return redirect("pedidos:reserva")

        if "eliminar" in request.POST:
            carrito.pop(request.POST.get("eliminar", ""), None)
            guardar_carrito(request, carrito)
            messages.success(request, "El libro fue eliminado de la reserva.")
            return redirect("pedidos:reserva")

        if "envio" in request.POST:
            guardar_envio(request, request.POST.get("tipo_envio", ENVIO_RETIRO))
            return redirect("pedidos:reserva")

        if "actualizar" in request.POST:
            for libro_id in list(carrito):
                try:
                    libro = Libro.objects.get(pk=libro_id)
                except (Libro.DoesNotExist, ValueError):
                    carrito.pop(libro_id, None)
                    continue

                try:
                    cantidad = int(
                        request.POST.get(
                            f"cantidad_{libro_id}",
                            carrito[libro_id],
                        )
                    )
                except (TypeError, ValueError):
                    cantidad = carrito[libro_id]

                if libro.stock <= 0:
                    carrito.pop(libro_id, None)
                    messages.warning(
                        request,
                        f'"{libro.titulo}" ya no tiene stock.',
                    )
                elif cantidad <= 0:
                    carrito.pop(libro_id, None)
                elif cantidad > libro.stock:
                    carrito[libro_id] = libro.stock
                    messages.warning(
                        request,
                        f'Solo hay {libro.stock} unidades de "{libro.titulo}".',
                    )
                else:
                    carrito[libro_id] = cantidad

            guardar_carrito(request, carrito)
            return redirect("pedidos:reserva")

    items = obtener_items(carrito)
    carrito_sincronizado = {
        str(item["libro"].pk): item["cantidad"] for item in items
    }

    if carrito_sincronizado != carrito:
        guardar_carrito(request, carrito_sincronizado)
        carrito = carrito_sincronizado
        messages.warning(request, "Ajustamos tu reserva al stock disponible.")

    tipo_envio = obtener_envio(request)
    totales = calcular_totales(items, tipo_envio)

    return render(
        request,
        "pedidos/reserva.html",
        {
            "items": items,
            "tipo_envio": tipo_envio,
            "totales": totales,
        },
    )


@require_POST
def agregar_al_carrito(request, libro_id):
    libro = get_object_or_404(Libro, pk=libro_id, activo=True)

    if libro.estado not in (Libro.Estado.DISPONIBLE, Libro.Estado.PREVENTA):
        messages.error(request, f'"{libro.titulo}" no está disponible.')
        return redirect("catalogo:detalle", slug=libro.slug)

    if libro.stock <= 0:
        messages.error(request, f'"{libro.titulo}" no tiene stock.')
        return redirect("catalogo:detalle", slug=libro.slug)

    carrito = obtener_carrito(request)
    cantidad = carrito.get(str(libro.pk), 0)

    if cantidad >= libro.stock:
        messages.warning(
            request,
            f'Ya tienes el máximo disponible de "{libro.titulo}".',
        )
    else:
        carrito[str(libro.pk)] = cantidad + 1
        guardar_carrito(request, carrito)
        messages.success(request, f'"{libro.titulo}" se agregó a tu reserva.')

    return redirect("catalogo:detalle", slug=libro.slug)


@login_required
def confirmar_reserva(request):
    # Si vuelve desde el login con un GET, lo mandamos a la reserva.
    if request.method != "POST":
        return redirect("pedidos:reserva")

    carrito = obtener_carrito(request)

    if not carrito:
        messages.error(request, "Tu reserva está vacía.")
        return redirect("pedidos:reserva")

    tipo_envio = obtener_envio(request)
    error = None

    with transaction.atomic():
        ids = [int(libro_id) for libro_id in carrito]
        libros = {
            str(libro.pk): libro
            for libro in Libro.objects.select_for_update().filter(
                pk__in=ids,
                activo=True,
            )
        }

        for libro_id, cantidad in carrito.items():
            libro = libros.get(libro_id)

            if libro is None:
                error = "Uno de los libros de tu reserva ya no está disponible."
                break

            if cantidad > libro.stock:
                error = (
                    f'Solo quedan {libro.stock} unidades de "{libro.titulo}".'
                )
                break

        if error is None:
            items = [
                {
                    "libro": libro,
                    "cantidad": carrito[libro_id],
                    "subtotal": libro.precio * carrito[libro_id],
                }
                for libro_id, libro in libros.items()
            ]

            totales = calcular_totales(items, tipo_envio)

            detalles = []
            for item in items:
                libro = item["libro"]
                cantidad = item["cantidad"]

                libro.stock -= cantidad
                if libro.stock == 0:
                    libro.estado = Libro.Estado.AGOTADO

                libro.save(
                    update_fields=["stock", "estado", "fecha_actualizacion"]
                )

                detalles.append(
                    {
                        "codigo": libro.codigo,
                        "titulo": libro.titulo,
                        "cantidad": cantidad,
                        "precio_fmt": formato_clp(libro.precio),
                        "subtotal_fmt": formato_clp(item["subtotal"]),
                    }
                )

    if error:
        messages.error(request, error)
        return redirect("pedidos:reserva")

    perfil = getattr(request.user, "perfil", None)

    request.session["comprobante"] = {
        "folio": f"RES-{timezone.now():%Y%m%d%H%M%S}-{request.user.pk}",
        "fecha": timezone.localtime().strftime("%d/%m/%Y %H:%M"),
        "usuario": {
            "nombre": request.user.get_full_name() or request.user.username,
            "email": request.user.email,
            "rut": getattr(perfil, "rut", "") or "",
            "telefono": getattr(perfil, "telefono", "") or "",
            "direccion": getattr(perfil, "direccion", "") or "",
            "comuna": getattr(perfil, "comuna", "") or "",
        },
        "items": detalles,
        "envio_tipo": (
            "Retiro en tienda"
            if tipo_envio == ENVIO_RETIRO
            else "Despacho a domicilio"
        ),
        "subtotal_fmt": totales["subtotal_fmt"],
        "iva_fmt": totales["iva_fmt"],
        "envio_fmt": totales["envio_fmt"],
        "total_fmt": totales["total_fmt"],
    }

    guardar_carrito(request, {})
    guardar_envio(request, ENVIO_RETIRO)
    messages.success(request, "Reserva confirmada. Tu comprobante está listo.")

    return redirect("pedidos:comprobante")


@login_required
def ver_comprobante(request):
    comprobante = request.session.get("comprobante")

    if not comprobante:
        messages.info(request, "No hay un comprobante para mostrar.")
        return redirect("pedidos:reserva")

    return render(
        request,
        "pedidos/comprobante.html",
        {"comprobante": comprobante},
    )
