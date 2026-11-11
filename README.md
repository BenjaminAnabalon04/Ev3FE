<p align="center">
  <img src="static/images/logo.png" alt="Logo de Librería Universo Parral" width="220">
</p>

<h1 align="center">Librería Universo Parral</h1>

<p align="center">
  <em>Tradición y cultura desde 1928</em><br>
  Catálogo online y reserva de libros para una librería independiente de Parral, Chile.
</p>




## Descripción

Sistema web de catálogo y reserva de libros desarrollado con Django, para una librería independiente con venta online, reserva de ejemplares, retiro en tienda y despacho a todo Chile.

Las personas pueden explorar el catálogo, ver el detalle de cada libro y armar una lista de reserva que se guarda en la sesión del navegador, con validación de stock, IVA de 19 %, costo de envío y un comprobante simulado. El personal autorizado administra libros y géneros desde un panel protegido y desde el administrador de Django.



## Ficha de registro

| Campo | Detalle |
|---|---|
| **Nombre de la Organización** | Librería Universo Parral |
| **Modelo de Negocio / Giro** | Librería independiente con catálogo online y venta de libros. |
| **Integrantes del Equipo** | Benjamín Anabalón (21.715.412-K) |
| **Entidad de Contexto / Agrupación (ORM)** | `GeneroLiterario` |
| **Entidad Principal Gestionable (ORM)** | `Libro` |
| **Propósito de la Sesión (`request.session`)** | Lista de reserva de ejemplares con validación de stock, cálculo de subtotal, IVA 19%, costo de envío y comprobante simulado. |

---

## Funcionalidades

**Catálogo público**
- Tarjetas de Bootstrap con portada, título, autor, precio y estado.
- Buscador multicampo (título, código, autor y sinopsis) con objetos `Q`.
- Filtro por género y orden por título (A-Z, Z-A) o precio (menor a mayor, mayor a menor).
- Paginación de 12 libros por página.
- Ficha de detalle accesible por *slug*, con libros relacionados del mismo género.

**Reserva en sesión**
- Agregar libros desde el detalle, validando estado y stock.
- Modificar cantidades (0 elimina), eliminar un libro y vaciar la reserva.
- Desglose con subtotal, IVA 19 %, envío (retiro en tienda o despacho) y total en CLP.
- Contador de unidades en el ícono del carrito del menú, en todas las páginas.
- Confirmación con inicio de sesión: descuenta stock y genera un comprobante simulado.

**Cuentas y seguridad**
- Registro con validación de RUT y correo; contraseñas protegidas con hash.
- Inicio de sesión con usuario o correo; cierre de sesión por POST.
- Perfil de usuario con RUT, teléfono, comuna, dirección y rol.
- Protección CSRF en todos los formularios POST.

**Gestión (administradores)**
- Crear y editar libros con portada, dar de baja con pantalla de confirmación (baja lógica).
- Crear y editar géneros literarios.
- Administrador de Django personalizado: títulos corporativos, `list_display`, `list_filter`, `search_fields`, `list_editable` y `fieldsets`.

---

## Tecnologías

| Componente | Uso |
|---|---|
| Python 3.12+ y Django 6.1.3 | Framework back end |
| SQLite | Base de datos de desarrollo |
| Bootstrap 5 (local) | Interfaz responsiva |
| Pillow | Portadas de los libros (`ImageField`) |
| django-environ / python-dotenv | Variables de entorno |

---


---

## Instalación y ejecución

Requisito: **Python 3.12 o superior**. Los comandos son para Windows (PowerShell), desde la carpeta del proyecto.

