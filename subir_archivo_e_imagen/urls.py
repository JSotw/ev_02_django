from django.urls import path
from django.urls import path
from subir_archivo_e_imagen import views


urlpatterns = [
    path('', views.user_login, name='login'),
    path("upload/", views.upload, name="upload"),
    path("lista-de-registros/", views.listarData, name="listarData"),
    path("delete/<str:folder>/<str:object>", views.delete, name="delete"),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
]
