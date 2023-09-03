import numpy as np
import random
import math

class entity(object):
  types = ["static_agent","learnable_agent","player","person_of_interest","sign_of_life"]

  def __init__(self, game, pos = np.array([0.0,0.0], dtype=np.float32), speed=10, size=20, entity_type="static_agent"):
    self.game = game
    self.speed = speed
    self.size = size
    self.pos = pos
    self.destroyed = False
    self.id=-1
    self.entity_type = entity_type
    self.cur_action = np.zeros((2,),dtype=np.float32)
    self.speed_multiplier=1

  def render(self, color, screen, pov=-1, debug=False):
    self.game.draw.circle(screen, color, center=(float(self.pos[0]), float(self.pos[1])), radius=self.size)
  
  def debug_render(self, color, screen, debug=False):
    return

  def update(self, delta_time, game_instance):
    self.choose_action(game_instance)
    self.take_action(delta_time)

  def choose_action(self, game_instance):
    self.cur_action = np.array([1-2*random.random(), 1-2*random.random()])
    return self.cur_action

  def take_action(self, game_instance):
    #print(f"pos {self.pos}, cur_act: {self.cur_action}, speed: {self.speed}, speedmult: {self.speed_multiplier}")
    scale = np.linalg.norm(self.cur_action)
    dir = self.cur_action * self.speed * self.speed_multiplier * 2 
    if scale > 0:
      dir = dir / scale
    #print(f"Dir: {dir}, pos: {self.pos} = {self.pos+dir}")
    self.pos += dir
    self.pos[0] = max(min(self.pos[0],game_instance.map_pixel_width-0.01),0)
    self.pos[1] = max(min(self.pos[1],game_instance.map_pixel_height-0.01),0)
    
  
  def destroy(self):
    self.destroyed = True

  def get_tile_from_pos(self, game_instance):
    col = int(math.floor(self.pos[0]/game_instance.map_pixel_width*game_instance.tile_map.shape[1]))
    row = int(math.floor(self.pos[1]/game_instance.map_pixel_height*game_instance.tile_map.shape[0]))
    tile = game_instance.tiles[game_instance.tile_map[row,col]]
    return row, col, tile