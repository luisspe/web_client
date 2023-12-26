from django import forms
from .models import CustomUser
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
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'login-input',
        'placeholder': 'Contraseña'
    }))
    

class ClienteRegistrationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['nombre', 'email', 'phone_number']  # Cambiado de 'username' a 'nombre'

class ClienteLoginForm(forms.Form):
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15)


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
    
    def generate_unique_username(self):
        # Genera un username único
        while True:
            username = uuid.uuid4().hex[:6].lower()
            if not CustomUser.objects.filter(username=username).exists():
                return username

    
    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        if CustomUser.objects.filter(nombre=nombre).exists():
            raise forms.ValidationError("Este nombre ya está en usooooo.")
        return nombre