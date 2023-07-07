import numpy as np
import random
import projectile

class player_controller():
  def __init__(self, parent):
    self.cur_action=np.zeros(2)
  def choose_action(self, state, game_instance):
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

class basic_controller():
  def __init__(self, parent):
    self.parent = parent
    self.cur_action=np.zeros(2)
  def choose_action(self, state, game_instance):
    dx=random.randint(-1,1)
    dy=random.randint(-1,1)
    temp = np.array([dx, dy], dtype="float32")
    if dx != 0 or dy != 0:
      temp/=np.linalg.norm(temp)
    self.cur_action = temp
    return self.cur_action

class agent_controller():
  def __init__(self, parent):
    self.parent = parent
    self.cur_action=np.zeros(2)
  def choose_action(self, game_instance):
    dx=random.randint(-1,1)
    dy=random.randint(-1,1)
    temp = np.array([dx, dy], dtype="float32")
    if dx != 0 or dy != 0:
      temp/=np.linalg.norm(temp)
    self.cur_action = temp
    return self.cur_action
