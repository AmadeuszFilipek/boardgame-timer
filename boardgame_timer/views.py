from django.shortcuts import render, redirect
import random
import json
from django.http import JsonResponse
from boardgame_timer.session import Session
from boardgame_timer.timer import CountDownTimer, CountUpTimer, TimePerMoveTimer
from django.views.decorators.http import require_http_methods
import django.conf.global_settings as settings

supported_timers = {'CountDownTimer': CountDownTimer,
                    'CountUpTimer': CountUpTimer,
                    'TimePerMoveTimer': TimePerMoveTimer}
sessions = {}

def getFavicon(request):
   redirect(url=settings.STATIC_URL + 'static/icons/favicon.ico')

def index(request):

   return render(request, 'index.html')

def getSession(request, session):

   if session in sessions:
      return JsonResponse(sessions[session].to_dict())
   else:
      return JsonResponse({'status': 'error'})

def getSessionAndIndex(request, session):
   if session in sessions:
      context = {}
      context['session'] = json.dumps(sessions[session].to_dict())
      return render(request, 'index.html', context)
   else:
      return redirect(index)

def createSession(request):
   if request.method == "POST":

      inc_data = json.loads(request.body)
      new_session_name = inc_data["slug"]
      if new_session_name in sessions:
         return JsonResponse({'status': 'error', 'message': 'Session name is currently taken.'})
      else:
         timer_name = inc_data["timer"]
         auto_pass = inc_data["autoPass"]
         seconds = inc_data["seconds"]

         if timer_name in supported_timers:
            timer_class = supported_timers[timer_name] 
            sessions[new_session_name] = Session(
               new_session_name, timer_class, seconds, auto_pass)
            return JsonResponse({'status': 'ok'})

   else:
      return JsonResponse({'status': 'error'})

def addPlayer(request, session, player):
   if request.method == "POST":
      if session in sessions:
         if player in sessions[session].players:
            return JsonResponse({'status': 'error', 'message': "Player already exists."})
         else:      
            sessions[session].addPlayer(player)

            return JsonResponse({'status': 'ok'})

   return JsonResponse({'status': 'error'})

def togglePlayer(request, session, player):
   if request.method == "POST":
      if session in sessions:
         if player in sessions[session].players:

            sessions[session].toggle(player)
            return JsonResponse({'status': 'ok'})
         else:      
            return JsonResponse({'status': 'error'})

   return JsonResponse({'status': 'error'})

def movePlayer(request, session, player, placement):
   if request.method == "POST":
      if session in sessions:
         if player in sessions[session].players:
            sessions[session].movePlayer(player, placement)
            return JsonResponse({'status': 'ok'})

   return JsonResponse({'status': 'error'})

def shufflePlayers(request, session):
   if session in sessions:
      sessions[session].shuffle()
      return JsonResponse({'status': 'ok'})
   else:
      return JsonResponse({'status': 'error'})

def nextPlayer(request, session):
   if session in sessions:
      sessions[session].nextPlayer()
      return JsonResponse(sessions[session].to_dict())
   else:
      return JsonResponse({'status': 'error'})

def previousPlayer(request, session):
   if session in sessions:
      sessions[session].previousPlayer()
      return JsonResponse(sessions[session].to_dict())
   else:
      return JsonResponse({'status': 'error'})

def start(request, session):
   if request.method == "POST":
      if session in sessions:
         sessions[session].start()
         return JsonResponse({'status': 'ok'})
   
   return JsonResponse({'status': 'error'})

def stop(request, session):
   if request.method == "POST":
      if session in sessions:
         sessions[session].stop()
         return JsonResponse({'status': 'ok'})
   
   return JsonResponse({'status': 'error'})

def restart(request, session):
   if request.method == "POST":
      if session in sessions:
         sessions[session].restart()
         return JsonResponse({'status': 'ok'})
   
   return JsonResponse({'status': 'error'})



