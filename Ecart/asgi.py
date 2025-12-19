# project/asgi.py
import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import UserApp.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Ecart.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(UserApp.routing.websocket_urlpatterns)
    )
})
