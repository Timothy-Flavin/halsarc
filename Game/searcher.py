import numpy as np
from entity import entity
from controllers import player_controller
import math

class searcher(entity):
  # Speed is how many times per frame the agent can move
  def __init__(self, agent_blueprint, game):
    entity.__init__(self, "green", game, np.array([200,200],dtype=np.float32), 50, 5)
    self.name = agent_blueprint["name"]
    self.view_range = agent_blueprint["view_range"]
    self.speed = float(agent_blueprint["speed"])
    self.active_time = int(agent_blueprint["active_time"]*100)
    print(self.active_time)
    self.time_active = 0
    self.grounded = agent_blueprint["grounded"]
    self.color = agent_blueprint["color"]
    self.tile_names = []
    self.speeds = {}
    self.visibilities = {}
    self.controller = player_controller(self)
    self.speed_multiplier = 1.0
    self.tile_num = 0
    self.effective_view_range = 1.0
    #print(list(agent_blueprint["speeds"].keys()))
    for k in list(agent_blueprint["speeds"].keys()):
      self.speeds[k] = agent_blueprint["speeds"][k]
      self.tile_names.append(k)
    for k in list(agent_blueprint["visibilities"].keys()):
      self.visibilities[k] = agent_blueprint["visibilities"][k]
  def get_tile_from_pos(self, pos, game_instance):
    col = int(math.floor(self.pos[0]/game_instance.screen.get_width()*game_instance.tile_map.shape[1]))
    row = int(math.floor(self.pos[1]/game_instance.screen.get_height()*game_instance.tile_map.shape[0]))
    return row, col

  def update(self, delta_time, game_instance):
    row, col = self.get_tile_from_pos(self.pos, game_instance)
    self.tile = game_instance.tiles[game_instance.tile_map[row,col]]
    print(self.time_active)
    self.time_active+=1
    if self.time_active>self.active_time:
      self.destroy()
      return
    #print(game_instance.tiles)
    #print(game_instance.tile_map)
    #input()
    self.altitude = self.tile['altitude']
    self.speed_multiplier = self.speeds[self.tile['name']]
    self.visibility_multiplier = self.visibilities[self.tile['name']]
    if not self.grounded:
      self.speed_multiplier = 1.0
      self.altitude = 1.0
    self.effective_view_range = self.view_range*self.altitude*game_instance.tile_width
    #print(row,col,self.speed_multiplier)
    self.controller.choose_action(game_instance)
    self.controller.take_action(delta_time)



  def set_controller(self, controller):
    self.controller = controller 

  def render(self, color, screen, debug=False):
    print(self.size)
    self.game.draw.circle(screen, color, center=(float(self.pos[0]), float(self.pos[1])), radius=self.size)
    h = max(int(self.size/5),2)
    trect = self.game.Rect(self.pos[0]-self.size,self.pos[1]-self.size-h, int(self.size*2-self.size*2*self.time_active/self.active_time),h)
    self.game.draw.rect(screen, (0,100,250), trect)
  def debug_render(self, color, screen, debug=False):
    self.game.draw.circle(screen, (250,250,250,100), center=(float(self.pos[0]), float(self.pos[1])), radius=self.effective_view_range)
  