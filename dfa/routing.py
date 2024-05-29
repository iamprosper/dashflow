from django.urls import path, re_path
from dashboard.consumers import DataConsumer

websocket_urlpatterns = [
    re_path(r'dashboard/ws/fill/', DataConsumer.as_asgi()),
]