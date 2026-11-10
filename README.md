# Librería Universo Parral

Sistema web de catálogo y reserva de libros desarrollado con Django, para una librería independiente con venta online, reserva de ejemplares, retiro en tienda y despacho a todo Chile.

---

## Ficha de registro

**Nombre de la Organización:** Librería Universo Parral

**Modelo de Negocio / Giro:** Librería independiente con catálogo online, venta de libros, reserva de ejemplares, retiro en tienda y despacho a todo Chile.

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
