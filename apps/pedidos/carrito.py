from decimal import ROUND_HALF_UP, Decimal

from apps.catalogo.models import Libro

CARRITO_SESION = "carrito"
ENVIO_SESION = "envio_reserva"

ENVIO_RETIRO = "retiro"
ENVIO_DESPACHO = "despacho"

COSTOS_ENVIO = {
    ENVIO_RETIRO: Decimal("0"),
    ENVIO_DESPACHO: Decimal("4000"),
}

IVA = Decimal("0.19")


def obtener_carrito(request):
    carrito = request.session.get(CARRITO_SESION, {})
    if not isinstance(carrito, dict):
        return {}

    limpio = {}
    for libro_id, cantidad in carrito.items():
        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            continue

        if cantidad > 0:
            limpio[str(libro_id)] = cantidad

    return limpio


def guardar_carrito(request, carrito):
    request.session[CARRITO_SESION] = carrito
    request.session.modified = True


def obtener_envio(request):
    envio = request.session.get(ENVIO_SESION, ENVIO_RETIRO)
    return envio if envio in COSTOS_ENVIO else ENVIO_RETIRO


def guardar_envio(request, envio):
    request.session[ENVIO_SESION] = (
        envio if envio in COSTOS_ENVIO else ENVIO_RETIRO
    )
    request.session.modified = True


def formato_clp(valor):
    return f"${valor:,.0f}".replace(",", ".")


def obtener_items(carrito):
    ids = []
    for libro_id in carrito:
        try:
            ids.append(int(libro_id))
        except (TypeError, ValueError):
            continue

    libros = (
        Libro.objects.filter(pk__in=ids, activo=True)
        .select_related("genero")
        .order_by("titulo")
    )

    items = []
    for libro in libros:
        cantidad = min(carrito.get(str(libro.pk), 0), libro.stock)

        if cantidad <= 0:
            continue

        subtotal = libro.precio * cantidad
        items.append(
            {
                "libro": libro,
                "cantidad": cantidad,
                "subtotal": subtotal,
                "subtotal_fmt": formato_clp(subtotal),
            }
        )

    return items


def calcular_totales(items, tipo_envio):
    subtotal = sum((item["subtotal"] for item in items), Decimal("0"))
    iva = (subtotal * IVA).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    envio = COSTOS_ENVIO.get(tipo_envio, Decimal("0"))
    total = subtotal + iva + envio

    return {
        "subtotal": subtotal,
        "subtotal_fmt": formato_clp(subtotal),
        "iva": iva,
        "iva_fmt": formato_clp(iva),
        "envio": envio,
        "envio_fmt": formato_clp(envio),
        "total": total,
        "total_fmt": formato_clp(total),
    }
