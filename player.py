import numpy as np
import random
from projectile import projectile 
from entity import entity

class player(entity):
  def __init__(self, team, game, pos = np.array([0,0]), speed=10, size=20):
    entity.__init__(self, team, game, pos, 20, 10)

  def update(self, delta_time, game_instance):
    self.choose_action(game_instance)
    self.take_action(delta_time)

  def choose_action(self, game_instance):
    dx = 0
    dy = 0
    
    if game_instance.player_input['S']:
      dy+=1
    if game_instance.player_input['W']:
      dy-=1
    if game_instance.player_input['D']:
      dx+=1
    if game_instance.player_input['A']:
      dx-=1
    temp = np.array([dx, dy], dtype="float32")
    if dx != 0 or dy != 0:
      temp/=np.linalg.norm(temp)
    self.cur_action = temp

    if game_instance.clicked==True:
      print(game_instance.mouse_pos)
      game_instance.objects.append(projectile(self.team,self.game,np.copy(self.pos),20,np.copy(self.cur_action), 10))

    return self.cur_action

  def take_action(self, delta_time):
    self.pos += self.cur_action * self.speed * delta_time

  def destroy(self):
    self.destroyed = True
