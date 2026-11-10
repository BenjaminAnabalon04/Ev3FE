from django.conf import settings
from django.db import models


class PerfilUsuario(models.Model):

    class Rol(models.TextChoices):
        CLIENTE = "cliente", "Cliente"
        VENDEDOR = "vendedor", "Vendedor / Bibliotecario"
        ADMINISTRADOR = "administrador", "Administrador"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
        verbose_name="Usuario",
    )
    rut = models.CharField(
        max_length=12,
        unique=True,
        verbose_name="RUT",
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono",
    )
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.CLIENTE,
        verbose_name="Rol",
    )
    comuna = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Comuna",
    )
    direccion = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Dirección",
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuarios"

    def __str__(self):
        return f"{self.user.get_username()} - {self.get_rol_display()}"