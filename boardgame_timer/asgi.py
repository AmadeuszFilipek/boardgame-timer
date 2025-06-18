import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import boardgame_timer.routing # Will be created next

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boardgame_timer.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            boardgame_timer.routing.websocket_urlpatterns
        )
    ),
})
