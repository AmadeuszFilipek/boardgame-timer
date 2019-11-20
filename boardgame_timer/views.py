from django.shortcuts import render, redirect
import random
import json
from django.http import JsonResponse, HttpResponseNotFound
from boardgame_timer.session import Session, CountDownTimer

sessions = {}

def index(request):

   return render(request, 'index.html')

def getSessionAndIndex(request, session):
   if session in sessions:
      context = {}
      context['session'] = sessions[session].to_dict()
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
            print('Adding player')
            print(sessions[session].to_dict())
            return JsonResponse({'status': 'ok'})

   return HttpResponseNotFound()

def togglePlayer(request, session, player):
   if request.method == "POST":
      if session in sessions:
         if player in sessions[session].players:
            print('toggling')
            sessions[session].toggle(player)
            return JsonResponse({'status': 'ok'})
         else:      
            return JsonResponse({'status': 'error'})

   return HttpResponseNotFound()

def getSession(request, session):

   if session in sessions:
      return JsonResponse(sessions[session].to_dict())
   else:
      return HttpResponseNotFound()

def shufflePlayers(request, session):
   if session in sessions:
      sessions[session].players.shuffle()
      return JsonResponse(sessions[session].to_dict())
   else:
      return HttpResponseNotFound()

def nextPlayer(request):
   if session in sessions:
      sessions[session].players.next()
      return JsonResponse(sessions[session].to_dict())
   else:
      return HttpResponseNotFound()

def previousPlayer(request):
   if session in sessions:
      sessions[session].players.previous()
      return JsonResponse(sessions[session].to_dict())
   else:
      return HttpResponseNotFound()

def replacePlayer(request, session, player, place):
   if session in sessions and player in sessions[session].players:
      sessions[session].players[player].move(place)
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





