from django.forms import formset_factory
from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import user_passes_test, login_required
from .forms import AdminRegistrationForm, AdminLoginForm, ClienteRegistrationForm
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from clientes.models import CustomUser, Documento
import uuid
from .forms import DocumentoForm
import requests
from dateutil import parser
from django.utils import timezone

# LOGINS Y CREACION DE CUENTAS


def admin_login(request):
    if request.method == "POST":
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(
                request,
                username=email,
                password=password,
                backend="administradores.backends.EmailAuthenticationBackend",
            )

            if user is not None and user.is_admin:
                login(request, user)
                return redirect("search_client")
            else:
                form.add_error(
                    None, "Credenciales inválidas o el usuario no es administrador."
                )
        else:
            print("Errores del formulario:", form.errors)
    else:
        form = AdminLoginForm()

    return render(request, "admin_login.html", {"form": form})


@user_passes_test(lambda u: u.is_superuser)
def create_admin(request):
    if request.method == "POST":
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            print("Form data:", form.cleaned_data)

            form.save()
            return redirect("create_client")
    else:
        form = AdminRegistrationForm()
    return render(request, "create_admin.html", {"form": form})


def generate_unique_username(nombre):
    """Genera un nombre de usuario único a partir del nombre."""
    # Eliminar espacios y convertir a minúsculas
    base_username = nombre.replace(" ", "").lower()
    unique_username = base_username + uuid.uuid4().hex[:6].lower()

    while CustomUser.objects.filter(username=unique_username).exists():
        unique_username = base_username + uuid.uuid4().hex[:6].lower()

    return unique_username


@user_passes_test(lambda u: u.is_staff)
def create_client(request):
    if request.method == "POST":
        form = ClienteRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            phone_number = form.cleaned_data["phone_number"]

            # Verificar si el correo ya está en uso
            if CustomUser.objects.filter(email=email).exists():
                form.add_error("email", "Este correo electrónico ya está en uso.")

            # Verificar si el número de teléfono ya está en uso
            elif CustomUser.objects.filter(phone_number=phone_number).exists():
                form.add_error(
                    "phone_number", "Este número de teléfono ya está en uso."
                )

            else:
                try:
                    new_user = form.save(commit=False)
                    new_user.is_admin = False
                    new_user.username = generate_unique_username(
                        form.cleaned_data["nombre"]
                    )
                    new_user.set_password(
                        "some_default_password"
                    )  # Considera un método más seguro para las contraseñas
                    new_user.save()
                    return redirect("cliente_login")
                except IntegrityError:
                    form.add_error("nombre", "Este nombre ya está en uso.")
        # Si hay errores, se vuelve a renderizar el formulario con ellos
        return render(request, "create_client.html", {"form": form})

    else:
        form = ClienteRegistrationForm()
        return render(request, "create_client.html", {"form": form})


# FUNCIONALIDAD DE DASHBOARD PARA VENDEDORES
# Función para obtener los datos del cliente usando el email del usuario logueado


@user_passes_test(lambda u: u.is_staff)
def search_client(request):
    query = request.GET.get("q", "")
    clients = CustomUser.objects.filter(nombre__icontains=query) if query else []
    return render(request, "search_client.html", {"clients": clients})


