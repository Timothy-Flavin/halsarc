import numpy as np
from halsarc.Game.entity import entity
import random

class sign_of_life(entity):
  # Speed is how many times per frame the agent can move
  def __init__(self, name, game, pos, color, s_num, reward=0.2):
    entity.__init__(self, game, np.array(pos,dtype=np.float32), 0, 3, entity_type="sign_of_life")
    self.name = name
    self.hidden = True
    self.s_num = s_num
    #self.seen_by = np.zeros(max_agents, dtype=np.float16)
    self.time_active = 0
    self.color = color
    self.found_reward = reward

  def update(self, delta_time, game_instance):
    self.time_active+=1
  
  def render(self, color, screen, pov=None, debug=False):
    #print(f"s state: {self.s_num}, -1, shape: {pov.s_state.shape}")
    if not self.hidden and pov is None:
      self.game.draw.circle(screen, color, center=(float(self.pos[0]), float(self.pos[1])), radius=self.size)    
    elif (pov is not None) and pov.s_state[self.s_num,-1]>0:
      self.game.draw.circle(screen, np.array(color)*pov.s_state[self.s_num,-1], center=(float(pov.s_state[self.s_num,0]), float(pov.s_state[self.s_num,1])), radius=self.size)

  def debug_render(self, color, screen, debug=False):
    self.game.draw.circle(screen, color, center=(float(self.pos[0]), float(self.pos[1])), radius=self.size)

  