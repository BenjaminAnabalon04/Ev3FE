from django import forms

from .models import GeneroLiterario, Libro


def aplicar_estilos(form):
    """Agrega las clases de Bootstrap a todos los campos del formulario."""
    for campo in form.fields.values():
        widget = campo.widget

        if isinstance(widget, forms.CheckboxInput):
            widget.attrs.setdefault("class", "form-check-input")
        elif isinstance(widget, forms.Select):
            widget.attrs.setdefault("class", "form-select")
        else:
            widget.attrs.setdefault("class", "form-control")


class GeneroForm(forms.ModelForm):
    class Meta:
        model = GeneroLiterario
        fields = ("nombre", "descripcion", "activo")
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_estilos(self)


class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = (
            "codigo",
            "titulo",
            "genero",
            "autor",
            "editorial",
            "anio_publicacion",
            "sinopsis",
            "precio",
            "stock",
            "estado",
            "portada",
            "destacado",
            "activo",
        )
        widgets = {
            "sinopsis": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_estilos(self)
