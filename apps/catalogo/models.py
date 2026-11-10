from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify


class GeneroLiterario(models.Model):
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre del género",
    )
    slug = models.SlugField( # Campo para generar la URL del género
        max_length=120,
        unique=True,
        blank=True,
        verbose_name="Slug",
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="¿Activo?",
    )
    creado_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creado en",
    )

    class Meta:
        verbose_name = "Género literario"
        verbose_name_plural = "Géneros literarios"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.nombre)[:100] or "genero"
            slug = base
            contador = 1
            while (
                GeneroLiterario.objects.filter(slug=slug)
                .exclude(pk=self.pk)
                .exists()
            ):
                slug = f"{base}-{contador}"
                contador += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Libro(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = "disponible", "Disponible"
        AGOTADO = "agotado", "Agotado"
        PREVENTA = "preventa", "Preventa"
        DESCONTINUADO = "descontinuado", "Descontinuado"
    codigo = models.CharField(
        max_length=20,
        unique=True,
        help_text="Formato sugerido: LF-0001",
        verbose_name="Código",
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título",
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        verbose_name="Slug",
    )
    genero = models.ForeignKey(
        GeneroLiterario,
        on_delete=models.PROTECT,
        related_name="libros",
        verbose_name="Género",
    )
    autor = models.CharField(
        max_length=150,
        verbose_name="Autor",
    )
    editorial = models.CharField(
        max_length=120,
        verbose_name="Editorial",
    )
    anio_publicacion = models.PositiveIntegerField(
        validators=[MinValueValidator(1000), MaxValueValidator(2100)],
        verbose_name="Año de publicación",
    )
    sinopsis = models.TextField(
        verbose_name="Sinopsis",
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        verbose_name="Precio en CLP",
    )
    stock = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Stock",
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.DISPONIBLE,
        verbose_name="Estado",
    )
    portada = models.ImageField(
        upload_to="portadas/",
        blank=True,
        null=True,
        verbose_name="Portada",
    )
    destacado = models.BooleanField(
        default=False,
        verbose_name="¿Destacado?",
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="¿Activo?",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Libro"
        verbose_name_plural = "Libros"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"{self.titulo} ({self.autor})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.titulo)[:200] or "libro"
            slug = base
            contador = 1
            while (
                Libro.objects.filter(slug=slug)
                .exclude(pk=self.pk)
                .exists()
            ):
                slug = f"{base}-{contador}"
                contador += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def en_stock(self):
        return self.stock > 0

    @property
    def disponible(self):
        return self.activo and self.estado in (
            self.Estado.DISPONIBLE,
            self.Estado.PREVENTA,
        )

    @property
    def precio_formateado(self):
        return f"${self.precio:,.0f}".replace(",", ".")