from django.core.management.base import BaseCommand
from django.db.models import Count
from academico.models import Curso
from estudiantes.models import Matricula


class Command(BaseCommand):
    help = 'Fusiona cursos duplicados con el mismo nombre (por el bug de sede=None)'

    def handle(self, *args, **options):
        dups = Curso.objects.values('nombre').annotate(c=Count('id')).filter(c__gt=1)
        total = 0

        for d in dups:
            cursos = Curso.objects.filter(nombre=d['nombre'])
            keeper = cursos.first()
            for c in cursos.exclude(id=keeper.id):
                movidas = Matricula.objects.filter(curso=c).count()
                Matricula.objects.filter(curso=c).update(curso=keeper)
                c.delete()
                total += 1
                self.stdout.write(f'  {c.nombre} (id={c.id}) -> {keeper.id} ({movidas} matrículas movidas)')

        if total == 0:
            self.stdout.write(self.style.SUCCESS('No hay cursos duplicados.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'{total} curso(s) duplicado(s) fusionados.'))
