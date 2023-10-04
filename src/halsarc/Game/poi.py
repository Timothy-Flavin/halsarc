import numpy as np
from halsarc.Game.entity import entity
from halsarc.Game.controllers import player_controller
import math
import random

class person_of_interest(entity):
  # Speed is how many times per frame the agent can move
  def __init__(self, poi_blueprint, name, p_num, game):
    entity.__init__(self, game, np.array([300,300],dtype=np.float32), 50, 5, entity_type="person_of_interest")
    self.name = name
    self.found_reward = 1
    self.saved_reward = 1
    self.hidden = True
    self.saved = False
    self.p_num = p_num
    self.dir = random.random()*2*math.pi
    self.turn_bias = random.random()/4 - 1/8

    self.speed = float(poi_blueprint["speed"])
    self.active_time = int(poi_blueprint["active_time"]*100)
    self.time_active = 0
    self.color = poi_blueprint["color"]
    self.tile_names = []
    self.speeds = {}
    self.speed_multiplier = 1.0
    self.tile_num = 0
    self.camo = poi_blueprint["camo"]
    self.track_prob = poi_blueprint["track_prob"]
    self.drop_prob = poi_blueprint["drop_prob"]
    self.save_by = poi_blueprint["save_by"]
    self.v = np.zeros(2)
    for k in list(poi_blueprint["speeds"].keys()):
      self.speeds[k] = poi_blueprint["speeds"][k]
      self.tile_names.append(k)

  def sign_of_life(self, game_instance):
    ep1 = random.random()
    if ep1 < self.track_prob:
      #print(f"ep: {ep1}, track_prob: {self.track_prob}, {ep1 < self.track_prob}")
      game_instance.leave_tracks(self)
    ep1 = random.random()
    if ep1 < self.drop_prob:
      #print(f"ep: {ep1}, clothes_prob: {self.drop_prob}, {ep1 < self.drop_prob}")
      game_instance.leave_clothes(self)

  def update(self, delta_time, game_instance):
    #print("poi update")
    #print(f"screen: {game_instance.screen}, tilemap: {game_instance.tile_map}")
    #self.sign_of_life(game_instance=game_instance)
    row, col, self.tile = self.get_tile_from_pos(game_instance)
    game_instance.trails[row,col] = 1
    game_instance.trail_nums[row,col] = self.p_num
    self.time_active+=1
    if self.time_active>self.active_time and not self.saved:
      self.destroy()
      return
    self.altitude = self.tile['altitude']
    self.speed_multiplier = self.speeds[self.tile['name']]
    dx=math.cos(self.dir)
    dy=math.sin(self.dir)
    self.dir+=(random.random()-0.5)/2 +random.random()*self.turn_bias
    temp = np.array([dx, dy], dtype="float32")
    if abs(temp[0])>0.001 or abs(temp[1])>0.001:
      temp/=np.linalg.norm(temp)
      self.cur_action = temp
      if self.hidden:
        self.take_action(game_instance)
    return self.cur_action
  
  def render(self, color, screen, pov=None, debug=False):
    if not self.hidden and pov is None:
      self.game.draw.circle(screen, color, center=(float(self.pos[0]), float(self.pos[1])), radius=self.size)
      h = max(int(self.size/5),2)
      trect = self.game.Rect(self.pos[0]-self.size,self.pos[1]-self.size-h, int(self.size*2-self.size*2*self.time_active/self.active_time),h)
      self.game.draw.rect(screen, (0,100,250), trect)
    elif pov is not None and pov.p_state[self.p_num,5]>0:
      self.game.draw.circle(screen, np.array(color)*pov.p_state[self.p_num,5], center=(float(pov.p_state[self.p_num,0]), float(pov.p_state[self.p_num,1])), radius=self.size)
      h = max(int(self.size/5),2)
      trect = self.game.Rect(pov.p_state[self.p_num,0]-self.size,pov.p_state[self.p_num,1]-self.size-h, int(self.size*2-self.size*2*self.time_active/self.active_time),h)
      self.game.draw.rect(screen, (0,100,250), trect)
  def debug_render(self, color, screen, debug=False):
    #print("debug render")
    self.game.draw.circle(screen, color, center=(float(self.pos[0]), float(self.pos[1])), radius=self.size)
    h = max(int(self.size/5),2)
    trect = self.game.Rect(self.pos[0]-self.size,self.pos[1]-self.size-h, int(self.size*2-self.size*2*self.time_active/self.active_time),h)
    self.game.draw.rect(screen, (0,100,250), trect)

  