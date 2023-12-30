from django import forms
from clientes.models import CustomUser, Documento
import uuid
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

class AdminLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={
        'autofocus': True,
        'class': 'login-input',
        'placeholder': 'Correo electrónico'
    }))
    password = forms.CharField(label ='Contraseña',widget=forms.PasswordInput(attrs={
        'class': 'login-input',
        'placeholder': 'Contraseña'
    }))

class AdminRegistrationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['nombre', 'email', 'phone_number', 'is_admin', 'password']


    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.username = self.generate_unique_username()  # Marcamos automáticamente al usuario como administrador
        if commit:
            user.save()
        return user
    
class ClienteRegistrationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['nombre', 'email', 'phone_number']  # Cambiado de 'username' a 'nombre'

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['estado']