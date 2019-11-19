from itertools import count
import time

class Session:

   iterator = count()

   def __init__(self, slug):
      self.slug = slug
      self.id = self.iterator.__next__()
      self.version = time.time()
      self.players = {}

   def addPlayer(self, name, timer):
      self.players[name] = Player(name, timer)

   def to_dict(self):
      timestamp = time.time()
      players = {p.name: p.to_dict() for p in self.players.values()}
      output = {
         'slug': self.slug,
         'id': self.id,
         'version': timestamp,
         'players': players
      }
   
      return output

class Player:

   iterator = count()

   def __init__(self, name, timer):
      self.name = name
      self.timer = timer
      self.id = self.iterator.__next__()
   
   def to_dict(self):
      output = {
         'name': self.name,
         'id': self.id,
         'time': self.timer.time()
      }
      return output  

class CountDownTimer:

   def __init__(self, total_time):
      self.remaining_time = total_time # in seconds
      self.is_running = False

   def start(self):
      self.is_running = True
      self.start_time = time.time()
   
   def stop(self):
      self.is_running = False
   
   def time(self):
      if self.is_running:
         elapsed_time = time.time() - start_time
         self.start_time = time.time()
         self.remaining_time -= elapsed_time
         if self.remaining_time < 0:
            self.remaining_time = 0
            self.is_running = False
         return self.remaining_time
      else:
         return self.remaining_time
