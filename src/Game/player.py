import numpy as np
import random
from entity import entity
from projectile import projectile

class player(entity):
  def __init__(self, team, game, pos = np.array([0,0]), speed=10, size=20, entity_type="combatant"):
    entity.__init__(self, team, game, pos, speed, size, "player")
    self.cooldown = 0.2
    self.cd_left = 0

  def update(self, delta_time, game_instance):
    self.cd_left-=delta_time
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

    if game_instance.clicked==True and self.cd_left<0:
      self.cd_left = self.cooldown
      print(game_instance.mouse_pos)
      proj_dir = (game_instance.mouse_pos-self.pos)
      proj_dir /= np.linalg.norm(proj_dir)
      print(proj_dir)
      game_instance.add_entity(projectile(self.team,self.game,np.copy(self.pos),40,np.copy( proj_dir ), 10))

    return self.cur_action

  def take_action(self, delta_time):
    #print(f"Player {self.cur_action, self.speed, delta_time}")
    self.pos += self.cur_action * self.speed * delta_time

  def destroy(self):
    self.destroyed = True
