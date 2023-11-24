from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Documento, UserNotificationSettings, Notificacion

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['nombre', 'email', 'is_admin', 'phone_number', 'is_staff']  # Añade 'nombre'
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('nombre', 'is_admin', 'phone_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('nombre', 'is_admin', 'phone_number')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Documento)
admin.site.register(UserNotificationSettings)
admin.site.register(Notificacion)