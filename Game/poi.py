import numpy as np
from entity import entity
from controllers import player_controller
import math
import random

class person_of_interest(entity):
  # Speed is how many times per frame the agent can move
  def __init__(self, agent_blueprint, name, game):
    entity.__init__(self, "green", game, np.array([300,300],dtype=np.float32), 50, 5, entity_type="person_of_interest")
    #print("poi added")
    self.name = name
    self.hidden = True
    self.speed = float(agent_blueprint["speed"])
    self.active_time = int(agent_blueprint["active_time"]*100)
    #print(self.active_time)
    self.time_active = 0
    self.color = agent_blueprint["color"]
    self.tile_names = []
    self.speeds = {}
    self.speed_multiplier = 1.0
    self.tile_num = 0
    self.camo = agent_blueprint["camo"]
    for k in list(agent_blueprint["speeds"].keys()):
      self.speeds[k] = agent_blueprint["speeds"][k]
      self.tile_names.append(k)

  def update(self, delta_time, game_instance):
    #print("poi update")
    #print(f"screen: {game_instance.screen}, tilemap: {game_instance.tile_map}")
    row, col, self.tile = self.get_tile_from_pos(self.pos, game_instance)
    self.time_active+=1
    if self.time_active>self.active_time and self.hidden:
      self.destroy()
      return
    self.altitude = self.tile['altitude']
    self.speed_multiplier = self.speeds[self.tile['name']]
    dx=random.randint(-1,1)
    dy=random.randint(-1,1)
    if abs(dx)>0.001 or abs(dy)>0.001:
      temp = np.array([dx, dy], dtype="float32")
      temp/=np.linalg.norm(temp)
      self.cur_action = temp
      if self.hidden:
        self.take_action(0.01)
    return self.cur_action

  def take_action(self, delta_time):
    self.pos += self.cur_action * self.speed * self.speed_multiplier

  def render(self, color, screen, debug=False):
    #print(self.size)
    #print("poi render")
    if not self.hidden:
      self.game.draw.circle(screen, color, center=(float(self.pos[0]), float(self.pos[1])), radius=self.size)
      h = max(int(self.size/5),2)
      trect = self.game.Rect(self.pos[0]-self.size,self.pos[1]-self.size-h, int(self.size*2-self.size*2*self.time_active/self.active_time),h)
      self.game.draw.rect(screen, (0,100,250), trect)

  def debug_render(self, color, screen, debug=False):
    #print("debug render")
    self.game.draw.circle(screen, color, center=(float(self.pos[0]), float(self.pos[1])), radius=self.size)
    h = max(int(self.size/5),2)
    trect = self.game.Rect(self.pos[0]-self.size,self.pos[1]-self.size-h, int(self.size*2-self.size*2*self.time_active/self.active_time),h)
    self.game.draw.rect(screen, (0,100,250), trect)

  