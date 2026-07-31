from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudiantes', '0018_alter_estudiante_tipo_documento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estudiante',
            name='celular',
            field=models.CharField(blank=True, max_length=50, verbose_name='Celular'),
        ),
        migrations.AlterField(
            model_name='estudiante',
            name='telefono',
            field=models.CharField(blank=True, max_length=50, verbose_name='Teléfono'),
        ),
    ]
