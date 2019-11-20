from itertools import count, cycle
import time

class Session:

   iterator = count()

   def __init__(self, slug):
      self.slug = slug
      self.id = self.iterator.__next__()
      self.version = time.time()
      self.players = {}
      self.active_player = None
      self.any_timer_active = False

   def addPlayer(self, name, timer):
      self.players[name] = Player(name, timer)
      if self.active_player is None:
         self.active_player = name

   def to_dict(self):
      timestamp = time.time()
      players = [p.to_dict() for p in self.players.values()]
      players.sort(key=lambda p: p['id'])

      output = {
         'slug': self.slug,
         'id': self.id,
         'version': timestamp,
         'players': players,
         'active': self.any_timer_active,
         'activePlayer': self.active_player
      }
   
      return output

   def checkActive(self):
      pass

   def toggle(self, player):
      if player is self.active_player:
         
         self.players[self.active_player].toggle()
         self.any_timer_active = not self.any_timer_active
      else:
         self.players[self.active_player].stop()
         self.players[player].start()
         self.active_player = player
         self.any_timer_active = True
   
   def nextPlayer(self):
      if not self.any_timer_active:
         return

      old_id = self.players[self.active_player]
      players_by_id = {p.id: p for p in self.players.values()}
      
      if old_id >= len(self.players):
         new_id = 0
      else:
         new_id = old_id + 1
      
      players_by_id[old_id].stop()
      players_by_id[new_id].start()
      self.active_player = players_by_id[new_id].name

   def previousPlayer(self):
      if not self.any_timer_active:
         return

      old_id = self.players[self.active_player]
      players_by_id = {p.id: p for p in self.players.values()}
      
      if old_id <= 0:
         new_id = len(self.players) - 1
      else:
         new_id = old_id - 1
      
      players_by_id[old_id].stop()
      players_by_id[new_id].start()
      self.active_player = players_by_id[new_id].name

   def start(self):
      if self.any_timer_active:
         return

      self.players[self.active_player].start()
      self.any_timer_active = True
   
   def stop(self):
      if not self.any_timer_active:
          return
      
      self.players[self.active_player].stop()
      self.any_timer_active = False


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
         'time': self.timer.time(),
         'ratio': self.timer.ratio()
      }
      return output 
   
   def toggle(self):
      if self.timer.is_running:
         self.timer.stop()
      else:
         self.timer.start()

   def stop(self):
      self.timer.stop()

   def start(self):
      self.timer.start()

class CountDownTimer:

   def __init__(self, total_time):
      self.total_time = total_time
      self.remaining_time = total_time # in seconds
      self.is_running = False

   def start(self):
      self.is_running = True
      self.start_time = time.time()
   
   def stop(self):
      self.is_running = False
   
   def time(self):
      if self.is_running:
         elapsed_time = time.time() - self.start_time
         self.start_time = time.time()
         self.remaining_time -= elapsed_time
         if self.remaining_time < 0:
            self.remaining_time = 0
            self.is_running = False
            
      return self.remaining_time
   
   def ratio(self):
      return self.time() / self.total_time
