from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.http import require_POST
from .forms import ClienteRegistrationForm, ClienteLoginForm, AdminRegistrationForm, AdminLoginForm
from .models import CustomUser, Documento,  UserNotificationSettings, Notificacion
from django.core.exceptions import ValidationError
import uuid
from django.db import IntegrityError
from django.conf import settings
from django.http import JsonResponse







def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('admin_dashboard')  # o donde sea que deba redirigir después del login
    else:
        form = AdminLoginForm()
    return render(request, 'admin_login.html', {'form': form})


def cliente_login(request):
    if request.method == 'POST':
        form = ClienteLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            user = CustomUser.objects.filter(email=email, phone_number=phone_number).first()
            if user and not user.is_admin:
                login(request, user)
                return redirect('cliente_dashboard')  # Asegúrate de tener esta vista y URL
            else:
                form.add_error(None, "Credenciales incorrectas o no es cliente.")
    else:
        form = ClienteLoginForm()
    return render(request, 'login.html', {'form': form})

@user_passes_test(lambda u: u.is_staff)
def create_client(request):
    if request.method == 'POST':
        form = ClienteRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']

            # Verificar si el correo ya está en uso
            if CustomUser.objects.filter(email=email).exists():
                form.add_error('email', 'Este correo electrónico ya está en uso.')

            # Verificar si el número de teléfono ya está en uso
            elif CustomUser.objects.filter(phone_number=phone_number).exists():
                form.add_error('phone_number', 'Este número de teléfono ya está en uso.')

            else:
                try:
                    new_user = form.save(commit=False)
                    new_user.is_admin = False
                    new_user.username = generate_unique_username(form.cleaned_data['nombre'])
                    new_user.set_password('some_default_password')  # Considera un método más seguro para las contraseñas
                    new_user.save()
                    return redirect('cliente_login')
                except IntegrityError:
                    form.add_error('nombre', 'Este nombre ya está en uso.')
        # Si hay errores, se vuelve a renderizar el formulario con ellos
        return render(request, 'create_client.html', {'form': form})

    else:
        form = ClienteRegistrationForm()
        return render(request, 'create_client.html', {'form': form})



def logout_view(request):
    logout(request)
    return redirect('cliente_login')

def generate_unique_username(nombre):
    """Genera un nombre de usuario único a partir del nombre."""
    # Eliminar espacios y convertir a minúsculas
    base_username = nombre.replace(" ", "").lower()
    unique_username = base_username + uuid.uuid4().hex[:6].lower()

    while CustomUser.objects.filter(username=unique_username).exists():
        unique_username = base_username + uuid.uuid4().hex[:6].lower()

    return unique_username


@user_passes_test(lambda u: u.is_superuser)
def create_admin(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            print("Form data:", form.cleaned_data) 
            
            form.save()
            return redirect('create_client')
            
    else:
        form = AdminRegistrationForm()

    return render(request, 'create_admin.html', {'form': form})


@login_required
def cliente_citas(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user, leida=False).order_by('-fecha_creacion')
    context = {
        'notificaciones': notificaciones
    }
    return render(request, 'cliente_citas.html', context)

@login_required
def cliente_dashboard(request):
    documentos_usuario = Documento.objects.filter(usuario=request.user).order_by('-fecha_actualizacion')
    
    documentos_unicos = {}
    for doc in documentos_usuario:
        if doc.tipo_documento not in documentos_unicos:
            documentos_unicos[doc.tipo_documento] = doc

    documentos_subidos = {tipo: True for tipo, doc in documentos_unicos.items() if doc.estado == 'SUBIDO'}
    documentos_rechazados = {tipo: True for tipo, doc in documentos_unicos.items() if doc.estado == 'RECHAZADO'}
    documentos_aprobados = {tipo: True for tipo, doc in documentos_unicos.items() if doc.estado == 'APROBADO'}

    # Obtener las notificaciones del usuario
    notificaciones = Notificacion.objects.filter(usuario=request.user, leida=False).order_by('-fecha_creacion')

    context = {
        'documentos_subidos': documentos_subidos,
        'documentos_rechazados': documentos_rechazados,
        'documentos_aprobados': documentos_aprobados,
        'notificaciones': notificaciones,
    }

    return render(request, 'cliente_dashboard.html', context)

@login_required
def upload_file(request):
    if request.method == 'POST':
        tipo_documento = request.POST.get('tipo_documento')
        file = request.FILES.get('file')

        # Validar que el archivo sea un PDF
        if file.content_type != 'application/pdf':
            return JsonResponse({'status': 'Error', 'message': 'Por favor, sube un archivo PDF.'}, status=400)

        # Asociar el documento con el usuario
        documento = Documento(usuario=request.user, archivo=file, tipo_documento=tipo_documento)
        
        # Guardar el archivo
        documento.save()

        return JsonResponse({'status': 'Completado', 'id': documento.id})
    
    return JsonResponse({'status': 'Error'}, status=400)


@login_required
def notification_settings(request):
    # Obtener las notificaciones del usuario
    notificaciones = Notificacion.objects.filter(usuario=request.user, leida=False).order_by('-fecha_creacion')
    
    if request.method == 'POST':
        settings, created = UserNotificationSettings.objects.get_or_create(user=request.user)
        settings.receive_notifications = request.POST.get('receive_notifications') == 'on'
        settings.notify_document_status = request.POST.get('notify_document_status') == 'on'
        settings.notify_appointment_confirmation = request.POST.get('notify_appointment_confirmation') == 'on'
        settings.notify_appointment_reminder = request.POST.get('notify_appointment_reminder') == 'on'
        settings.save()
        return redirect('notification_settings')
    context ={
        'notificaciones': notificaciones,
    }
    current_settings = UserNotificationSettings.objects.get_or_create(user=request.user)[0]
    return render(request, 'notification_settings.html', {'settings': current_settings, 'notificaciones': notificaciones})



@require_POST
@login_required
def eliminar_notificacion(request, id_notificacion):
    try:
        notificacion = Notificacion.objects.get(id=id_notificacion, usuario=request.user)
        notificacion.leida = True  # O notificacion.delete() si prefieres eliminarla
        notificacion.save()
        return JsonResponse({'status': 'success'})
    except Notificacion.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)
    


@login_required
def comentarios_y_sugerencias(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user, leida=False).order_by('-fecha_creacion')
    context = {
        'notificaciones': notificaciones
    }
    return render(request, 'cliente_comentarios.html', context)