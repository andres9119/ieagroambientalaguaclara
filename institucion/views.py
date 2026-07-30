import random
from pathlib import Path
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.views.generic import TemplateView, View
from .models import InformacionInstitucional, PilarEducativo, DocumentoInteres, CertificadoEmitido
from .forms import SolicitarCertificadoForm
from estudiantes.utils import render_to_pdf

MAX_CERTIFICADOS_POR_MES = 3


def numero_a_palabras(num):
    unidades = ['cero', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete',
                'ocho', 'nueve', 'diez', 'once', 'doce', 'trece', 'catorce',
                'quince', 'dieciseis', 'diecisiete', 'dieciocho', 'diecinueve',
                'veinte', 'veintiuno', 'veintidos', 'veintitres', 'veinticuatro',
                'veinticinco', 'veintiseis', 'veintisiete', 'veintiocho', 'veintinueve']
    decenas = ['', '', 'treinta', 'cuarenta', 'cincuenta', 'sesenta',
               'setenta', 'ochenta', 'noventa']
    centenas = ['', 'ciento', 'doscientos', 'trescientos', 'cuatrocientos',
                'quinientos', 'seiscientos', 'setecientos', 'ochocientos', 'novecientos']

    if num < 30:
        return unidades[num]
    if num < 100:
        d = num // 10
        u = num % 10
        if u == 0:
            return decenas[d]
        return decenas[d] + ' y ' + unidades[u]
    if num < 1000:
        c = num // 100
        resto = num % 100
        if num == 100:
            return 'cien'
        if resto == 0:
            return centenas[c]
        return centenas[c] + ' ' + numero_a_palabras(resto)
    if num < 1000000:
        m = num // 1000
        resto = num % 1000
        if m == 1:
            mil = 'mil'
        else:
            mil = numero_a_palabras(m) + ' mil'
        if resto == 0:
            return mil
        return mil + ' ' + numero_a_palabras(resto)
    return str(num)


def fecha_a_letras(fecha):
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
             'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    dia = fecha.day
    mes = meses[fecha.month - 1]
    anio = fecha.year

    if dia == 1:
        dia_palabra = 'un'
    elif dia == 21:
        dia_palabra = 'veintiun'
    else:
        dia_palabra = numero_a_palabras(dia)

    anio_palabra = numero_a_palabras(anio).capitalize()

    return f'{dia_palabra} ({dia}) días del mes de {mes} del año {anio_palabra}. ({anio})'


def get_info():
    return InformacionInstitucional.objects.first()


class InstitucionView(TemplateView):
    template_name = 'institucion/detalle.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['info'] = get_info()
        context['pilares'] = PilarEducativo.objects.all()
        return context


class PoliticaPrivacidadView(TemplateView):
    template_name = 'institucion/politica_privacidad.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['info'] = get_info()
        return context


class DocumentosListView(TemplateView):
    template_name = 'institucion/documentos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        documentos_qs = DocumentoInteres.objects.filter(publico=True)
        if self.request.user.is_authenticated:
            documentos_qs = DocumentoInteres.objects.all()

        context['manuales'] = documentos_qs.filter(categoria='manual')
        context['decretos'] = documentos_qs.filter(categoria='decreto')
        context['circulares'] = documentos_qs.filter(categoria='circular')
        context['generales'] = documentos_qs.filter(categoria='general')
        context['certificado_form'] = SolicitarCertificadoForm()
        context['certificado_creado'] = None
        context['info'] = get_info()

        if self.request.user.is_authenticated and hasattr(self.request.user, 'perfil_estudiante'):
            from estudiantes.models import DocumentoEstudiante
            estudiante = self.request.user.perfil_estudiante
            context['estudiante'] = estudiante
            context['mis_certificados'] = DocumentoEstudiante.objects.filter(estudiante=estudiante)
            context['es_estudiante'] = True
            context['mis_emitidos'] = CertificadoEmitido.objects.filter(
                estudiante_documento=estudiante.usuario.username
            ).order_by('-fecha_emision')[:10]

        return context

    def post(self, request, *args, **kwargs):
        if not (request.user.is_authenticated and hasattr(request.user, 'perfil_estudiante')):
            messages.error(request, 'Debes iniciar sesión como estudiante para solicitar el certificado.')
            return self.get(request, *args, **kwargs)

        form = SolicitarCertificadoForm(request.POST)
        context = self.get_context_data()
        context['certificado_form'] = form

        if form.is_valid():
            estudiante = request.user.perfil_estudiante

            if not estudiante.pago_certificado:
                messages.error(request, 'La descarga de certificados está bloqueada para tu cuenta. Solicita al administrador que la habilite.')
                return self.get(request, *args, **kwargs)

            desde = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            descargas_mes = CertificadoEmitido.objects.filter(
                estudiante_documento=estudiante.usuario.username,
                fecha_emision__gte=desde
            ).count()
            if descargas_mes >= MAX_CERTIFICADOS_POR_MES:
                messages.error(request, f'Has alcanzado el límite de {MAX_CERTIFICADOS_POR_MES} certificados por mes. Inténtelo de nuevo el próximo mes.')
                return self.get(request, *args, **kwargs)

            matricula_activa = estudiante.matriculas.filter(activo=True).first()
            curso = matricula_activa.curso if matricula_activa else None

            codigo = str(random.randint(1000000000, 9999999999))
            while CertificadoEmitido.objects.filter(codigo=codigo).exists():
                codigo = str(random.randint(1000000000, 9999999999))

            sede_nombre = curso.sede.nombre if curso and curso.sede else (getattr(get_info(), 'sede_principal', '') or 'Sede Principal')

            cert = CertificadoEmitido.objects.create(
                codigo=codigo,
                estudiante_nombre=estudiante.usuario.get_full_name() or estudiante.usuario.username,
                estudiante_documento=estudiante.usuario.username,
                tipo_documento=estudiante.get_tipo_documento_display(),
                grado=curso.nombre if curso else 'Sin Curso',
                nivel=curso.nivel if curso else '',
                anio=timezone.now().year,
                sede=sede_nombre,
            )

            estudiante.save()

            context['certificado_creado'] = cert
            return self.render_to_response(context)

        return self.render_to_response(context)


