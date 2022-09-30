from django.urls import re_path
from django.conf.urls import url

from . import consumers

# USE OF ws/ to separate out our ws URIs, like rest use of api/
websocket_urlpatterns = [
    url(r'^ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatConsumer.as_asgi())
]
