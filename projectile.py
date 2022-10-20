from logging import exception
import numpy as np
from entity import entity

class projectile(entity):
  def __init__(self, team, game, pos = np.array([0,0]), speed=10, dir=np.array([0,0]), damage=10):
    entity.__init__(self, team, game, pos, speed, 4)
    self.dir = dir
    self.damage=damage
  
  def update(self, delta_time, game_instance):
    self.pos+=self.speed*self.dir*delta_time
    self.check_collision(game_instance)

  def check_collision(self, game_instance):
    for obj in game_instance.objects:
      if obj.team != self.team and obj.combat is not None and np.sum(np.square(obj.pos-self.pos)) < pow(obj.size+self.size,2):
        obj.combat.take_hit(self.damage)
        self.destroy()
      if obj.team != self.team and np.sum(np.square(obj.pos-self.pos)) < pow(obj.size+self.size,2):
        self.destroy()

  def choose_action(self, game_instance):
    exception("Projectiles do not choose actions but choose_action was called on this projectile")

  def take_action(self, delta_time):
    exception("Projectiles do not take actions but take_action was called on this projectile")

