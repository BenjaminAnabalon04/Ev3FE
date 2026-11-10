# Librería Universo Parral

Sistema web de catálogo y reserva de libros desarrollado con Django, para una librería independiente con venta online, reserva de ejemplares, retiro en tienda y despacho a todo Chile.

---

## Ficha de registro

**Nombre de la Organización:** Librería Universo Parral

**Modelo de Negocio / Giro:** Librería independiente con catálogo online y venta de libros.

**Integrantes del Equipo:** Benjamín Anabalón (21.715.412-K)

**Entidad de Contexto / Agrupación (ORM):** GeneroLiterario

**Entidad Principal Gestionable (ORM):** Libros

**Propósito de la Sesión (request.session):** Lista de reserva de ejemplares con validación de stock, cálculo de subtotal, IVA 19%, costo de envío y comprobante simulado.

---



## Instalación y ejecución

Los comandos son para Windows (PowerShell), desde la carpeta del proyecto.

1. **Crear y activar el entorno virtual**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. **Instalar dependencias**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Aplicar migraciones**
   ```powershell
   python manage.py migrate
   ```

4. **Poblar la base de datos con datos de ejemplo**
   ```powershell
   python manage.py poblar_datos
   ```

5. **Iniciar el servidor**
   ```powershell
   python manage.py runserver 
   ```



---

## Credenciales de prueba

| Rol | Email| Clave | Acceso |
|---|---|---|---|
| Administrador | `admin@libreriauniverso.cl` | `Admin12345!` | http://127.0.0.1:8000/admin/ |
| Cliente | `cliente@libreriauniverso.cl` | `Cliente12345!` | Sitio público |



---



# Bitácora de Prompts (uso técnico y ético de IA)

**Herramienta(s) utilizada(s):** (COMPLETAR: ej. ChatGPT, Claude, Gemini, Copilot)

**Criterio de uso:** La IA se utilizó como apoyo técnico. Cada sugerencia fue revisada, adaptada a los requisitos del proyecto y probada antes de incorporarla.

| Caso | Tema | Estado |
|---|---|---|
| 1 | Registro y login con validaciones | Completado |

## Caso 1: Registro y login con validaciones

### Prompt utilizado

> Necesito hacer un sistema de registro y login. Ya tengo los templates y el modelo de datos listo.
>
> Registro:
> - Las contraseñas deben quedar protegidas por hash.
> - Validaciones de datos ingresados:
>   1. Email: correo ya registrado y correo con formato incorrecto.
>   2. RUT: formato incorrecto. Formato correcto: 11.111.111-K

### Respuesta técnica

La IA propuso:

Código completo propuesto por la IA (versión original, antes de mis adaptaciones):

**`apps/usuarios/forms.py`**

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

**`apps/usuarios/views.py`**

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

### Adaptación aplicada

- Cambié `required=False` por `required=True` en teléfono, comuna y dirección, porque el requisito del sistema exige esos datos en el registro.
- Cambié el formato del RUT de `11.111.111-K` a `11111111-K` (sin puntos), para que sea más cómodo de escribir para un usuario nuevo.
### Verificación

1. Dejé teléfono, comuna y dirección en blanco: el formulario muestra error.
2. Usé un correo y un usuario ya registrados: el formulario muestra error.
3. Probé formatos de RUT incorrectos: el formulario muestra error.



## Caso 2: Catálogo 

### Prompt utilizado

> Quiero hacer el catálogo de mi página. M
>
> Para ello necesito:
>
> - Usar tarjetas de Bootstrap (Cards) que muestren la portada, título, autor, precio, estado y un botón que abrirá la página del libro (todavía no la hago, así que no redirecciones).
> - Buscador multicampo con objeto Q que busque simultáneamente entre el título, código, descripción o autor de un libro.
> - Un filtro entre los géneros que existen.
> - Que el usuario pueda ordenar la lista por título (A-Z) (Z-A) o por precio (menor a mayor) (mayor a menor).
> - Paginación con Paginator, 12 libros por página.

### Respuesta técnica

La IA propuso:



**`apps/catalogo/views.py`**

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

**`templates/catalogo/lista.html`**

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

### Adaptación aplicada

- Agregue un enlace para cuando no se encuentren resultados de un libro. Para que sea mas comodo para el usuario y no tenga la sensacion de quedarse encerrado en la pagina


### Verificación

1. Busqué por título, código, autor y descripción: el catálogo devuelve los libros correctos.
2. Filtré por género: solo aparecen libros de ese género.
3. Probé cada opción de orden (título A-Z y Z-A, precio ascendente y descendente, más recientes): la lista se ordena correctamente.
6. Un libro inactivo no aparece en el catálogo.
7. Una búsqueda sin coincidencias muestra el mensaje con el enlace para ver todo el catálogo.
8. el catalogo abre perfectamente sin havber iniciado sesion.