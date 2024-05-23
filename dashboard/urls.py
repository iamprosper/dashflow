from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("upload/", views.upload_file, name="upload"),
    path("success/", views.upload_success, name="success"),
    path("process/", views.process_file, name="process_file"),
    path("display/", views.lazy_display, name="lazy"),
    path("processd/", views.process_data, name="process_data"),
    path("fill/", views.fill_db, name='fill'),
]