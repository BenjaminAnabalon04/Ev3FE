from django.contrib import admin

from .models import PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("user", "rut", "telefono", "rol", "comuna")
    list_filter = ("rol", "comuna")
    search_fields = ("user__username", "user__email", "rut", "telefono")