class GenerarCertificadoEstudiosPDF(View):
    def get(self, request, *args, **kwargs):
        codigo = request.GET.get('codigo', '').strip()
        cert = get_object_or_404(CertificadoEmitido, codigo=codigo, valido=True)

        info = get_info()
        ahora = timezone.now()
        escudo_path = str(Path(__file__).resolve().parent.parent / 'static' / 'img' / 'escudo.png')

        verificacion_url = f'https://ieagroambientalaguaclara.com/institucion/certificados/verificar/?codigo={cert.codigo}'

        qr_path = None
        try:
            import qrcode
            qr = qrcode.make(verificacion_url)
            qr_path = str(Path(__file__).resolve().parent.parent / 'static' / 'img' / f'qr_{cert.codigo}.png')
            qr.save(qr_path)
        except Exception:
            qr_path = None

        context = {
            'info': info,
            'nombre_completo': cert.estudiante_nombre,
            'tipo_documento': cert.tipo_documento,
            'numero_documento': cert.estudiante_documento,
            'grado': cert.grado,
            'nivel': cert.nivel,
            'sede': cert.sede or getattr(info, 'sede_principal', 'Sede Principal'),
            'anio': cert.anio,
            'calendario': getattr(info, 'calendario', 'A') or 'A',
            'jornada': getattr(info, 'jornada', 'Mañana') or 'Mañana',
            'horario': getattr(info, 'horario', '') or 'Lunes a viernes de 08:00 am a 02:20 pm',
            'codigo_verificacion': cert.codigo,
            'fecha': ahora,
            'fecha_letras': fecha_a_letras(ahora),
            'escudo_path': escudo_path,
            'qr_path': qr_path,
            'verificacion_url': verificacion_url,
            'nombre_rector': getattr(info, 'nombre_rector', '') or 'Mgtr. Luz Enith Valencia Hernandez',
            'rector_cc': getattr(info, 'rector_cc', '') or 'C.C. 1067464246',
            'nombre_colegio': getattr(info, 'nombre_colegio', '') or 'INSTITUCION EDUCATIVA AGROAMBIENTAL AGUA CLARA',
            'dane': getattr(info, 'dane', '') or '219780000343',
            'nit': getattr(info, 'nit', '') or '901803194-5',
            'resolucion': getattr(info, 'resolucion', '') or '01458-03-2012',
            'departamento': getattr(info, 'departamento', '') or 'DEPARTAMENTO DEL CAUCA',
            'municipio': getattr(info, 'municipio', '') or 'Suarez',
            'codigo_documento': getattr(info, 'codigo_documento', '') or 'CO-02',
            'version_documento': getattr(info, 'version_documento', '') or '01',
        }

        pdf_response = render_to_pdf('institucion/certificado_estudios_pdf.html', context)
        if pdf_response:
            filename = f"Certificado_Estudios_{cert.estudiante_documento}.pdf"
            pdf_response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return pdf_response

        messages.error(request, 'Ocurrió un error al generar el certificado.')
        return redirect('documentos')


class VerificarCertificadoView(TemplateView):
    template_name = 'institucion/verificar_certificado.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['info'] = get_info()
        context['certificado'] = None
        context['codigo'] = self.request.GET.get('codigo', '')
        context['valido'] = False
        context['desde_qr'] = bool(self.request.GET.get('codigo'))
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        codigo = context['codigo']
        if codigo:
            cert = CertificadoEmitido.objects.filter(codigo=codigo, valido=True).first()
            if cert:
                context['certificado'] = cert
                context['valido'] = True
            else:
                messages.error(request, 'El código ingresado no es válido o ha sido revocado.')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        codigo = request.POST.get('codigo', '').strip()
        context = self.get_context_data()
        context['codigo'] = codigo

        if not codigo:
            messages.error(request, 'Ingresa un código de verificación.')
            return render(request, self.template_name, context)

        cert = CertificadoEmitido.objects.filter(codigo=codigo, valido=True).first()
        if cert:
            context['certificado'] = cert
            context['valido'] = True
        else:
            messages.error(request, 'El codigo ingresado no es valido o ha sido revocado.')

        return render(request, self.template_name, context)