from django.urls import path
from . import views

urlpatterns = [
    path("login", views.admin_login, name="admin_login"),
    path("crear-admin/", views.create_admin, name="create_admin"),
    path("registrar/cliente", views.create_client, name="create_client"),
    path("search-client/", views.search_client, name="search_client"),
    path("client-details/<int:user_id>/", views.client_details, name="client_details"),
    path("base", views.base, name="base")
]
