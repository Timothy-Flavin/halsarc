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
from sol import sign_of_life
from message import Message
import queue

class sar_env():
  def wait(self, ms):
    pygame.time.wait(ms)

  def __set_max_entities__(self, agent_names, poi_names, max_agents, max_poi, max_sol):
    self.max_agents = len(agent_names)
    if max_agents is not None:
      if max_agents < self.max_agents:
        raise Exception(f"Max agents {max_agents} less than number of agent names: {len(agent_names)}")
      self.max_agents = max_agents
    self.max_poi = len(poi_names)
    if max_poi is not None:
      if max_poi < self.max_poi:
        raise Exception(f"Max persons of interest poi: {max_poi} less than number of poi names: {len(poi_names)}")
      self.max_poi = max_poi
    self.max_sol = max_sol
    self.poi_names = poi_names
    self.agent_names = agent_names

  def __setup_screen__(self, tile_map, display):
    self.text_box_height = 124
    self.tile_width = 10
    self.map_pixel_height = tile_map.shape[0]*self.tile_width
    self.map_pixel_width = tile_map.shape[1]*self.tile_width
    self.my_font = pygame.font.SysFont('Comic Sans MS', 12)
    pygame.font.init()
    self.display = display
    self.screen = pygame.display.set_mode([tile_map.shape[1]*10, tile_map.shape[0]*10+self.text_box_height])
    self.tile_map = tile_map
    
  def __load_agents_tiles__(self, level_name):
    agent_blueprint_url=f"../LevelGen/{level_name}/Agents.json"
    tiles_url=f"../LevelGen/{level_name}/Tiles.json"
    hidden_url=f"../LevelGen/{level_name}/POI.json"
    self.agent_blueprint = json.load(open(agent_blueprint_url))
    self.hidden_blueprint = json.load(open(hidden_url))
    self.tiles = json.load(open(tiles_url))

  def __init__(self, 
               tile_map, 
               max_agents=None, 
               max_poi=None, 
               max_sol=10, 
               vectorize_state=True, 
               display=False, 
               level_name="Island", 
               agent_names=["Human","RoboDog","Drone"], 
               poi_names=["Child","Child","Adult"], 
               seed=0):
    """
    Args:
      tile_map: n x m np int array of tile id's
      max_agents: used to vectorize agent locations, this is the max number of 
        agents allowed for the scenario. If None, len(agent_names) will be used
      max_poi: maximum number of person's of interest to be searched for in the
        scenario. if None, len(poi_names) will be used
      max_sol: Maximum number of signs of life present on the map at a time. 
        Oldest sign of life will be overwritten by newer ones
      vectorize_state: If True, returns the vectorized state with each part in a
        dictionary. If False, returns the rgb array that would be rendered to a human
      display: if true, game will be displayed, if false it will run headless
      level_name: Which folder to load the level from 
      agent_names: The controllable agents that will play in the environment from 
        Agents.json. repeat names will be added with ids so Human, Human will cause
        the environment to make Human1 Human2
      poi_names: The person's of interest names that will be added to the environment
        from POI.json
      seed: random seed used for spawning Agents and POI
    """
    random.seed(seed)
    self.__set_max_entities__(agent_names, poi_names, max_agents, max_poi, max_sol)
    self.__load_agents_tiles__(level_name)
    self.__setup_screen__(tile_map, display)
    self.player_input = {'W': False, 'A': False, 'S':False, 'D': False}
    self.reset()

  def __reset_state_constants__(self):
    self.current_agent = 0
    self.current_step = 0
    self.running = True
    self.mouse_pos=None
    self.clicked=False
    self.current_id=0
    self.debug_render = False
    self.max_agent_view_dist = 1
    self.truncated = False
    
  def __populate_agents__(self):
    max_view = 0
    max_alt = 0
    for t in self.tiles:
      if t["altitude"] > max_alt:
        max_alt = t["altitude"]
    agent_name_ct = {}
    self.agent_types = {}
    self.num_agent_types = len(self.agent_blueprint.keys())
    for i,nm in enumerate(self.agent_blueprint.keys()):
      self.agent_types[nm] = i

    for i,agent_name in enumerate(self.agent_names):
      agent_name_ct[agent_name] = agent_name_ct.get(agent_name,0)+1
      agent = self.agent_blueprint[agent_name]
      self.agents.append(searcher(agent, i, agent_name, agent_name_ct[agent_name], self.agent_types[agent_name], pygame)) 
      self.agents[-1].memory = np.zeros((self.tile_map.shape[0], self.tile_map.shape[1]))
      self.agents[-1].a_state = np.zeros((self.max_agents,4+self.num_agent_types)) # x,y,alive,recency,[atype] one hot coded
      self.agents[-1].p_state = np.zeros((self.max_poi,6)) # x,y,destroyed,saved,age,recency
      self.agents[-1].s_state = np.zeros((self.max_sol,4)) # x,y,age,recency
      self.add_entity(self.agents[-1])
      self.actions.append([random.random(),random.random()])
      if agent["grounded"]:
        if agent["view_range"]*max_alt > max_view:
          max_view = agent["view_range"]*max_alt
      else:
        if agent["view_range"] > max_view:
          max_view = agent["view_range"]
    self.actions = np.array(self.actions)
    self.max_agent_view_dist = max_view
    self.num_agents = len(self.agents)
    self.final_rewards = np.zeros(self.num_agents)

  def __populate_poi__(self):
    poi_name_ct = {}
    for i,poiname in enumerate(self.poi_names):
      poi = self.hidden_blueprint[poiname]
      poi_name_ct[poiname] = poi_name_ct.get(poiname,0)+1
      self.pois.append(person_of_interest(poi, poiname+str(poi_name_ct[poiname]), i, pygame)) 
      self.add_entity(self.pois[-1])
      self.pois[-1].pos = np.array([float(random.randint(100,self.map_pixel_width-100)), float(random.randint(100,self.map_pixel_height-100))], dtype=np.float32)
      #print(f"pois : {self.pois[-1].pos}")

  def reset(self):
    self.__reset_state_constants__()
    self.draw_surface = pygame.Surface((self.map_pixel_width,self.map_pixel_height+self.text_box_height),pygame.SRCALPHA)
    self.active_objects = []
    self.objects = []
    self.agents = []
    self.pois = []
    self.actions = []
    self.signs_of_life = [None]*self.max_sol
    self.cur_sol = 0
    self.__populate_agents__()
    self.__populate_poi__()

  def __look_for_key_press__(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.running = False
      if self.display:
        self.handle_key_press(event)
        self.handle_mouse_event(event)

  def step(self, actions, messages=None):
    self.actions = actions
    self.next_message = messages 
    self.__look_for_key_press__()
    self.game_logic(0.01)
    #print(f"rewards in step: {self.rewards}")
    state = self.make_state()
    if self.display:
      self.draw_from_pov(self.agents[0], state)
    self.terminated = self.finished()
    return state, self.rewards, self.terminated, self.truncated, self
  
  def __get_viewable_tiles__(self, agent):
    pos = agent.pos
    row, col, tile = agent.get_tile_from_pos(self)
    tile_pos = [row,col]
    viewable = np.zeros((int(self.max_agent_view_dist*2+1),int(self.max_agent_view_dist*2+1)))-1
    for r in range(tile_pos[0]-self.max_agent_view_dist, tile_pos[0]+self.max_agent_view_dist+1):
      for c in range(tile_pos[1]-self.max_agent_view_dist, tile_pos[1]+self.max_agent_view_dist+1):
        # Checks if tile is within view range and if it is in the map
        if (((r-tile_pos[0])*self.tile_width)**2 + ((c-tile_pos[1])*self.tile_width)**2 <= agent.effective_view_range**2 
        and r>=0 and r<self.tile_map.shape[0] and c>=0 and c<self.tile_map.shape[1]):
          viewable[r-tile_pos[0]+self.max_agent_view_dist, c-tile_pos[1]+self.max_agent_view_dist] = self.tile_map[r,c]
          agent.memory[r,c]=1
    agent.memory*=0.99
    return viewable, agent.memory
  
  def __get_viewable_objects__(self, a):
    return {"a_state": a.a_state, "s_state": a.s_state, "p_state":a.p_state}
  
  def get_dynamic_map(self,a):
    return np.zeros((int(self.max_agent_view_dist*2+1),int(self.max_agent_view_dist*2+1)))

  def make_state(self):
    map_state = np.zeros((len(self.agents),int(self.max_agent_view_dist*2+1),int(self.max_agent_view_dist*2+1),2))
    object_state = []
    memory=[]
    for i,a in enumerate(self.agents):
      tiles, agent_memory = self.__get_viewable_tiles__(a)
      map_state[i, :, :, 0] = tiles
      map_state[i,:,:,1] = self.get_dynamic_map(a)
      object_state.append(self.__get_viewable_objects__(a))
      memory.append(agent_memory)
    return {"view":map_state,"object_state":np.array(object_state), "memory":np.array(memory)}
  
  def start(self):
    self.reset()
    return self.make_state(), self

  def leave_tracks(self, a):
    sol = sign_of_life("Track",pygame,a.pos,[200,150,120],self.cur_sol%self.max_sol,0.1) 
    #self.add_entity(sol)
    self.signs_of_life[self.cur_sol%self.max_sol] = sol
    self.cur_sol += 1
    
  def leave_clothes(self, a):
    print("pop")
    sol = sign_of_life("Clothes",pygame,a.pos,[200,150,120],self.cur_sol%self.max_sol,0.1) 
    #self.add_entity(sol)
    self.signs_of_life[self.cur_sol%self.max_sol] = sol
    self.cur_sol += 1

  def finished(self):
    finished = True
    for o in self.active_objects:
      if o.entity_type in ["static_agent","learnable_agent","player"]:
          finished = False
    if finished:
      print("All agents gone game over")
    return finished
  
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
    #print("Set rewards to slight negative")
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
    #print(f"rewards after update: {self.rewards}")
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
          trect = pygame.Rect(self.map_pixel_width*c/self.tile_map.shape[1],self.map_pixel_height*r/self.tile_map.shape[0], self.map_pixel_width/self.tile_map.shape[1],self.map_pixel_height/self.tile_map.shape[0])
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
  
  def draw_from_pov(self, a, state): # a is agent
    self.screen.fill((0,0,0,255))
    self.draw_surface.fill((0,0,0,0))
    # Fill the background with white
    if self.display:
      self.screen.fill((255, 255, 255,0))
      for r in range(self.tile_map.shape[0]):
        for c in range(self.tile_map.shape[1]):
          trect = pygame.Rect(self.map_pixel_width*c/self.tile_map.shape[1],self.map_pixel_height*r/self.tile_map.shape[0], self.map_pixel_width/self.tile_map.shape[1],self.map_pixel_height/self.tile_map.shape[0])
          tpose = np.array([c*self.tile_width, r*self.tile_width])
          pygame.draw.rect(self.screen, np.array(self.tiles[self.tile_map[r,c]]["color"])*(a.memory[r,c]*0.8+0.2), trect)
    # Draw agents and poi
      for i in self.active_objects:
        i.render(color = i.color, screen = self.screen,pov=a)
        if self.debug_render:
          i.debug_render(color = i.color, screen = self.draw_surface)
      #print("Updated")
      for i,sol in enumerate(self.signs_of_life):
        if sol is None:
          continue
        sol.render(color = sol.color, screen = self.screen, pov=a)
        if self.debug_render:
          sol.debug_render(color = sol.color, screen = self.draw_surface)
      #print()
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
        self.player_input['A'] = True
      if event.key == pygame.K_s:
        self.player_input['S'] = True
      if event.key == pygame.K_d:
        self.player_input['D'] = True
      if event.key == pygame.K_SPACE:
        self.debug_render = True
      handled=True
    elif event.type == pygame.KEYUP:
      if event.key == pygame.K_w:
        self.player_input['W'] = False
      if event.key == pygame.K_a:
        self.player_input['A'] = False
      if event.key == pygame.K_s:
        self.player_input['S'] = False
      if event.key == pygame.K_d:
        self.player_input['D'] = False
      if event.key == pygame.K_SPACE:
        self.debug_render = False
      handled=True
    return handled

  def found(self, obj, agent):
    reward = 0
    reward += obj.found_reward
    if obj.entity_type=="person_of_interest":
      if agent.a_type in obj.save_by:
        reward += obj.saved_reward
        obj.saved = True
    self.rewards[agent.id]+=reward
    self.final_rewards+=reward/self.num_agents
  
if __name__ == "__main__":
  agents = ["Human","RoboDog","Drone"]
  pois = ["Child", "Child", "Adult"]
  premade_map = np.load("../LevelGen/Island/Map.npy")
  game = sar_env(display=True, tile_map=premade_map, agent_names=agents, poi_names=pois)
  state, info = game.start()
  controller = player_controller(None)
  terminated = False

  while not terminated:
    actions = np.zeros((len(agents),2))
    messages = np.zeros((len(agents),2))
    for i,a in enumerate(agents):
      actions[i] = controller.choose_action(state=state, game_instance=game)
    state, rewards, terminated, truncated, info = game.step(actions=actions, messages=messages)
    game.wait(100)
  