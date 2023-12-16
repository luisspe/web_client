from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    
    email = models.EmailField(('email address'), unique=True)  # Asegúrate de que el email sea único
    is_admin = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    nombre = models.CharField(max_length=100, unique=True)

        # Elimina el username de los campos requeridos

    def __str__(self):
        return self.email

class Documento(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('INE_FRENTE', 'Frente de INE'),
        ('INE_REVERSO', 'Reverso de INE'),
        ('CONSTANCIA_FISCAL', 'Constancia fiscal'),
        ('COMPROBANTE_DOMICILIO', 'Comprobante domicilio'),
        ('COMPROBANTE_INGRESOS', 'Comprobante ingresos'),
        ('CURP', 'curp'),

        
        
    ]

    ESTADOS = [
        ('SUBIDO', 'subido'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    archivo = models.FileField(upload_to='documentos/')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo_documento = models.CharField(max_length=100, choices=TIPO_DOCUMENTO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="SUBIDO")
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.usuario} {self.tipo_documento} {self.estado}'
    

#NOTIFICACIONES DEL USUARIO
class UserNotificationSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    receive_notifications = models.BooleanField(default=True)
    notify_document_status = models.BooleanField(default=False)
    notify_appointment_confirmation = models.BooleanField(default=False)
    notify_appointment_reminder = models.BooleanField(default=False)
    credit_response = models.BooleanField(default=True)
    plates_status = models.BooleanField(default=True)
    unit_details = models.BooleanField(default=True)
    payments_confirmations = models.BooleanField(default=True)

    def __str__(self):
        return f'Notificaciones para {self.user.username}'
    

class Notificacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)

    def __str__(self):
        return f"Notificación para {self.usuario.username}: {self.mensaje}"
    


