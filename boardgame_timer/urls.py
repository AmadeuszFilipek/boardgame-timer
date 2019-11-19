
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('api/sessions', views.createSession, name='createSession'),
    path('sessions/<slug:session>', views.getSession, name='getSession')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