1. **Crear y activar el entorno virtual**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. **Instalar dependencias**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Configurar las variables de entorno**
   ```powershell
   Copy-Item .env.example .env
   ```
   Abre el archivo `.env` y reemplaza `SECRET_KEY` por una clave propia. Puedes generar una con:
   ```powershell
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   El archivo `.env` está en `.gitignore` y no se sube al repositorio.

4. **Aplicar migraciones**
   ```powershell
   python manage.py migrate
   ```

5. **Poblar la base de datos con datos de ejemplo** (4 géneros, 8 libros y 2 usuarios de prueba)
   ```powershell
   python manage.py poblar_datos
   ```

6. **Iniciar el servidor**
   ```powershell
   python manage.py runserver
   ```
   El sitio queda disponible en http://127.0.0.1:8000/

---

## Credenciales de prueba


| Rol | Email | Clave | Acceso |
|---|---|---|---|
| Administrador | `admin@libreriauniverso.cl` | `Admin12345!` | http://127.0.0.1:8000/admin/ |
| Cliente | `cliente@libreriauniverso.cl` | `Cliente12345!` | Sitio público |


> Para ingresar al panel de Django (`/admin/`) se usa el usuario `admin`, no el correo. En el sitio público (`/login/`) se puede usar usuario o correo.
> Estas credenciales son solo para pruebas locales.

---




---


## Bitácora de Prompts

Uso técnico y ético de inteligencia artificial.


**Herramienta(s) utilizada(s):** ChatGPT y OpenCode (agente de IA en el editor)

**Criterio de uso:** La IA se utilizó como apoyo técnico. Cada sugerencia fue revisada, adaptada a los requisitos del proyecto y probada antes de incorporarla.

| Caso | Tema |
|---|---|---|
| 1 | Registro y login con validaciones | 
| 2 | Catálogo público con búsqueda, filtros y paginación | 
| 3 | Reserva en sesión con IVA, envío y comprobante |

### Caso 1: Registro y login con validaciones

#### Prompt utilizado

> Necesito hacer un sistema de registro y login. Ya tengo los templates y el modelo de datos listo.
>
> Registro:
> - Las contraseñas deben quedar protegidas por hash.
> - Validaciones de datos ingresados:
>   1. Email: correo ya registrado y correo con formato incorrecto.
>   2. RUT: formato incorrecto. Formato correcto: 11.111.111-K

#### Respuesta técnica

La IA propuso:

Código completo propuesto por la IA (versión original, antes de mis adaptaciones):

<details>
<summary><code>apps/usuarios/forms.py</code></summary>

```python
import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import PerfilUsuario

User = get_user_model()

# Acepta RUT de 7 u 8 dígitos: 1.234.567-8 o 11.111.111-K
RUT_REGEX = re.compile(r"^[0-9]{1,2}\.[0-9]{3}\.[0-9]{3}-[0-9K]$")


class RegistroForm(UserCreationForm):
    rut = forms.CharField(
        max_length=12,
        label="RUT",
        help_text="Formato: 11.111.111-K",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "11.111.111-K",
                "autocomplete": "off",
            }
        ),
    )

    telefono = forms.CharField(
        max_length=20,
        required=False,
        label="Teléfono",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "+56 9 1234 5678",
                "autocomplete": "tel",
            }
        ),
    )

    comuna = forms.CharField(
        max_length=100,
        required=False,
        label="Comuna",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Parral",
                "autocomplete": "address-level2",
            }
        ),
    )

    direccion = forms.CharField(
        max_length=200,
        required=False,
        label="Dirección",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Calle y número",
                "autocomplete": "street-address",
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")
        labels = {
            "username": "Nombre de usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["email"].required = True

        for campo in self.fields.values():
            campo.widget.attrs.setdefault("class", "form-control")

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()

        if not email:
            raise ValidationError("El correo electrónico es obligatorio.")

        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Ya existe una cuenta registrada con este correo.")

        return email

    def clean_rut(self):
        rut = self.cleaned_data.get("rut", "").strip().upper()

        if not RUT_REGEX.fullmatch(rut):
            raise ValidationError(
                "Formato de RUT inválido. Usa el formato 11.111.111-K."
            )

        if PerfilUsuario.objects.filter(rut__iexact=rut).exists():
            raise ValidationError("Ya existe una cuenta registrada con este RUT.")

        return rut

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

            PerfilUsuario.objects.create(
                user=user,
                rut=self.cleaned_data["rut"],
                telefono=self.cleaned_data.get("telefono", ""),
                comuna=self.cleaned_data.get("comuna", ""),
                direccion=self.cleaned_data.get("direccion", ""),
            )

        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Usuario o correo electrónico",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "tu@correo.cl o tu usuario",
                "autocomplete": "username",
            }
        ),
    )

    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Tu contraseña",
                "autocomplete": "current-password",
            }
        ),
    )
