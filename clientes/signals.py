from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Documento, Notificacion, UserNotificationSettings

@receiver(post_save, sender=Documento)
def crear_notificacion_por_cambio_estado(sender, instance, **kwargs):
    if kwargs.get('created', False):
        return  # No hacer nada si el documento es nuevo

    documento_anterior = Documento.objects.get(id=instance.id)
    if documento_anterior.estado != instance.estado:
        crear_notificacion_documento(instance)

def crear_notificacion_documento(documento):
    user_notification_settings = UserNotificationSettings.objects.get(user=documento.usuario)
    if user_notification_settings.receive_notifications and user_notification_settings.notify_document_status:
        Notificacion.objects.create(
            usuario=documento.usuario,
            mensaje=f"El estado de tu documento '{documento.tipo_documento}' ha cambiado a '{documento.estado}'."
        )