def fetch_client_by_email(email):
    api_url = (
        "https://lbvj22e1he.execute-api.us-east-1.amazonaws.com/dev/clients/query/"
    )
    headers = {
        "Content-Type": "application/json",
        "x-api-key": "IUPDlxEc2i2xxCYpmmnGL2JmqhVRkQba1n9Tbl6B",
    }
    response = requests.get(f"{api_url}{email}/", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None


@user_passes_test(lambda u: u.is_staff)
def expediente_cliente(request, cliente_id):
    documentos_activos = Documento.objects.filter(usuario_id=cliente_id, activo=True)
    cliente = get_object_or_404(CustomUser, pk=cliente_id)

    if request.method == "POST":
        documento_id = request.POST.get("doc_id")
        documento = get_object_or_404(Documento, pk=documento_id, activo=True)
        form = DocumentoForm(
            request.POST, instance=documento, prefix="doc_" + str(documento_id)
        )

        if form.is_valid():
            form.save()
            return redirect("expediente_cliente", cliente_id=cliente_id)

    documentos_forms = [
        (
            documento,
            DocumentoForm(instance=documento, prefix="doc_" + str(documento.id)),
        )
        for documento in documentos_activos
    ]

    client_data = fetch_client_by_email(cliente.email)

    tipo_evento_mapa = {
        "document_upload": "Subida de Documento",
        "appointment_generation": "Generación de Cita",
        "bitacora_venta_update": "Actualización en bitacora de ventas",
        # Agrega otros mapeos según sea necesario
    }

    event_source_mapa = {
        "Bitacora_de_ventas": "Bitacora de ventas",
    }

    campo_bitacora_mapa = {
        "ESTATUS": "Estatus de crédito",
    }
    tipo_documento_mapa = {
        "CONSTANCIA_FISCAL": "Constancia fiscal",
        "CURP": "CURP",
        "INE_FRENTE": "Frente de INE",
        "INE_REVERSO": "Reverso de INE" , 
    }

    eventos = []
    if client_data:
        client_id = client_data.get("client_id")
        events_api_url = f"https://lbvj22e1he.execute-api.us-east-1.amazonaws.com/dev/clients/{client_id}/events/"
        client_info_url = f"https://lbvj22e1he.execute-api.us-east-1.amazonaws.com/dev/clients/{client_id}/"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": "IUPDlxEc2i2xxCYpmmnGL2JmqhVRkQba1n9Tbl6B",
        }
        client_info_response = requests.get(client_info_url, headers=headers)
        client_info = {}
        if client_info_response.status_code == 200:
            client_info = client_info_response.json()
        events_response = requests.get(events_api_url, headers=headers)
        if events_response.status_code == 200:
            raw_eventos = events_response.json().get("events", [])
            for evento in raw_eventos:
                event_data = evento.get("event_data", {})
                formatted_start = None
                formatted_end = None
                if "scheduled_start" in event_data:
                    formatted_start = timezone.localtime(
                        parser.parse(event_data["scheduled_start"])
                    ).strftime("%Y-%m-%d %H:%M")
                if "scheduled_end" in event_data:
                    formatted_end = timezone.localtime(
                        parser.parse(event_data["scheduled_end"])
                    ).strftime("%Y-%m-%d %H:%M")

                eventos.append(
                    {
                        "event_type": tipo_evento_mapa.get(
                            evento["event_type"], evento["event_type"]
                        ),
                        "timestamp": timezone.localtime(
                            parser.parse(evento["timestamp"])
                        ).strftime("%Y-%m-%d %H:%M"),
                        "event_data": {
                            "concept": event_data.get("concept"),
                            "type": event_data.get("type"),
                            "scheduled_start": formatted_start,
                            "scheduled_end": formatted_end,
                            "documento": tipo_documento_mapa.get(event_data.get("document"), event_data.get("document")),
                            "file_size": event_data.get("file_size"),
                            "sheetName": event_data.get("sheetName"),
                            
                            "column": campo_bitacora_mapa.get(
                                event_data.get("column"), event_data.get("column")
                            ),
                            "value": event_data.get("value"),
                        },
                        "tipo": evento["event_type"],
                        "event_source": event_source_mapa.get(
                            evento["event_source"], evento["event_source"]
                        ),
                    }
                )

    context = {
        "documentos_forms": documentos_forms,
        "cliente_id": cliente_id,
        "eventos": eventos,
        'client_info': client_info,
    }

    return render(request, "expediente_cliente.html", context)


def base(request):
    return render(request, "base_admin.html")
 