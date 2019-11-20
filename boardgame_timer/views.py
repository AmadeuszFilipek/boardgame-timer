from django.shortcuts import render, redirect
import random
import json
from django.http import JsonResponse, HttpResponseNotFound
from boardgame_timer.session import Session, CountDownTimer

sessions = {}

def index(request):

   return render(request, 'index.html')

def getSession(request, session):

   if session in sessions:
      return JsonResponse(sessions[session].to_dict())
   else:
      return HttpResponseNotFound()

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
      new_session_name = inc_data["session"]["slug"]
      if new_session_name in sessions:
         return getSessionAndIndex(request, new_session_name)
      else:
         sessions[new_session_name] = Session(new_session_name)
         return JsonResponse({'status': 'ok'})

   else:
      return JsonResponse({'status': 'error'})

def addPlayer(request, session, player):
   if request.method == "POST":
      if session in sessions:
         if player in sessions[session].players:
            return JsonResponse({'status': 'error'})
         else:      
            timer = CountDownTimer(10 * 60)
            sessions[session].addPlayer(player, timer)

            return JsonResponse({'status': 'ok'})

   return HttpResponseNotFound()

def togglePlayer(request, session, player):
   if request.method == "POST":
      if session in sessions:
         if player in sessions[session].players:

            sessions[session].toggle(player)
            return JsonResponse({'status': 'ok'})
         else:      
            return JsonResponse({'status': 'error'})

   return HttpResponseNotFound()

def shufflePlayers(request, session):
   if session in sessions:
      sessions[session].shuffle()
      return JsonResponse({'status': 'ok'})
   else:
      return HttpResponseNotFound()

def nextPlayer(request, session):
   if session in sessions:
      sessions[session].nextPlayer()
      return JsonResponse(sessions[session].to_dict())
   else:
      return HttpResponseNotFound()

def previousPlayer(request, session):
   if session in sessions:
      sessions[session].previousPlayer()
      return JsonResponse(sessions[session].to_dict())
   else:
      return HttpResponseNotFound()

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

def replacePlayer(request, session, player, place):
   # not implemented
   pass





