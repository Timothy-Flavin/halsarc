import numpy as np
import random
import math

class entity(object):
  types = ["static_agent","learnable_agent","player","projectile","person_of_interest", "object_of_interest"]

  def __init__(self, team, game, pos = np.array([0.0,0.0], dtype=np.float32), speed=10, size=20, entity_type="static_agent"):
    self.team = team
    self.game = game
    self.speed = speed
    self.size = size
    self.pos = pos
    self.destroyed = False
    self.combat = None
    self.id=-1
    self.entity_type = entity_type
    self.cur_action = np.zeros((2,),dtype=np.float32)
    self.speed_multiplier=1
  def render(self, color, screen, debug=False):
    self.game.draw.circle(screen, color, center=(float(self.pos[0]), float(self.pos[1])), radius=self.size)
  def debug_render(self, color, screen, debug=False):
    return

  def update(self, delta_time, game_instance):
    self.choose_action(game_instance)
    self.take_action(delta_time)

  def choose_action(self, game_instance):
    self.cur_action = np.array([1-2*random.random(), 1-2*random.random()])
    return self.cur_action

  def take_action(self, delta_time):
    #print(f"pos {self.pos}, cur_act: {self.cur_action}, speed: {self.speed}, speedmult: {self.speed_multiplier}")
    self.pos += self.cur_action * self.speed * self.speed_multiplier
    
  
  def destroy(self):
    self.destroyed = True
    print("I got destroyed")

  def get_tile_from_pos(self, pos, game_instance):
    #print("entity get tile from pos")
    #print(f"screen: {game_instance.screen}, tilemap: {game_instance.tile_map}")
    #print(f"{self.pos[0]} / {game_instance.screen.get_width()} * {game_instance.tile_map.shape[1]}")
    col = int(math.floor(self.pos[0]/game_instance.screen.get_width()*game_instance.tile_map.shape[1]))
    row = int(math.floor(self.pos[1]/game_instance.screen.get_height()*game_instance.tile_map.shape[0]))
    tile = game_instance.tiles[game_instance.tile_map[row,col]]
    return row, col, tile