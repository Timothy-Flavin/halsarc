import numpy as np
import random

class entity(object):
  types = ["unlisted","combatant", "projectile"]

  def __init__(self, team, game, pos = np.array([0.0,0.0], dtype=np.float32), speed=10, size=20, entity_type="unlisted"):
    self.team = team
    self.game = game
    self.speed = speed
    self.size = size
    self.pos = pos
    self.destroyed = False
    self.combat = None
    self.id=-1
    self.entity_type = "unlisted"
  
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
    print(self.speed)
    print(delta_time)
    print(self.cur_action * self.speed * delta_time)
    print("---------------------------")
    self.pos += self.cur_action * self.speed * delta_time
  
  def destroy(self):
    self.destroyed = True
    print("I got destroyed")
