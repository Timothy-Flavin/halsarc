import numpy as np
import random
from projectile import projectile 
from entity import entity

class deepq(entity):
  def __init__(self, team, game, pos = np.array([0,0]), speed=10, size=20):
    entity.__init__(self, team, game, pos, 20, 10)
    self.cooldown = 0.2
    self.cd_left = 0

  def update(self, delta_time, game_instance):
    self.cd_left-=delta_time
    self.choose_action(game_instance)
    self.take_action(delta_time)

  def choose_action(self, game_instance):
    dx = 0
    dy = 0

    if game_instance.clicked==True and self.cd_left<0:
      self.cd_left = self.cooldown
      proj_dir = (game_instance.mouse_pos-self.pos)
      proj_dir /= np.linalg.norm(proj_dir)
      game_instance.objects.append(projectile(self.team,self.game,np.copy(self.pos),40,np.copy( proj_dir ), 10))

    return self.cur_action

  def take_action(self, delta_time):
    self.pos += self.cur_action * self.speed * delta_time

  def destroy(self):
    self.destroyed = True
