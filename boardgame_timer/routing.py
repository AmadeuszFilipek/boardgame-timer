from django.urls import re_path
from . import consumers # Will be created next

websocket_urlpatterns = [
    re_path(r'ws/session/(?P<session_slug>[^/]+)/$', consumers.SessionConsumer.as_asgi()),
]
