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
def search_client(request):
    query = request.GET.get('q', '')
    clients = CustomUser.objects.filter(nombre__icontains=query) if query else []
    return render(request, 'search_client.html', {'clients': clients})

def expediente_cliente(request, cliente_id):
    documentos = Documento.objects.filter(usuario_id=cliente_id)
    
    if request.method == 'POST':
        documento_id = request.POST.get('doc_id')
        documento = get_object_or_404(Documento, pk=documento_id)
        form = DocumentoForm(request.POST, instance=documento, prefix='doc_'+str(documento_id))
        
        if form.is_valid():
            form.save()
            return redirect('expediente_cliente', cliente_id=cliente_id)
    else:
        documentos_forms = [(documento, DocumentoForm(instance=documento, prefix='doc_'+str(documento.id)))
                            for documento in documentos]
    
    context = {
        'documentos_forms': documentos_forms,
        'cliente_id': cliente_id,
    }
    return render(request, 'expediente_cliente.html', context)

def base(request):
    return render(request, 'base_admin.html')