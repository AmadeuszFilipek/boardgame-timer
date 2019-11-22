import time

class AbstractTimer:

   def __init__(self):
      self.is_running = False

   def start(self):
      self.is_running = True
      self.start_time = time.time()
   
   def stop(self):
      self.is_running = False

   def __str__(self):
      return type(self).__name__

class CountDownTimer(AbstractTimer):

   def __init__(self, total_time=1):
      AbstractTimer.__init__(self)
      self.total_time = total_time
      self.remaining_time = total_time # in seconds
   
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
      if self.total_time == 0:
         return 0
      return self.time() / self.total_time

class CountUpTimer(AbstractTimer):

   def __init__(self, *args, **kwargs):
      AbstractTimer.__init__(self)
      self.total_time = 0

   def time(self):
      if self.is_running:
         elapsed_time = time.time() - self.start_time
         self.start_time = time.time()
         self.total_time += elapsed_time
            
      return self.total_time
   
   def ratio(self):
      return 0

class TimePerMoveTimer(CountDownTimer):
   
   def start(self):
      self.remaining_time = self.total_time
      self.is_running = True
      self.start_time = time.time()

