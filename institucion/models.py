from django.db import models

class InformacionInstitucional(models.Model):
    historia = models.TextField(verbose_name="Historia")
    foto_historia = models.ImageField(upload_to='institucion/', verbose_name="Imagen de Historia", blank=True, null=True, help_text="Imagen que acompaña la sección de historia")
    mision = models.TextField(verbose_name="Misión")
    vision = models.TextField(verbose_name="Visión")
    valores = models.TextField(verbose_name="Valores")
    lema = models.CharField(max_length=200, verbose_name="Lema o Tagline", blank=True, null=True, help_text="Frase corta que aparece en el banner principal")
    mensaje_rectoria = models.TextField(verbose_name="Mensaje de Rectoría", blank=True, null=True)
    nombre_rector = models.CharField(max_length=100, verbose_name="Nombre del Rector(a)", blank=True, null=True)
    foto_rector = models.ImageField(upload_to='institucion/', verbose_name="Foto del Rector(a)", blank=True, null=True)
    politica_privacidad = models.TextField(verbose_name="Política de Tratamiento de Datos Personales", blank=True, null=True)
    aviso_privacidad_corto = models.TextField(verbose_name="Aviso de Privacidad Corto", blank=True, null=True, help_text="Texto que aparecerá en los formularios")

    nombre_colegio = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nombre de la Institución", help_text="Ej: Institución Educativa Agroambiental Agua Clara")
    dane = models.CharField(max_length=20, blank=True, null=True, verbose_name="Código DANE")
    nit = models.CharField(max_length=20, blank=True, null=True, verbose_name="NIT")
    resolucion = models.CharField(max_length=100, blank=True, null=True, verbose_name="Resolución", help_text="Ej: 01458-03-2012")
    sede_principal = models.CharField(max_length=200, blank=True, null=True, verbose_name="Sede Principal", help_text="Ej: Centro Docente Agua Clara - Sede Principal")
    departamento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Departamento")
    municipio = models.CharField(max_length=100, blank=True, null=True, verbose_name="Municipio")
    calendario = models.CharField(max_length=10, blank=True, null=True, default='A', verbose_name="Calendario")
    jornada = models.CharField(max_length=50, blank=True, null=True, default='Mañana', verbose_name="Jornada")
    horario = models.CharField(max_length=200, blank=True, null=True, verbose_name="Horario", help_text="Ej: Lunes a viernes de 08:00 am a 02:20 pm")
    rector_cc = models.CharField(max_length=20, blank=True, null=True, verbose_name="C.C. del Rector(a)")
    codigo_documento = models.CharField(max_length=20, blank=True, null=True, default='CO-02', verbose_name="Código de Documento")
    version_documento = models.CharField(max_length=10, blank=True, null=True, default='01', verbose_name="Versión de Documento")

    class Meta:
        verbose_name = "Información Institucional"
        verbose_name_plural = "Información Institucional"

    def __str__(self):
        return "Información del Colegio"

class DocumentoInteres(models.Model):
    CATEGORIAS = (
        ('manual', 'Manual de Convivencia'),
        ('decreto', 'Decretos y Resoluciones'),
        ('circular', 'Circulares'),
        ('general', 'Información General'),
    )
    titulo = models.CharField(max_length=200, verbose_name="Título del Documento")
    archivo = models.FileField(upload_to='documentos_institucionales/', verbose_name="Archivo")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='general', verbose_name="Categoría")
    fecha_publicacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Publicación")
    publico = models.BooleanField(default=True, verbose_name="Es Público", help_text="Si se desmarca, solo usuarios registrados podrán verlo")

    class Meta:
        verbose_name = "Documento de Interés"
        verbose_name_plural = "Documentos de Interés"
        ordering = ['-fecha_publicacion']

    def __str__(self):
        return self.titulo


class CertificadoEmitido(models.Model):
    codigo = models.CharField(max_length=12, unique=True, verbose_name="Código de Verificación")
    estudiante_nombre = models.CharField(max_length=300, verbose_name="Nombre del Estudiante")
    estudiante_documento = models.CharField(max_length=60, verbose_name="Documento")
    tipo_documento = models.CharField(max_length=50, verbose_name="Tipo de Documento")
    grado = models.CharField(max_length=100, verbose_name="Grado")
    nivel = models.CharField(max_length=100, blank=True, verbose_name="Nivel")
    anio = models.PositiveIntegerField(verbose_name="Año Lectivo")
    sede = models.CharField(max_length=200, blank=True, verbose_name="Sede")
    fecha_emision = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Emisión")
    valido = models.BooleanField(default=True, verbose_name="Válido")

    class Meta:
        verbose_name = "Certificado Emitido"
        verbose_name_plural = "Certificados Emitidos"
        ordering = ['-fecha_emision']

    def __str__(self):
        return f"{self.codigo} - {self.estudiante_nombre} ({self.anio})"


class PilarEducativo(models.Model):
    titulo = models.CharField(max_length=100, verbose_name="Título")
    descripcion = models.TextField(verbose_name="Descripción")
    icono = models.CharField(max_length=50, verbose_name="Clase de Icono (FontAwesome)", help_text="Ejemplo: fas fa-book")
    orden = models.IntegerField(default=0, verbose_name="Orden de visualización")

    class Meta:
        verbose_name = "Pilar Educativo"
        verbose_name_plural = "Pilares Educativos"
        ordering = ['orden']

    def __str__(self):
        return self.titulo
