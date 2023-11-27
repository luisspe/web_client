from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Documento, Notificacion, UserNotificationSettings

# Diccionario para almacenar el estado anterior de los documentos
estado_anterior_documento = {}

@receiver(pre_save, sender=Documento)
def capturar_estado_anterior(sender, instance, **kwargs):
    if instance.id:
        estado_anterior = Documento.objects.get(id=instance.id).estado
        estado_anterior_documento[instance.id] = estado_anterior

@receiver(post_save, sender=Documento)
def crear_notificacion_por_cambio_estado(sender, instance, created, **kwargs):
    if created:
        return  # No hacer nada si el documento es nuevo

    estado_anterior = estado_anterior_documento.get(instance.id)
    if estado_anterior and estado_anterior != instance.estado:
        crear_notificacion_documento(instance)

    # Limpiar el diccionario para el documento actual
    if instance.id in estado_anterior_documento:
        del estado_anterior_documento[instance.id]

def crear_notificacion_documento(documento):
    user_notification_settings = UserNotificationSettings.objects.get(user=documento.usuario)
    if user_notification_settings.receive_notifications and user_notification_settings.notify_document_status:
        tipo_documento_legible = documento.get_tipo_documento_display()  # Obtener la versión legible del tipo de documento
        Notificacion.objects.create(
            usuario=documento.usuario,
            mensaje=f"El estado de tu documento '{tipo_documento_legible}' ha cambiado a '{documento.estado}'."
        )