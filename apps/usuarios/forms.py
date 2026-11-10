import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import PerfilUsuario

User = get_user_model()

# Acepta RUT de 7 u 8 dígitos: 1.234.567-8 o 11.111.111-K
RUT_REGEX = re.compile(r"^[0-9]{7,8}-[0-9K]$")


class RegistroForm(UserCreationForm):
    rut = forms.CharField(
        max_length=12,
        label="RUT",
        help_text="Formato: 11111111-K",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "11111111-K",
                "autocomplete": "off",
            }
        ),
    )

    telefono = forms.CharField(
        max_length=20,
        required=True,
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
        required=True,
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
        required=True,
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
                "Formato de RUT inválido. Usa el formato 11111111-K."
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
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "tu@correo.cl",
                "autocomplete": "email",
                "inputmode": "email",
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