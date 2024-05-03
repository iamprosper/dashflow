from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("ex", views.process_csv, name="process"),
    path("upload/", views.upload_file, name="upload"),
    path("success/", views.upload_success, name="success"),
]