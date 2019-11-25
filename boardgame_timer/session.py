from itertools import count, cycle
import time
import random

class Session:

   counter = count()

   def __init__(self, slug, timer, seconds, auto_pass):
      self.slug = slug
      self.id = self.counter.__next__()
      self.version = time.time()
      self.timer = timer
      self.seconds = seconds
      self.auto_pass = auto_pass

      self.player_counter = count()
      self.players = {}
      self.active_player = None
      self.any_timer_active = False

   def addPlayer(self, name):
      timer = self.timer(self.seconds)
      self.players[name] = Player(name, timer, counter=self.player_counter)
      if self.active_player is None:
         self.active_player = name

   def is_state_to_be_changed(self):
      if not self.auto_pass:
         return False

      if self.any_timer_active and self.players[self.active_player].measure() == 0:
         return True
   
   def to_dict(self):
      timestamp = time.time()
      
      if self.is_state_to_be_changed():
         self.nextPlayer()

      players = [p.to_dict() for p in self.players.values()]
      players.sort(key=lambda p: p['id'])

      output = {
         'slug': self.slug,
         'id': self.id,
         'type': self.timer().__str__(),
         'version': timestamp,
         'players': players,
         'active': self.any_timer_active,
         'activePlayer': self.active_player
      }
   
      return output

   def restart(self):

      for name in self.players:
         timer = self.timer(self.seconds)
         self.players[name] = Player(name, timer, id=self.players[name].id)
      self.any_timer_active = False

   def shuffle(self):
      player_ids = [p.id for p in self.players.values()]
      
      for i in range(5):
         random.shuffle(player_ids)
      
      for i, player in zip(player_ids, self.players.values()):
         player.id = i 

   def toggle(self, player):
      if player == self.active_player:
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

      old_id = self.players[self.active_player].id
      players_by_id = {p.id: p for p in self.players.values()}
      
      if old_id >= len(self.players) - 1:
         new_id = 0
      else:
         new_id = old_id + 1
      
      players_by_id[old_id].stop()
      players_by_id[new_id].start()
      self.active_player = players_by_id[new_id].name

   def previousPlayer(self):
      if not self.any_timer_active:
         return
      
      old_id = self.players[self.active_player].id
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
      if self.active_player is None:
         return

      self.players[self.active_player].start()
      self.any_timer_active = True
   
   def stop(self):
      if not self.any_timer_active:
          return
      
      self.players[self.active_player].stop()
      self.any_timer_active = False


class Player:

   counter = count()

   def __init__(self, name, timer, counter=count(), id=None):
      self.name = name
      self.timer = timer
      if id is None:
         self.id = counter.__next__()
      else:
         self.id = id
      
   def measure(self):
      return self.timer.time()

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