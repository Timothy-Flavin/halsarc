import numpy as np
import projectile

class player_controller():
  def __init__(self, parent):
    self.parent = parent
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

    return self.cur_action

  def take_action(self, delta_time):
    self.parent.pos += self.cur_action * self.parent.speed * self.parent.speed_multiplier
