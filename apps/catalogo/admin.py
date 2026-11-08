from django.contrib import admin

from .models import GeneroLiterario, Libro


admin.site.site_header = "Librería El Faro - Panel de Administración"
admin.site.site_title = "Librería El Faro Admin"
admin.site.index_title = "Gestión del Catálogo e Inventario"

@admin.register(GeneroLiterario)
class GeneroLiterarioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug", "activo", "creado_en")
    list_filter = ("activo",)
    search_fields = ("nombre", "descripcion")
    prepopulated_fields = {"slug": ("nombre",)}
    list_editable = ("activo",)
    
@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ("codigo","titulo","genero","precio","stock","estado","activo",)
    list_filter = ("genero", "estado", "activo", "destacado")
    search_fields = ("codigo", "titulo", "autor", "editorial", "sinopsis")
    list_editable = ("precio", "stock", "estado", "activo")
    prepopulated_fields = {"slug": ("titulo",)}
    list_per_page = 15