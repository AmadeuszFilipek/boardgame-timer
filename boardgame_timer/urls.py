
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('favicon.ico', views.getFavicon),
    path('sessions/<slug:session>', views.getSessionAndIndex, name='getSessionAndIndex'),
    
    path('api/sessions', views.createSession, name='createSession'),
    path('api/sessions/<slug:session>', views.getSession, name='getSession'),
    
    path('api/sessions/<slug:session>/start', views.start),
    path('api/sessions/<slug:session>/stop', views.stop),
    path('api/sessions/<slug:session>/next', views.nextPlayer),
    path('api/sessions/<slug:session>/previous', views.previousPlayer),
    path('api/sessions/<slug:session>/shuffle', views.shufflePlayers),
    path('api/sessions/<slug:session>/restart', views.restart),
    
    
    path('api/sessions/<slug:session>/<slug:player>', views.addPlayer),
    path('api/sessions/<slug:session>/<slug:player>/toggle', views.togglePlayer),
    
]
