import numpy as np
import random 

class player(object):

  def __init__(self, team, game, pos = np.array([0,0]), speed=10, size=20):
    self.team = team
    self.game = game
    self.speed = speed
    self.size = size
    self.pos = pos
    self.destroyed = False
  
  def render(self, color, screen):
    self.game.draw.circle(screen, color, (self.pos[0], self.pos[1]), self.size)

  def update(self, delta_time, game_instance):
    self.choose_action(game_instance)
    self.take_action(delta_time)

  def choose_action(self, game_instance):
    self.cur_action = np.array([1-2*random.random(), 1-2*random.random()])
    return self.cur_action

  def take_action(self, delta_time):
    self.pos += self.cur_action * self.speed * delta_time
  
  def destroy(self):
    self.destroyed = True