```

</details>

<details>
<summary><code>apps/usuarios/views.py</code></summary>

```python
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import LoginForm, RegistroForm

User = get_user_model()


def registro_view(request):
    if request.user.is_authenticated:
        return redirect("core:inicio")

    form = RegistroForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tu cuenta fue creada correctamente.")
        return redirect("usuarios:login")

    return render(request, "usuarios/registro.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:inicio")

    form = LoginForm(request.POST or None)
    next_url = request.POST.get("next") or request.GET.get("next")

    if request.method == "POST" and form.is_valid():
        identificador = form.cleaned_data["username"].strip()
        password = form.cleaned_data["password"]

        # El backend por defecto autentica con username.
        # Si el usuario escribió un correo, buscamos su username.
        username = identificador

        if "@" in identificador:
            usuario = (
                User.objects.filter(email__iexact=identificador)
                .only("username")
                .first()
            )
            if usuario:
                username = usuario.username

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(
                request,
                f"Bienvenido, {user.first_name or user.username}.",
            )

            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)

            # Cuando exista la URL del catálogo, puedes cambiarlo por
            # "catalogo:lista".
            return redirect("core:inicio")

        messages.error(request, "Usuario/correo o contraseña incorrectos.")

    return render(
        request,
        "usuarios/login.html",
        {
            "form": form,
            "next": next_url or "",
        },
    )


@require_POST
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect("core:inicio")
```

</details>

#### Adaptación aplicada

- Cambié `required=False` por `required=True` en teléfono, comuna y dirección, porque el requisito del sistema exige esos datos en el registro.
- Cambié el formato del RUT de `11.111.111-K` a `11111111-K` (sin puntos), para que sea más cómodo de escribir para un usuario nuevo.

#### Verificación

1. Dejé teléfono, comuna y dirección en blanco: el formulario muestra error.
2. Usé un correo y un usuario ya registrados: el formulario muestra error.
3. Probé formatos de RUT incorrectos: el formulario muestra error.

---

### Caso 2: Catálogo

#### Prompt utilizado

> Quiero hacer el catálogo de mi página. M
>
> Para ello necesito:
>
> - Usar tarjetas de Bootstrap (Cards) que muestren la portada, título, autor, precio, estado y un botón que abrirá la página del libro (todavía no la hago, así que no redirecciones).
> - Buscador multicampo con objeto Q que busque simultáneamente entre el título, código, descripción o autor de un libro.
> - Un filtro entre los géneros que existen.
> - Que el usuario pueda ordenar la lista por título (A-Z) (Z-A) o por precio (menor a mayor) (mayor a menor).
> - Paginación con Paginator, 12 libros por página.

#### Respuesta técnica

La IA propuso:

<details>
<summary><code>apps/catalogo/views.py</code></summary>

```python
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

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
```

</details>

<details>
<summary><code>templates/catalogo/lista.html</code></summary>

```html
{% extends "base.html" %}

{% block title %}Catálogo | Librería Universo{% endblock %}
{% block description %}Explora los libros disponibles en Librería Universo, Parral.{% endblock %}

