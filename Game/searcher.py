import numpy as np
from entity import entity
from controllers import player_controller
import math

class searcher(entity):
  # Speed is how many times per frame the agent can move
  def __init__(self, agent_blueprint, name, game):
    entity.__init__(self, "green", game, np.array([200,200],dtype=np.float32), 50, 5, entity_type="learnable_agent")
    self.name = name
    self.view_range = agent_blueprint["view_range"]
    self.speed = float(agent_blueprint["speed"])
    self.active_time = int(agent_blueprint["active_time"]*100)
    #print(self.active_time)
    self.time_active = 0
    self.grounded = agent_blueprint["grounded"]
    self.color = agent_blueprint["color"]
    self.tile_names = []
    self.speeds = {}
    self.visibilities = {}
    self.controller = player_controller(self)
    self.speed_multiplier = 1.0
    self.tile_num = 0
    self.effective_view_range = self.view_range
    #print(list(agent_blueprint["speeds"].keys()))
    for k in list(agent_blueprint["speeds"].keys()):
      self.speeds[k] = agent_blueprint["speeds"][k]
      self.tile_names.append(k)
    for k in list(agent_blueprint["visibilities"].keys()):
      self.visibilities[k] = agent_blueprint["visibilities"][k]

  def update(self, delta_time, game_instance):
    self.take_action(delta_time)
    self.pos[0] = max(min(self.pos[0],game_instance.screen.get_width()-0.01),0)
    self.pos[1] = max(min(self.pos[1],game_instance.screen.get_height()-0.01),0)
    row, col, self.tile = self.get_tile_from_pos(self.pos, game_instance)
    self.time_active+=1
    if self.time_active>self.active_time:
      self.destroy()
      return
    self.altitude = self.tile['altitude']
    self.speed_multiplier = self.speeds[self.tile['name']]
    self.visibility_multiplier = self.visibilities[self.tile['name']]
    if not self.grounded:
      self.speed_multiplier = 1.0
      self.altitude = 1.0
    self.effective_view_range = self.view_range*self.altitude*game_instance.tile_width
    for obj in game_instance.active_objects:
      
      if obj.entity_type == "person_of_interest" or obj.entity_type == "object_of_interest":
        #print(f"found poi {self.pos} {obj.pos} : {np.sqrt(np.sum(np.square(self.pos - obj.pos)))}")
        #r, c, tile = self.get_tile_from_pos(self.pos, game_instance)
        if np.sqrt(np.sum(np.square(self.pos - obj.pos))) < self.effective_view_range:
          if obj.hidden==True:
            game_instance.found(obj, self.id)
          obj.hidden = False

  def render(self, color, screen, debug=False):
    #print(self.size)
    self.game.draw.circle(screen, color, center=(float(self.pos[0]), float(self.pos[1])), radius=self.size)
    h = max(int(self.size/5),2)
    trect = self.game.Rect(self.pos[0]-self.size,self.pos[1]-self.size-h, int(self.size*2-self.size*2*self.time_active/self.active_time),h)
    self.game.draw.rect(screen, (0,100,250), trect)
  def debug_render(self, color, screen, debug=False):
    self.game.draw.circle(screen, (250,250,250,100), center=(float(self.pos[0]), float(self.pos[1])), radius=self.effective_view_range)
  