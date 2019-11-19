from django.shortcuts import render
import random
import json
from django.http import JsonResponse

sessions = {}
class Session: pass

def index(request):

   return render(request, 'index.html')

def createSession(request):
   if request.method == "POST":

      inc_data = json.loads(request.body)
      new_session_name = inc_data["session"]["slug"]
      if new_session_name in sessions:
         return JsonResponse({'status': 'error'})
      else:
         sessions[new_session_name] = Session(new_session_name)
         return JsonResponse({'status': 'created'})

   else:
      return JsonResponse({'status': 'error'})

def getSession(request, session):

   if session in sessions:
      return JsonResponse(sessions[session].to_dict())
   else:
      return JsonResponse({'status': 'error'})

def shufflePlayers(request):
   pass

def nextPlayer(request):
   pass

def previousPlayer(request):
   pass

def togglePlayer(request):
   pass

def switchPlayers(request):
   pass

def addPlayer(request):
   # add a player to the ongoing session
   # if request.method == "POST":
   pass

