def carrito_context(request):
    carrito = request.session.get("carrito", {})
    total_items = 0

    if isinstance(carrito, dict):
        for cantidad in carrito.values():
            try:
                total_items += int(cantidad)
            except (TypeError, ValueError):
                continue

    return {"carrito_total_items": total_items}
