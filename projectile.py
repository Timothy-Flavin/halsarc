from logging import exception
import numpy as np
from Goblins.entity import entity

class projectile(entity):
  def __init__(self, team, game, pos = np.array([0,0]), speed=10, dir=np.array([0,0]), damage=10):
    entity.__init__(self, team, game, pos, speed, 4)
    self.dir = dir
    self.damage=damage
  
  def update(self, delta_time, game_instance):
    self.pos+=self.speed*self.dir*delta_time

  def check_collision(self, game_instance):
    for obj in game_instance.objects:
      if obj.team != self.team and obj.combat is not None:
        obj.combat.takeHit(self.damage)
      self.destroy()

  def choose_action(self, game_instance):
    exception("Projectiles do not choose actions but choose_action was called on this projectile")

  def take_action(self, delta_time):
    exception("Projectiles do not take actions but take_action was called on this projectile")

