from django.urls import path
from . import views

urlpatterns = [

    path('', views.cliente_login, name='cliente_login'),
    path('login/cliente', views.cliente_login, name='cliente_login'),
    path('v2/dashboard/documentos', views.cliente_dashboard_documentos, name='cliente_dashboard'),
    path('upload', views.upload_file, name='upload_file'),
    path('v2/cliente_citas/', views.cliente_citas, name='cliente_citas'),
    path('logout', views.logout_view, name='logout'),
    path('v2/settings/notifications', views.notification_settings, name='notification_settings'),
    path('eliminar-notificacion/<int:id_notificacion>', views.marcar_leida_notificacion, name='eliminar_notificacion'),
    path('v2/dashboard/comentarios', views.comentarios_y_sugerencias, name='comentarios_y_sugerencias'),
    path('v2/notifications', views.notifications, name='notifications'),
    path('book_appointment/', views.book_appointment, name='book_appointment'),
   path('eliminar-notificacion/<int:notificacion_id>/', views.eliminar_notificacion, name='eliminar_notificacion'),
]
