from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalogo.models import GeneroLiterario, Libro
from apps.usuarios.models import PerfilUsuario

User = get_user_model()


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Poblando la base de datos de Librería El Faro...")

        generos = self._crear_generos()
        total_usuarios = self._crear_usuarios()
        total_libros = self._crear_libros(generos)

        self.stdout.write(
            self.style.SUCCESS(
                f"Poblamiento completado: {len(generos)} géneros, "
                f"{total_libros} libros y {total_usuarios} usuarios de prueba."
            )
        )
        self.stdout.write(
            "Credenciales: admin / Admin12345!  |  cliente / Cliente12345!"
        )

    #Creacion 4
    def _crear_generos(self):
        datos = (
            ("Narrativa Chilena", "La narrativa chilena reúne obras literarias que representan la historia, cultura, "
            "identidad, conflictos sociales y experiencias humanas propias de Chile."),

            ("Ciencia Ficción", "La ciencia ficción es un género narrativo que explora mundos, tecnologías y acontecimientos "
            "imaginarios basados en avances científicos o especulaciones futuristas."),

            ("Ensayo", "El ensayo es un género literario que desarrolla ideas, "
            "reflexiones y opiniones personales sobre diversos temas mediante argumentos y análisis críticos."),
            
            ("Literatura Infantil", "Libros ilustrados y lecturas para niños."),
        )
        generos = {}
        for nombre, descripcion in datos:
            genero, creado = GeneroLiterario.objects.update_or_create(
                nombre=nombre,
                defaults={
                    "descripcion": descripcion,
                    "activo": True,
                },
            )
            generos[nombre] = genero
            accion = "creado" if creado else "actualizado"
            self.stdout.write(f"  Género {accion}: {nombre}")
        return generos

    def _crear_usuarios(self):
        datos = (
            {
                "username": "admin",
                "email": "admin@elfaro.cl",
                "password": "Admin12345!",
                "first_name": "Administrador",
                "last_name": "El Faro",
                "is_staff": True,
                "is_superuser": True,
                "rut": "11.111.111-1",
                "telefono": "+56 9 1111 1111",
                "rol": PerfilUsuario.Rol.ADMINISTRADOR,
                "comuna": "Valparaíso",
                "direccion": "Cerro Alegre 123",
            },
            {
                "username": "cliente",
                "email": "cliente@correo.cl",
                "password": "Cliente12345!",
                "first_name": "Camila",
                "last_name": "Pérez",
                "is_staff": False,
                "is_superuser": False,
                "rut": "22.222.222-2",
                "telefono": "+56 9 2222 2222",
                "rol": PerfilUsuario.Rol.CLIENTE,
                "comuna": "Viña del Mar",
                "direccion": "Av. Libertad 456",
            },
        )

        for item in datos:
            user, creado = User.objects.get_or_create(
                username=item["username"],
                defaults={
                    "email": item["email"],
                    "first_name": item["first_name"],
                    "last_name": item["last_name"],
                    "is_staff": item["is_staff"],
                    "is_superuser": item["is_superuser"],
                    "is_active": True,
                },
            )

            # Deja las credenciales y permisos reproducibles en cada ejecución.
            user.email = item["email"]
            user.first_name = item["first_name"]
            user.last_name = item["last_name"]
            user.is_staff = item["is_staff"]
            user.is_superuser = item["is_superuser"]
            user.is_active = True
            user.set_password(item["password"])
            user.save()

            PerfilUsuario.objects.update_or_create(
                user=user,
                defaults={
                    "rut": item["rut"],
                    "telefono": item["telefono"],
                    "rol": item["rol"],
                    "comuna": item["comuna"],
                    "direccion": item["direccion"],
                },
            )

            accion = "creado" if creado else "actualizado"
            self.stdout.write(f"  Usuario {accion}: {item['username']}")

        return len(datos)

    def _crear_libros(self, generos):
        datos = (
            {
                "codigo": "LF-0001",
                "titulo": "La casa de los espíritus",
                "genero": generos["Narrativa Chilena"],
                "autor": "Isabel Allende",
                "editorial": "Plaza & Janés",
                "anio_publicacion": 1982,
                "sinopsis": (
                    "Saga familiar que recorre cuatro generaciones "
                    "de la familia Trueba en Chile."
                ),
                "precio": Decimal("18990"),
                "stock": 12,
                "estado": Libro.Estado.DISPONIBLE,
                "destacado": True,
                "activo": True,
            },
            {
                "codigo": "LF-0002",
                "titulo": "Martín Rivas",
                "genero": generos["Narrativa Chilena"],
                "autor": "Alberto Blest Gana",
                "editorial": "Zig-Zag",
                "anio_publicacion": 1862,
                "sinopsis": (
                    "Novela costumbrista sobre el ascenso social "
                    "de un joven provinciano en Santiago."
                ),
                "precio": Decimal("12990"),
                "stock": 6,
                "estado": Libro.Estado.DISPONIBLE,
                "destacado": False,
                "activo": True,
            },
            {
                "codigo": "LF-0003",
                "titulo": "Dune",
                "genero": generos["Ciencia Ficción"],
                "autor": "Frank Herbert",
                "editorial": "Debolsillo",
                "anio_publicacion": 1965,
                "sinopsis": (
                    "En el planeta Arrakis, la especia más valiosa "
                    "del universo desata una guerra por el poder."
                ),
                "precio": Decimal("24990"),
                "stock": 9,
                "estado": Libro.Estado.DISPONIBLE,
                "destacado": True,
                "activo": True,
            },
            {
                "codigo": "LF-0004",
                "titulo": "Fundación",
                "genero": generos["Ciencia Ficción"],
                "autor": "Isaac Asimov",
                "editorial": "Debolsillo",
                "anio_publicacion": 1951,
                "sinopsis": (
                    "Un matemático predice la caída del Imperio Galáctico "
                    "y funda una ciencia para acortar la oscuridad."
                ),
                "precio": Decimal("19990"),
                "stock": 0,
                "estado": Libro.Estado.AGOTADO,
                "destacado": False,
                "activo": True,
            },
            {
                "codigo": "LF-0005",
                "titulo": "El arte de la guerra",
                "genero": generos["Ensayo"],
                "autor": "Sun Tzu",
                "editorial": "Edaf",
                "anio_publicacion": 2005,
                "sinopsis": (
                    "Tratado clásico sobre estrategia, liderazgo y conflicto."
                ),
                "precio": Decimal("9990"),
                "stock": 20,
                "estado": Libro.Estado.DISPONIBLE,
                "destacado": False,
                "activo": True,
            },
            {
                "codigo": "LF-0006",
                "titulo": "Sapiens: De animales a dioses",
                "genero": generos["Ensayo"],
                "autor": "Yuval Noah Harari",
                "editorial": "Debate",
                "anio_publicacion": 2014,
                "sinopsis": (
                    "Recorrido por la historia de la humanidad, "
                    "desde el Paleolítico hasta la era digital."
                ),
                "precio": Decimal("27990"),
                "stock": 4,
                "estado": Libro.Estado.DESCONTINUADO,
                "destacado": False,
                "activo": False,
            },
            {
                "codigo": "LF-0007",
                "titulo": "El Principito",
                "genero": generos["Literatura Infantil"],
                "autor": "Antoine de Saint-Exupéry",
                "editorial": "Salamandra",
                "anio_publicacion": 1943,
                "sinopsis": (
                    "Un piloto perdido en el desierto conoce a un pequeño "
                    "príncipe que le enseña a mirar con el corazón."
                ),
                "precio": Decimal("8990"),
                "stock": 15,
                "estado": Libro.Estado.DISPONIBLE,
                "destacado": True,
                "activo": True,
            },
            {
                "codigo": "LF-0008",
                "titulo": "La historia interminable",
                "genero": generos["Literatura Infantil"],
                "autor": "Michael Ende",
                "editorial": "Alfaguara",
                "anio_publicacion": 1979,
                "sinopsis": (
                    "Una niña descubre un libro mágico y un mundo "
                    "fantástico que se desmorona."
                ),
                "precio": Decimal("16990"),
                "stock": 5,
                "estado": Libro.Estado.PREVENTA,
                "destacado": False,
                "activo": True,
            },
        )

        for item in datos:
            codigo = item["codigo"]
            defaults = {
                clave: valor
                for clave, valor in item.items()
                if clave != "codigo"
            }
            libro, creado = Libro.objects.update_or_create(
                codigo=codigo,
                defaults=defaults,
            )
            accion = "creado" if creado else "actualizado"
            self.stdout.write(
                f"  Libro {accion}: {codigo} - {libro.titulo}"
            )

        return len(datos)