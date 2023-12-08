from django.urls import path
from . import views

urlpatterns = [
    path('login/cliente', views.cliente_login, name='cliente_login'),
    path('v2admin/registrar/cliente', views.create_client, name='create_client'),
    path('v2admin/login', views.admin_login, name='admin_login'),
    path('v2/dashboard/documentos', views.cliente_dashboard_documentos, name='cliente_dashboard'),
    path('upload', views.upload_file, name='upload_file'),
    path('v2/cliente_citas/', views.cliente_citas, name='cliente_citas'),
    path('logout', views.logout_view, name='logout'),
    path('crear-admin/', views.create_admin, name='create_admin'),
    path('settings/notifications', views.notification_settings, name='notification_settings'),
    path('eliminar-notificacion/<int:id_notificacion>', views.eliminar_notificacion, name='eliminar_notificacion'),
    path('v2/dashboard/comentarios', views.comentarios_y_sugerencias, name='comentarios_y_sugerencias'),
]