{% block content %}
<section class="section">
    <div class="container">
        <div class="section-heading">
            <span class="eyebrow">Catálogo</span>
            <h1>Nuestros libros</h1>
            <p>Busca por título, código, autor o descripción, y filtra por género.</p>
        </div>

        <form method="get" action="{% url 'catalogo:lista' %}" class="catalog-filters row g-3 align-items-end mb-4">
            <div class="col-lg-5">
                <label for="id_q" class="form-label">Buscar</label>
                <input
                    type="search"
                    class="form-control"
                    id="id_q"
                    name="q"
                    value="{{ busqueda }}"
                    placeholder="Título, código, autor o descripción"
                >
            </div>

            <div class="col-sm-6 col-lg-3">
                <label for="id_genero" class="form-label">Género</label>
                <select class="form-select" id="id_genero" name="genero">
                    <option value="">Todos los géneros</option>
                    {% for genero in generos %}
                    <option value="{{ genero.slug }}" {% if genero_actual == genero.slug %}selected{% endif %}>
                        {{ genero.nombre }}
                    </option>
                    {% endfor %}
                </select>
            </div>

            <div class="col-sm-6 col-lg-2">
                <label for="id_orden" class="form-label">Ordenar por</label>
                <select class="form-select" id="id_orden" name="orden">
                    {% for valor, etiqueta in ordenes %}
                    <option value="{{ valor }}" {% if orden_actual == valor %}selected{% endif %}>
                        {{ etiqueta }}
                    </option>
                    {% endfor %}
                </select>
            </div>

            <div class="col-lg-2 d-grid">
                <button type="submit" class="btn btn-brand">Filtrar</button>
            </div>
        </form>

        <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
            <p class="text-muted mb-0">
                {{ page_obj.paginator.count }} libro{{ page_obj.paginator.count|pluralize }}
                encontrado{{ page_obj.paginator.count|pluralize }}
            </p>

            {% if busqueda or genero_actual or orden_actual != "titulo_asc" %}
            <a class="auth-link" href="{% url 'catalogo:lista' %}">Limpiar filtros</a>
            {% endif %}
        </div>

        <div class="row g-4">
            {% for libro in page_obj %}
            <div class="col-sm-6 col-lg-4 col-xl-3">
                <article class="card book-card h-100">
                    {% if libro.portada %}
                    <img
                        class="card-img-top book-cover"
                        src="{{ libro.portada.url }}"
                        alt="Portada de {{ libro.titulo }}"
                    >
                    {% else %}
                    <div class="card-img-top book-cover book-cover-placeholder">
                        <strong>{{ libro.titulo }}</strong>
                        <small>{{ libro.autor }}</small>
                    </div>
                    {% endif %}

                    <div class="card-body book-body d-flex flex-column">
                        <span class="book-genre">{{ libro.genero.nombre }}</span>
                        <h3 class="book-title">{{ libro.titulo }}</h3>
                        <p class="book-author">{{ libro.autor }}</p>

                        <div class="mt-auto">
                            <div class="book-footer">
                                <span class="book-price">{{ libro.precio_formateado }}</span>

                                {% if libro.estado == "disponible" %}
                                <span class="badge text-bg-success">{{ libro.get_estado_display }}</span>
                                {% elif libro.estado == "preventa" %}
                                <span class="badge text-bg-warning">{{ libro.get_estado_display }}</span>
                                {% elif libro.estado == "agotado" %}
                                <span class="badge text-bg-secondary">{{ libro.get_estado_display }}</span>
                                {% else %}
                                <span class="badge text-bg-danger">{{ libro.get_estado_display }}</span>
                                {% endif %}
                            </div>

                            {# Cuando exista la página de detalle, reemplaza este botón por un enlace. #}
                            <button type="button" class="btn btn-brand w-100 mt-3" disabled>
                                Ver libro
                            </button>
                        </div>
                    </div>
                </article>
            </div>
            {% empty %}
            <div class="col-12">
                <p class="text-muted">No encontramos libros con esos filtros.</p>
            </div>
            {% endfor %}
        </div>

        {% if page_obj.has_other_pages %}
        <nav class="mt-4" aria-label="Paginación del catálogo">
            <ul class="pagination justify-content-center flex-wrap">
                <li class="page-item {% if not page_obj.has_previous %}disabled{% endif %}">
                    {% if page_obj.has_previous %}
                    <a class="page-link" href="{% querystring page=page_obj.previous_page_number %}">
                        Anterior
                    </a>
                    {% else %}
                    <span class="page-link">Anterior</span>
                    {% endif %}
                </li>

                {% for numero in page_obj.paginator.page_range %}
                    {% if numero == page_obj.number %}
                    <li class="page-item active" aria-current="page">
                        <span class="page-link">{{ numero }}</span>
                    </li>
                    {% else %}
                    <li class="page-item">
                        <a class="page-link" href="{% querystring page=numero %}">{{ numero }}</a>
                    </li>
                    {% endif %}
                {% endfor %}

                <li class="page-item {% if not page_obj.has_next %}disabled{% endif %}">
                    {% if page_obj.has_next %}
                    <a class="page-link" href="{% querystring page=page_obj.next_page_number %}">
                        Siguiente
                    </a>
                    {% else %}
                    <span class="page-link">Siguiente</span>
                    {% endif %}
                </li>
            </ul>
        </nav>
        {% endif %}
    </div>
</section>
{% endblock %}
```

</details>

#### Adaptación aplicada

- Agregue un enlace para cuando no se encuentren resultados de un libro. Para que sea mas comodo para el usuario y no tenga la sensacion de quedarse encerrado en la pagina

#### Verificación

1. Busqué por título, código, autor y descripción: el catálogo devuelve los libros correctos.
2. Filtré por género: solo aparecen libros de ese género.
3. Probé cada opción de orden (título A-Z y Z-A, precio ascendente y descendente, más recientes): la lista se ordena correctamente.
6. Un libro inactivo no aparece en el catálogo.
7. Una búsqueda sin coincidencias muestra el mensaje con el enlace para ver todo el catálogo.
8. el catalogo abre perfectamente sin havber iniciado sesion.

---

### Caso 3: Reserva en sesión, desglose económico y comprobante

#### Prompt utilizado

```text
Necesito agregar a mi pagina un carrito de compras guardado en request.session .
Quiero:
1.	Crear vista de la reserva, donde se pueda:
- Modificar cantidad de libros
( 1.Minimo 1. Si el cliente pone 0, eliminar de la reserva)
( 2. Que el cliente no pueda reservar mas libros de los que hay en stock)
- Eliminar un item
- Vaciar toda la reserva
-Boton  para confirmar reserva con login_required que
(1. Genere un comprobante de venta simulado, mostrando Fecha emisión, datos del usuario, libros reservados y desglose economico)
(2. Vacie el carrito luego de confirmar reserva)
(3. Descontar stock de libros)
2. Un desglose económico donde:
-muestre el subtotal
-iva aplicado al subtotal
-Envio
1. Retiro en tienda Valor = $0CLP
2. Despacho Valor = $4000CLP
- Final total en pesos chilenos (CLP)
```

#### Respuesta técnica



<details>
<summary><code>apps/pedidos/carrito.py</code></summary>

```python
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
```

</details>

<details>
<summary><code>apps/pedidos/views.py</code></summary>

```python
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
            messages.success(request, "Método de entrega actualizado.")
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
            messages.success(request, "Reserva actualizada.")
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
```

</details>

<details>
<summary><code>apps/pedidos/templates/pedidos/reserva.html</code></summary>

```html
{% extends "base.html" %}

{% block title %}Mi reserva | Librería Universo{% endblock %}
{% block description %}Revisa los libros de tu reserva en Librería Universo.{% endblock %}

{% block content %}
<section class="section">
    <div class="container">
        <div class="d-flex flex-wrap justify-content-between align-items-end gap-3 mb-4">
            <div class="section-heading mb-0">
                <span class="eyebrow">Carrito</span>
                <h1>Mi reserva</h1>
                <p>Ajusta cantidades y elige cómo recibir tus libros.</p>
            </div>

            <a class="btn btn-outline-brand" href="{% url 'catalogo:lista' %}">
                Seguir explorando
            </a>
        </div>

        {% if items %}
        <div class="row g-4">
            <div class="col-lg-8">
                <form method="post" action="{% url 'pedidos:reserva' %}">
                    {% csrf_token %}

                    <div class="admin-table-card">
                        <div class="table-responsive">
                            <table class="table admin-table align-middle mb-0">
                                <thead>
                                    <tr>
                                        <th scope="col">Libro</th>
                                        <th scope="col">Precio</th>
                                        <th scope="col">Cantidad</th>
                                        <th scope="col">Subtotal</th>
                                        <th scope="col" class="text-end">Acciones</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for item in items %}
                                    <tr>
                                        <td>
                                            <strong>{{ item.libro.titulo }}</strong>
                                            <div class="admin-table-description">
                                                {{ item.libro.autor }}
                                            </div>
                                        </td>
                                        <td>{{ item.libro.precio_formateado }}</td>
                                        <td style="min-width: 8rem;">
                                            <input
                                                type="number"
                                                class="form-control form-control-sm"
                                                name="cantidad_{{ item.libro.pk }}"
                                                value="{{ item.cantidad }}"
                                                min="0"
                                                max="{{ item.libro.stock }}"
                                                aria-label="Cantidad de {{ item.libro.titulo }}"
                                            >
                                            <div class="form-text">
                                                Máximo {{ item.libro.stock }}. 0 elimina.
                                            </div>
                                        </td>
                                        <td>{{ item.subtotal_fmt }}</td>
                                        <td class="text-end">
                                            <button
                                                type="submit"
                                                name="eliminar"
                                                value="{{ item.libro.pk }}"
                                                class="btn btn-outline-brand btn-sm"
                                            >
                                                Eliminar
                                            </button>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div class="d-flex flex-wrap gap-2 mt-3">
                        <button type="submit" name="actualizar" value="1" class="btn btn-brand">
                            Actualizar cantidades
                        </button>
                        <button type="submit" name="vaciar" value="1" class="btn btn-outline-brand">
                            Vaciar reserva
                        </button>
                    </div>
                </form>
            </div>

            <div class="col-lg-4">
                <div class="admin-form-card">
                    <h2 class="h5 mb-3">Desglose económico</h2>

                    <dl class="mb-0">
                        <div class="d-flex justify-content-between gap-3">
                            <dt class="fw-normal">Subtotal</dt>
                            <dd class="mb-0">{{ totales.subtotal_fmt }}</dd>
                        </div>
                        <div class="d-flex justify-content-between gap-3">
                            <dt class="fw-normal">IVA (19%)</dt>
                            <dd class="mb-0">{{ totales.iva_fmt }}</dd>
                        </div>
                        <div class="d-flex justify-content-between gap-3">
                            <dt class="fw-normal">Envío</dt>
                            <dd class="mb-0">{{ totales.envio_fmt }}</dd>
                        </div>
                    </dl>

                    <hr>

                    <form method="post" action="{% url 'pedidos:reserva' %}">
                        {% csrf_token %}

                        <fieldset>
                            <legend class="form-label">Método de entrega</legend>

                            <div class="form-check">
                                <input
                                    class="form-check-input"
                                    type="radio"
                                    name="tipo_envio"
                                    id="envio-retiro"
                                    value="retiro"
                                    {% if tipo_envio == "retiro" %}checked{% endif %}
                                >
                                <label class="form-check-label" for="envio-retiro">
                                    Retiro en tienda ($0)
                                </label>
                            </div>

                            <div class="form-check">
                                <input
                                    class="form-check-input"
                                    type="radio"
                                    name="tipo_envio"
                                    id="envio-despacho"
                                    value="despacho"
                                    {% if tipo_envio == "despacho" %}checked{% endif %}
                                >
                                <label class="form-check-label" for="envio-despacho">
                                    Despacho ($4.000)
                                </label>
                            </div>
                        </fieldset>

                        <button type="submit" name="envio" value="1" class="btn btn-outline-brand btn-sm mt-3">
                            Actualizar entrega
                        </button>
                    </form>

                    <hr>

                    <div class="d-flex justify-content-between fw-bold fs-5">
                        <span>Total</span>
                        <span>{{ totales.total_fmt }}</span>
                    </div>

                    <form method="post" action="{% url 'pedidos:confirmar' %}" class="mt-3">
                        {% csrf_token %}
                        <button type="submit" class="btn btn-brand w-100">
                            Confirmar reserva
                        </button>
                    </form>

                    {% if not user.is_authenticated %}
                    <p class="form-text mt-2 mb-0">
                        Al confirmar se te pedirá iniciar sesión.
                    </p>
                    {% endif %}
                </div>
            </div>
        </div>
        {% else %}
        <div class="admin-form-card text-center">
            <h2 class="h4">Tu reserva está vacía</h2>
            <p class="mb-4">Agrega libros desde el catálogo para comenzar.</p>
            <a class="btn btn-brand" href="{% url 'catalogo:lista' %}">
                Ir al catálogo
            </a>
        </div>
        {% endif %}
    </div>
</section>
{% endblock %}
```

</details>

#### Adaptación aplicada

- Creé un context processor para mostrar en el ícono del carrito cuántos libros hay en la reserva.
- Hice que las cantidades y la entrega se actualicen solas.

#### Verificación
- Creé un context processor para mostrar en el ícono del carrito cuántos libros hay en la reserva.
- Hice que las cantidades y la entrega se actualicen solas.
