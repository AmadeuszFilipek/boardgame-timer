
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('favicon.ico', views.getFavicon),
    path('sessions/<str:session>', views.getSessionAndIndex, name='getSessionAndIndex'),
    
    path('api/sessions', views.createSession, name='createSession'),
    path('api/sessions/<str:session>', views.getSession, name='getSession'),
    
    path('api/sessions/<str:session>/start', views.start),
    path('api/sessions/<str:session>/stop', views.stop),
    path('api/sessions/<str:session>/next', views.nextPlayer),
    path('api/sessions/<str:session>/previous', views.previousPlayer),
    path('api/sessions/<str:session>/shuffle', views.shufflePlayers),
    path('api/sessions/<str:session>/restart', views.restart),
    
    
    path('api/sessions/<str:session>/<str:player>', views.addPlayer),
    path('api/sessions/<str:session>/<str:player>/toggle', views.togglePlayer),
    
]
