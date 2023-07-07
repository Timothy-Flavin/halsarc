#import sys
import math
#sys.path.append('../Environment')

# Simple pygame program
# Import and initialize the pygame library
import pygame
pygame.init()

import time
from player import player
from entity import entity
import numpy as np
import random
import json
from controllers import *
# Set up the drawing window

from searcher import searcher
from poi import person_of_interest

class sar_env():
  def __init__(self, display=False, tile_map=None, level_name="Island", agent_names=["Human","RoboDog","Drone"], poi_names=["Child","Child","Adult"], seed=0):
    random.seed(seed)
    self.poi_names = poi_names
    self.agent_names = agent_names
    agent_blueprint_url=f"../LevelGen/{level_name}/Agents.json"
    tiles_url=f"../LevelGen/{level_name}/Tiles.json"
    hidden_url=f"../LevelGen/{level_name}/Hidden_Entities.json"
    self.display = display
    if tile_map is not None:
      self.screen = pygame.display.set_mode([tile_map.shape[1]*10, tile_map.shape[0]*10])
    else:
      self.screen = pygame.display.set_mode([64*10, 48*10])
    self.player_input = {'W': False, 'A': False, 'S':False, 'D': False}
    self.tile_map = tile_map
    self.tile_width = 1.0*self.screen.get_height()/tile_map.shape[0]
    self.agent_blueprint = json.load(open(agent_blueprint_url))
    self.hidden_blueprint = json.load(open(hidden_url))
    self.tiles = json.load(open(tiles_url))
    self.reset()

  def step(self, actions, messages):
    self.actions = actions
    self.messages = self.next_messages
    self.next_messages = messages 
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.running = False
      if self.display:
        self.handle_key_press(event)
        self.handle_mouse_event(event)
    
    self.game_logic(0.01)
    print(f"rewards in step: {self.rewards}")
    if self.display:
      self.draw_game()
    state = self.make_state()
    self.terminated = self.finished()
    return state, self.rewards, self.terminated, self.truncated, self
  
  def get_viewable_tiles(self, agent):
    pos = agent.pos
    row, col, tile = agent.get_tile_from_pos(pos, self)
    tile_pos = [row,col]
    viewable = np.zeros((int(self.state_range*2+1),int(self.state_range*2+1)))-1
    for r in range(tile_pos[0]-self.state_range, tile_pos[0]+self.state_range+1):
      for c in range(tile_pos[1]-self.state_range, tile_pos[1]+self.state_range+1):
        # Checks if tile is within view range and if it is in the map
        if (((r-tile_pos[0])*self.tile_width)**2 + ((c-tile_pos[1])*self.tile_width)**2 <= agent.effective_view_range**2 
        and r>=0 and r<self.tile_map.shape[0] and c>=0 and c<self.tile_map.shape[1]):
          viewable[r-tile_pos[0]+self.state_range, c-tile_pos[1]+self.state_range] = self.tile_map[r,c]
    return viewable
  
  def get_viewable_objects(self, a):
    object_state = np.zeros((len(self.objects),4))
    for i,o in enumerate(self.objects):
      if np.sum(np.square(o.pos-a.pos)) < a.effective_view_range*a.effective_view_range:
        object_state[i,0] = o.pos[0]
        object_state[i,1] = o.pos[1]
        if not o.destroyed:
          object_state[i,2] = 1
        object_state[i,3] = entity.types.index(o.entity_type)
    return object_state
  def get_dynamic_map(self,a):
    return np.zeros((int(self.state_range*2+1),int(self.state_range*2+1)))

  def make_state(self):
    map_state = np.zeros((len(self.agents),int(self.state_range*2+1),int(self.state_range*2+1),2))
    for i,a in enumerate(self.agents):
      map_state[i, :, :, 0] = self.get_viewable_tiles(a)
      map_state[i,:,:,1] = self.get_dynamic_map(a)
    object_state = self.get_viewable_objects(a)
    return {"map_state":map_state,"object_state":object_state}
  def start(self):
    return self.make_state(), self

  def finished(self):
    finished = True
    for o in self.active_objects:
      if o.entity_type in ["static_agent","learnable_agent","player"]:
          finished = False
    if finished:
      print("All agents gone game over")
    return finished

  def reset(self):
    self.current_agent = 0
    self.current_step = 0
    self.draw_surface = pygame.Surface((self.screen.get_width(),self.screen.get_height()),pygame.SRCALPHA)
    self.running = True
    self.active_objects = []
    self.objects = []
    self.mouse_pos=None
    self.clicked=False
    self.current_id=0
    self.debug_render = False
    self.agents = []
    self.pois = []
    self.actions = []
    self.state_range = 1
    max_view = 0
    max_alt = 0
    self.next_messages = None
    self.truncated = False
    for t in self.tiles:
      if t["altitude"] > max_alt:
        max_alt = t["altitude"]
    for agent_name in self.agent_names:
      agent = self.agent_blueprint[agent_name]
      self.agents.append(searcher(agent, agent_name, pygame)) 
      self.add_entity(self.agents[-1])
      self.actions.append([random.random(),random.random()])
      if agent["grounded"]:
        if agent["view_range"]*max_alt > max_view:
          max_view = agent["view_range"]*max_alt
      else:
        if agent["view_range"] > max_view:
          max_view = agent["view_range"]
    self.actions = np.array(self.actions)
    self.state_range = max_view
    print(max_view) 
    self.num_agents = len(self.agents)
    self.final_rewards = np.zeros(self.num_agents)
    for poiname in self.poi_names:
      poi = self.hidden_blueprint[poiname]
      self.pois.append(person_of_interest(poi, poiname, pygame)) 
      self.add_entity(self.pois[-1])
      self.pois[-1].pos = np.array([float(random.randint(100,self.screen.get_height()-100)), float(random.randint(100,self.screen.get_width()-100))], dtype=np.float32)
    
  def add_entity(self, obj):
    obj.id = self.current_id
    self.current_id += 1 
    self.active_objects.append(obj)
    self.objects.append(obj)

  def get_active_by_id(self, id):
    for i in self.active_objects:
      if i.id == id:
        return i
    return None

  def get_entity_by_id(self, id):
    for i in self.objects:
      if i.id == id:
        return i
    return None

  def game_logic(self, delta_time):
    print("Set rewards to slight negative")
    self.rewards=np.zeros(self.num_agents)
    for i,agent in enumerate(self.agents):
      if not agent.destroyed:
        self.rewards[i] -= 0.01
      agent.cur_action = self.actions[i]
    for i in self.active_objects:
      if i.destroyed:
        self.active_objects.remove(i)
      else:  
        i.update(delta_time, self)
    print(f"rewards after update: {self.rewards}")
    if self.finished():
      self.rewards += self.final_rewards
      #self.reset()

  def draw_game(self):
    self.screen.fill((0,0,0,255))
    self.draw_surface.fill((0,0,0,0))
    # Fill the background with white
    if self.display:
      self.screen.fill((255, 255, 255,0))
      for r in range(self.tile_map.shape[0]):
        for c in range(self.tile_map.shape[1]):
          trect = pygame.Rect(self.screen.get_width()*c/self.tile_map.shape[1],self.screen.get_height()*r/self.tile_map.shape[0], self.screen.get_width()/self.tile_map.shape[1],self.screen.get_height()/self.tile_map.shape[0])
          pygame.draw.rect(self.screen, self.tiles[self.tile_map[r,c]]["color"], trect)
    # Draw a solid blue circle in the center
    if self.display:
      for i in self.active_objects:
        i.render(color = i.color, screen = self.screen)
        if self.debug_render:
          i.debug_render(color = i.color, screen = self.draw_surface)
      #pygame.draw.circle(screen, (0, 0, 255), (self.x, self.y), 75)
    #self.draw_surface.fill((255,255,255,100),special_flags=pygame.BLEND_RGBA_MULT)
    self.screen.blit(self.draw_surface, (0,0))
    # Flip the display
    if self.display:
      pygame.display.flip()
  
  def handle_mouse_event(self, event):
    if event.type == pygame.MOUSEBUTTONDOWN and not self.clicked:
      self.mouse_pos = pygame.mouse.get_pos()
      self.clicked = True
    elif event.type == pygame.MOUSEBUTTONUP:
      self.clicked = False
 
  # Set the state of user input
  def handle_key_press(self, event):
    handled = False
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_w:
        self.player_input['W'] = True
      if event.key == pygame.K_a:
        game.player_input['A'] = True
      if event.key == pygame.K_s:
        game.player_input['S'] = True
      if event.key == pygame.K_d:
        game.player_input['D'] = True
      if event.key == pygame.K_SPACE:
        self.debug_render = True
      handled=True
    elif event.type == pygame.KEYUP:
      if event.key == pygame.K_w:
        game.player_input['W'] = False
      if event.key == pygame.K_a:
        game.player_input['A'] = False
      if event.key == pygame.K_s:
        game.player_input['S'] = False
      if event.key == pygame.K_d:
        game.player_input['D'] = False
      if event.key == pygame.K_SPACE:
        self.debug_render = False
      handled=True
    return handled

  def found(self, obj, id):
    reward = 0
    if obj.entity_type=="person_of_interest":
      reward+=1.0
    elif obj.entity_type=="point_of_interest":
      reward+=0.5
    self.rewards[id]+=reward
    self.final_rewards+=reward/self.num_agents
  
if __name__ == "__main__":
  agents = ["Human","RoboDog","Drone"]
  premade_map = np.load("../LevelGen/Island/Map.npy")
  game = sar_env(display=True, tile_map=premade_map, agent_names=agents)
  state, info = game.start()
  controller = player_controller(None)
  terminated = False

  while not terminated:
    actions = np.zeros((len(agents),2))
    messages = np.zeros((len(agents),2))
    for i,a in enumerate(agents):
      actions[i] = controller.choose_action(state=state, game_instance=game)
    state, rewards, terminated, truncated, info =game.step(actions=actions, messages=messages)
  pygame.quit()