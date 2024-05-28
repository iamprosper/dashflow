"""
ASGI config for dfa project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from matplotlib import path
from dashboard.consumers import DataConsumer
from routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dfa.settings')

#application = get_asgi_application()
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # 'websocket': URLRouter([
    #     path('/ws/fill', DataConsumer.as_asgi())
    # ]),
    'websocket': URLRouter(websocket_urlpatterns)
})
