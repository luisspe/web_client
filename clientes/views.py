from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.http import require_POST
from .forms import ClienteRegistrationForm, ClienteLoginForm, AdminRegistrationForm, AdminLoginForm
from .models import Appointment, CustomUser, Documento,  UserNotificationSettings, Notificacion, AppointmentType
import uuid
from django.db import IntegrityError
from django.http import JsonResponse
import requests
from uuid import uuid4
import json
#imports for appointments
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import time, datetime, timedelta
from django.contrib import messages
from django.utils.timezone import localtime
#credentials
from decouple import config

# Configuración de la API
api_url = config('API_URL')
API_HEADER_AUTHORIZATION = config('API_KEY')
headers = {
    'x-api-key': API_HEADER_AUTHORIZATION
}






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


# Función para crear un evento o un cliente
def create_event_or_client(request, client_info, event_info, headers, api_url):
    """
    Crea un cliente o un evento en la API.
    Si el cliente ya existe, solo crea el evento.
    Si el cliente no existe, primero crea el cliente y luego el evento.
    """
    client_id = None
    response = requests.get(f"{api_url}clients/query/{client_info['email']}/", headers=headers)
    if response.status_code == 200:
        client_data = response.json()
        client_id = client_data['client_id']
        update_response = requests.put(f"{api_url}clients/{client_id}/", headers=headers, json=client_info)
        if update_response.status_code != 200:
            print("Error al actualizar la información del cliente")
            print(update_response.json())  # Esto imprimirá la respuesta completa para que puedas ver qué salió mal

    else:
        if 'client_id' not in client_info:
            client_id = str(uuid4())
            client_info['client_id'] = client_id
        response = requests.post(f"{api_url}clients/create/", headers=headers, json=client_info)
        if response.status_code == 201:
            #event_info["event_data"]['visit'] = "P1"
            if 'client_id' not in event_info:
                event_info['client_id'] = client_id
            response = requests.post(f"{api_url}events/create/", headers=headers, json=event_info)
            return client_id, "Evento creado exitosamente" if response.status_code == 201 or response.status_code == 200 else "Error al crear el evento"
    event_info['client_id'] = client_id
    response = requests.post(f"{api_url}events/create/", headers=headers, json=event_info)
    return client_id, "Evento creado exitosamente" if response.status_code == 201 else "Error al crear el evento"


# Funcion para buscar client por email y rellenar los campos del formulario automaticamente
def fetch_client_by_email(request):
    # Use the email of the logged-in user
    user_email = request.user.email

    # The API URL, ensure that this is the correct URL for your API
    api_url = "https://lbvj22e1he.execute-api.us-east-1.amazonaws.com/dev/clients/query/"
    
    # Headers for the API request, add your required headers here
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': 'IUPDlxEc2i2xxCYpmmnGL2JmqhVRkQba1n9Tbl6B',
    }

    response = requests.get(f"{api_url}{user_email}/", headers=headers)
    if response.status_code == 200:
        client_data = response.json()
        return JsonResponse(client_data)
    else:
        return JsonResponse({"error": "Cliente no encontrado"}, status=response.status_code)
        

@login_required
def cliente_citas(request):
    # Obtener citas programadas para el cliente
    citas_agendadas = Appointment.objects.filter(usuario=request.user).order_by('scheduled_time')
    notificaciones = Notificacion.objects.filter(usuario=request.user, leida=False).order_by('-fecha_creacion')
    citas = [{
            'fecha': localtime(cita.scheduled_time).strftime("%A, %d de %B, %Y"),
            'hora': localtime(cita.scheduled_time).strftime("%H:%M - ") + localtime(cita.scheduled_time + timedelta(hours=1)).strftime("%H:%M"),
            'tipo': cita.appointment_type.name
        } for cita in citas_agendadas]
        
    context = {
        'citas_agendadas': citas,
        'notificaciones': notificaciones,
    }
    
    return render(request, 'cliente_citas.html', context)

@require_http_methods(['POST'])
def book_appointment(request):
    # Recibir y parsear los datos de la cita
    appointment_type_name = request.POST.get('appointment_type')
    scheduled_time_str = request.POST.get('scheduled_time')
    scheduled_time_naive = parse_datetime(scheduled_time_str)
    

     # Asigna la zona horaria a la fecha y hora
    scheduled_time = timezone.make_aware(scheduled_time_naive, timezone.get_current_timezone())
    
    if not scheduled_time:
        return JsonResponse({'success': False, 'message': 'Invalid datetime format.'}, status=400)

    # Obtener conteo de citas
    appointment_type = get_object_or_404(AppointmentType, name=appointment_type_name)

    # Verificar disponibilidad
    appointment_count = is_time_slot_available(request.user, scheduled_time)
        # Crear y guardar la nueva cita si está disponible
    client_response = fetch_client_by_email(request)
    if client_response.status_code == 200:
        client_data = client_response.content.decode('utf-8')
        client_data = json.loads(client_data)

        #extract the client_id
        client_id = client_data.get('client_id')
        event_data = {
             "client_id": client_id,
                "event_data": {
                    "concept": "appointment",
                    "type":appointment_type.name,
                },
                "event_source": "web_application",
                "event_type": "appointment_generation",
        }
        event_api_url = f"https://lbvj22e1he.execute-api.us-east-1.amazonaws.com/dev/events/create/"
        headers = {'Content-Type': 'application/json', 'x-api-key': 'IUPDlxEc2i2xxCYpmmnGL2JmqhVRkQba1n9Tbl6B'}
        response = requests.post(event_api_url, json=event_data, headers=headers)
        
             
    if appointment_count:
        Appointment.objects.create(
            usuario=request.user,
            appointment_type=appointment_type,  # Usar la instancia de AppointmentType
            scheduled_time=scheduled_time
        )
        messages.success(request, 'Cita agendada exitosamente.')
        if response.status_code == 200 or response.status_code == 201:
            print("evento creado")

    else:
        messages.error(request, 'Las citas para este horario están agotadas.')
    return redirect('cliente_citas')

def is_time_slot_available(user, start_time):
    end_time = start_time + timezone.timedelta(hours=1)
    
    # Filtrar citas que se superponen con el rango de tiempo seleccionado
    overlapping_appointments = Appointment.objects.filter(
        scheduled_time__lt=end_time,
        end_time__gt=start_time
    )
    
    # Cuenta las citas existentes en el rango de tiempo
    appointment_count = overlapping_appointments.count()
    return appointment_count < 5  # Permitir hasta 5 citas



@login_required
def cliente_dashboard_documentos(request):
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
        
        #post a la api
        client_response = fetch_client_by_email(request)
        if client_response.status_code == 200:
            client_data = client_response.content.decode('utf-8')  # Decode the JSON content
            client_data = json.loads(client_data)  # Parse the JSON content to get the dictionary

            # Extract client_id from the dictionary
            client_id = client_data.get('client_id')

            # Prepare the event data
            event_data = {
                
                "client_id": client_id,
                "event_data": {
                    "concept": "Upload de documento",
                    "file_name": file.name,
                    "document":tipo_documento,
                    "file_type": file.content_type,
                    "file_size": file.size, 
                },
                "event_source": "web_application",
                "event_type": "document_upload",
            }

            event_api_url = f"https://lbvj22e1he.execute-api.us-east-1.amazonaws.com/dev/events/create/"
            headers = {'Content-Type': 'application/json', 'x-api-key': 'IUPDlxEc2i2xxCYpmmnGL2JmqhVRkQba1n9Tbl6B'}  # Add any required headers
            response = requests.post(event_api_url, json=event_data, headers=headers)
            if response.status_code == 200 or response.status_code == 201:
                documento.save()
                return JsonResponse({'status': 'Completado', 'id': documento.id})
                
            else:
                return JsonResponse({'status': 'Error', 'message': 'Error al crear el evento.'}, status=response.status_code)
        
        

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


@login_required
def notifications(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user, leida=False).order_by('-fecha_creacion')
    notificaciones_list = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    
    context ={
        'notificaciones': notificaciones,
        'notificaciones_list':notificaciones_list
    }

    return render(request, 'notifications.html', context)


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