#import sys
import math
import os
#sys.path.append('../Environment')

# Simple pygame program
# Import and initialize the pygame library
import pygame
pygame.init()

import time
from halsarc.Game.player import player
from halsarc.Game.entity import entity
import numpy as np
import random
import json
from halsarc.Game.controllers import *
# Set up the drawing window

from halsarc.Game.searcher import searcher #halsarc.Game.
from halsarc.Game.poi import person_of_interest
from halsarc.Game.sol import sign_of_life
from halsarc.Game.message import Message

class Button():
  def __init__(self, callback, x, y, text, font, w=None, h=None, color=[200,200,250], text_color=[255,255,255], hover_color=None, image=None, args=None):
    self.hovered=False
    self.callback = callback
    self.args = args
    self.x = x
    self.y = y
    self.font = font
    self.color = color
    self.text_color = text_color
    self.text_height = font.get_height()
    self.image = image
    self.enabled = False
    if hover_color is None:
      self.hover_color=[]
      for i in range(len(self.color)):
        self.hover_color.append(max(self.color[i]-50,0))
    else:
      self.hover_color = hover_color
    if w is None:
      w = font.get_height()*len(text)
    else:
      self.w = w
    if h is None:
      self.h = int(self.text_height*1.2)
    else:
      self.h = h
    self.text = text

  def render(self, screen, enabled):
    self.enabled = enabled
    trect = pygame.Rect(self.x,self.y,self.w,self.h)
    if not self.enabled:
      pygame.draw.rect(screen, [150,150,150], trect)
    elif self.hovered:
      pygame.draw.rect(screen, self.hover_color, trect)
    else:
      pygame.draw.rect(screen, self.color, trect)
    if self.image is not None:
      screen.blit(self.image, (self.x,self.y))
      #print(f"{self.x},{self.y}")
    text_surface = self.font.render(self.text, False, self.text_color)
    pd = (self.h-self.text_height)//2
    screen.blit(text_surface, (self.x+pd,self.y+pd))

  def handle_move(self, mouse_pos):
    if mouse_pos[0] > self.x and mouse_pos[1] > self.y and mouse_pos[0]<self.x+self.w and mouse_pos[1] < self.y+self.h:
      self.hovered = True
    else:
      self.hovered = False

  def handle_press(self, mouse_pos):
    if not self.enabled:
      return
    if mouse_pos[0] > self.x and mouse_pos[1] > self.y and mouse_pos[0]<self.x+self.w and mouse_pos[1] < self.y+self.h:
      if self.args is None:
        self.callback(self)
      else:
        self.callback(self, self.args)
      return True
    return False

class sar_env():
  def wait(self, ms):
    pygame.time.wait(ms)

  def buttonback(self, button):
    print(f"pressed {button.text}")

  def __on_click_return_num__(self, button, args):
    self.bnum = args

  def __draw_ui_window__(self):
    trect = pygame.Rect(self.tile_width*2,
                        self.tile_width*2,
                        self.map_pixel_width+self.w_pad-self.tile_width*4,
                        self.map_pixel_height+self.h_pad-self.tile_width*4)
    pygame.draw.rect(self.screen,[30,30,30],trect)

  def __command_button__(self, button):
    selected = False
    mouse_loc = [0,0]
    h = self.my_font.get_height()
    mbtn = False
    agent = -1
    while not selected:
      agent = -1
      self.__draw_ui_window__()
      for event in pygame.event.get():
        self.handle_key_press(event)
        if event.type == pygame.QUIT:
          self.running = False
          selected=True
        if event.type == pygame.MOUSEMOTION:
          mouse_loc = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
          mbtn = True
        if event.type == pygame.MOUSEBUTTONUP:
          mbtn = False
      
      for i in range(len(self.agents)):
        if mouse_loc[0] > self.tile_width*2 and \
          mouse_loc[0] < self.map_pixel_width+self.w_pad-self.tile_width*2 and \
          mouse_loc[1] > self.tile_width*2 + i*h and \
          mouse_loc[1] < self.tile_width*2 + (i+1)*h:
          trect = pygame.Rect(self.tile_width*2,
                        self.tile_width*2+i*h,
                        self.map_pixel_width+self.w_pad-self.tile_width*4,
                        h)
          pygame.draw.rect(self.screen,[60,60,60],trect)
          agent = i
          if mbtn:
            selected = True
        pygame.draw.circle(
          self.screen, 
          self.agents[i].color, 
          center=(
            float(self.tile_width*3)+h/3, 
            float(self.tile_width*2+i*h)+h/2
          ), 
          radius=h/3
        )
        text_surface = self.my_font.render(self.agents[i].name, False, [250,250,250])
        self.screen.blit(text_surface, (self.tile_width*2+2*h,self.tile_width*2+i*h))
      pygame.display.flip()
    
    selected = False
    self.bnum = -1
    while not selected:
      for event in pygame.event.get():
        self.handle_key_press(event)
        if event.type == pygame.QUIT:
          self.running = False
          selected=True
        if event.type == pygame.MOUSEMOTION:
          for b in self.dir_buttons:
            b.handle_move(pygame.mouse.get_pos())
        if event.type == pygame.MOUSEBUTTONDOWN and not self.clicked:
          for b in self.dir_buttons:
            b.handle_press(pygame.mouse.get_pos())
      self.__draw_ui_window__()
      for b in self.dir_buttons:
        b.render(self.screen,True)
      if self.bnum>-1:
        selected=True
      pygame.display.flip()
      #TODO make message out of agent and self.bnum (direction)
    s2 = np.sqrt(2)
    dirs = [
      np.array([0,-1]),
      np.array([1,-1]) / s2,
      np.array([1,0]),
      np.array([1,1]) / s2,
      np.array([0,1]),
      np.array([-1,1]) / s2,
      np.array([-1,0]),
      np.array([-1,-1]) / s2,
    ]
    """
    msg = Message(
      game = self, 
      name = self.agents[self.player].name,
      m_type = 7,
      x = int(self.agents[self.player].pos[0]),
      y = int(self.agents[self.player].pos[1]),
      dx = dirs[self.bnum][0],
      dy = dirs[self.bnum][1],
      agent_type=self.agents[self.player].48,
      brain_type="Human",
      to=self.agents[agent].name,
      )
    msg.__send__()
    """
    self.actions[self.player]
    self.actions[self.player,2]=1.0
    self.actions[self.player,3]= dirs[self.bnum][0]
    self.actions[self.player,4]= dirs[self.bnum][1]
    self.actions[self.player,5]=5
    mt = np.zeros(8)
    mt[7]=1
    self.actions[self.player,6:14] = mt
    al = np.zeros(len(self.agents))
    al[agent]=1
    self.actions[self.player,14:] = al
    if self.agents[agent].commanded <=0:
      self.agents[agent].commanded = 5
      self.agents[agent].command_dir = dirs[self.bnum]
      self.agents[agent].command_frame = self.frame_num

  def __roger_button__(self,button):
    self.__general_button__(button, 5)
  def __sos_button__(self,button):
    self.__general_button__(button, 0)
  def __sol_button__(self,button):
    self.__general_button__(button, 1)

  def __found_button__(self, button):
    self.__general_button__(button, 4,1)
  
  def __needs_button__(self, button):
    self.__general_button__(button, 3,0)

  def __saved_button(self, button):
    self.__general_button__(button, 4,0)
  
  def __intent_button__(self, button):
    self.actions[self.player]
    self.actions[self.player,2]=1.0
    self.actions[self.player,3]=self.agents[self.player].cur_action[0]
    self.actions[self.player,4]=self.agents[self.player].cur_action[1]
    self.actions[self.player,5]=5
    mt = np.zeros(8)
    mt[6]=1
    self.actions[self.player,6:14] = mt
    self.actions[self.player,14:] = -1

    for i,a in enumerate(self.agents):
      if True: # if a can use radio TODO
        a.a_state[a.__i_adjust__(i),2] = self.agents[self.player].cur_action[0]
        a.a_state[a.__i_adjust__(i),3] = self.agents[self.player].cur_action[1]

  def __general_button__(self,button,msg_type, poi=-1):
    self.actions[self.player]
    self.actions[self.player,2]=1.0
    self.actions[self.player,3]=0
    self.actions[self.player,4]=0
    self.actions[self.player,5]=0
    mt = np.zeros(8)
    mt[msg_type]=1
    self.actions[self.player,6:14] = mt
    self.actions[self.player,14:] = -1

  def __make_buttons__(self):
    names = ["SOS","Sol","Found POI","Help POI", "Saved", "Roger", "Going", "Go"]
    widths = [58,  48,    112,        96,       72,      72,      72,      36]
    colors = [[240,100,100], [225,218,150], [150,240,150], [240,220,150], [0,250,100], [50,220,50], [100,100,240], [200,200,250]]
    callbacks = [
      self.__sos_button__, 
      self.__sol_button__, 
      self.__found_button__,  
      self.__needs_button__, 
      self.__saved_button, 
      self.__roger_button__, 
      self.__intent_button__, 
      self.__command_button__
    ]
    w=0
    self.buttons = []
    for i in range(len(names)):
      bt = Button(callbacks[i], 5+w,self.map_pixel_height+5,names[i],self.my_font,widths[i],self.my_font.get_height()+8,colors[i])
      self.buttons.append(bt)
      w += widths[i]+5

    self.dir_buttons = []
   #print("which file are my images in?")
   #print(__file__)
   #print(os.path.dirname(__file__))
    im = pygame.image.load(os.path.dirname(__file__)+f"/Dir_{0}.png")
    scale = im.get_width()
    #          up     upright right    r_down   down     l_down left
    xyoffs = [[scale ,0], [scale*2,0], [scale*2,scale], [scale*2,scale*2], [scale,scale*2], [0,scale*2],[0,scale],[0,0]]
    bx = (self.map_pixel_width + self.w_pad - scale *3)/2
    by = (self.map_pixel_height + self.h_pad - scale *3)/2
    for i in range(8):
      im = pygame.image.load(os.path.dirname(__file__)+f"\\Dir_{i}.png")
      #print(im)
      self.dir_buttons.append(
        Button(
          self.__on_click_return_num__,
          bx+xyoffs[i][0], 
          by+xyoffs[i][1],
          "",
          self.my_font, 
          scale,
          scale,
          [50,50,200],
          hover_color=[20,20,150],
          image=im,args=i)
        )

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
    self.button_height = 48
    self.tile_width = 10
    self.map_pixel_height = tile_map.shape[0]*self.tile_width
    self.map_pixel_width = tile_map.shape[1]*self.tile_width
    self.w_pad = 0
    if self.map_pixel_width < 480:
      self.w_pad = 480 - self.map_pixel_width
    self.h_pad = 0
    if self.map_pixel_height < 480:
      self.w_pad = 480 - self.map_pixel_height
    
    self.my_font = pygame.font.SysFont('Signal MS', 20)
    print(pygame.font.get_default_font())
    #pygame.font.init()
    self.display = display
    self.screen = pygame.display.set_mode([self.map_pixel_width+self.w_pad, self.map_pixel_height+self.text_box_height + self.button_height+self.h_pad])
    self.tile_map = tile_map
    
  def __load_agents_tiles__(self, level_dir, level_name):
    agent_blueprint_url=f"../{level_dir}/{level_name}/Agents.json"
    tiles_url=f"../{level_dir}/{level_name}/Tiles.json"
    hidden_url=f"../{level_dir}/{level_name}/POI.json"
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
               level_dir="LevelGen",
               level_name="Island", 
               agent_names=["Human","RoboDog","Drone"], 
               poi_names=["Child","Child","Adult"], 
               player = -1,
               explore_multiplier=0.1,
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
    self.player = player
    self.explore_multiplier = explore_multiplier
    self.radio = {"1":1}
    self.__set_max_entities__(agent_names, poi_names, max_agents, max_poi, max_sol)
    self.__load_agents_tiles__(level_dir, level_name)
    self.__setup_screen__(tile_map, display)
    self.__make_buttons__()
    self.player_input = {'W': False, 'A': False, 'S':False, 'D': False}
    self.reset()

  def __reset_state_constants__(self):
    self.rewards = np.zeros(self.max_agents)
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
    self.agent_type_names = list(self.agent_blueprint.keys())
    self.num_agent_types = len(self.agent_blueprint.keys())
    for i,nm in enumerate(self.agent_blueprint.keys()):
      self.agent_types[nm] = i

    for i,agent_name in enumerate(self.agent_names):
      agent_name_ct[agent_name] = agent_name_ct.get(agent_name,0)+1
      agent = self.agent_blueprint[agent_name]
      self.agents.append(searcher(agent, i, agent_name, agent_name_ct[agent_name], self.agent_types[agent_name], pygame)) 
      self.agents[-1].memory = np.zeros((self.tile_map.shape[0], self.tile_map.shape[1]))
      self.agents[-1].a_state = np.zeros((self.max_agents,6+self.num_agent_types)) # x,y,dx,dy,alive,recency,[atype] one hot coded
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

  def __reset_radio__(self):
    self.radio = {
        "message": 
        np.zeros((14+self.max_agents+len(self.agent_types))),
        "sender":[
          np.zeros(self.max_agents),
          np.zeros(len(self.agent_types)),
          self.agents[0].brain_name
        ],
        "queue_status":[],
        "message_legality":[]
      } 
    for i,a in enumerate(self.agents):
      self.radio['queue_status'].append([0,0,1])
      self.radio['message_legality'].append([0,0,0,0,0,0,1,1])
    self.radio['queue_status'] = np.array(self.radio['queue_status'])
    self.radio['message_legality'] = np.array(self.radio['message_legality'])
    
  def reset(self):
    self.__reset_state_constants__()
    self.draw_surface = pygame.Surface((self.map_pixel_width,self.map_pixel_height+self.text_box_height+self.button_height),pygame.SRCALPHA)
    self.active_objects = []
    self.objects = []
    self.agents = []
    self.pois = []
    self.actions = []
    self.signs_of_life = [None]*self.max_sol
    self.cur_sol = 0
    self.frame_num=0
    self.__populate_agents__()
    self.__populate_poi__()
    self.__reset_radio__()

  def __look_for_key_press__(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.running = False
      if self.display:
        self.handle_key_press(event)
        self.handle_mouse_event(event)

  def __chatter__(self, messages):
    rng = np.arange(0,len(self.agents),1)
    np.random.shuffle(rng)
    sent = False
    for m in rng:
      #print(messages[m,2]) 
      if messages[m,2] < 0.5:
        self.agents[m].message_state = np.array([0,0,1])
        continue
      elif sent:
        self.agents[m].message_state = np.array([0,1,0])
        continue
      self.agents[m].message_state = np.array([1,0,0])
      a = self.agents[m]
      mtp = np.argmax(messages[m,6:14]*a.legal_messages)
      act = messages[m,3:5]
      msg = Message(
        self,
        self.agents[m].name,
        mtp,
        a.pos[0],
        a.pos[1],
        act[0],
        act[1],
        a.a_num,
        a.brain_name,
        self.agents[np.argmax(messages[m,14:14+len(self.agents)])].name,
        a.poi,
        messages[m,5]
      )
      msg.__send__()
      if mtp <6: # this makes it so messages can only be sent the once
        #print("sent so illegal")
        a.legal_messages[mtp]=0
        if mtp == 2 or mtp == 3:
          a.poi = -1
      if mtp == 7:
        self.agents[np.argmax(messages[m,14:14+len(self.agents)])].legal_messages[5]=1

     #print(f"Messanger: [{m}], {self.agents[m].name}")
      for i,ag in enumerate(self.agents):
       #print(f"agent[{i}] updates {ag.__i_adjust__(m)}")
        if True: #Can use radio TODO
          ag.a_state[ag.__i_adjust__(m),0] = a.pos[0]
          ag.a_state[ag.__i_adjust__(m),1] = a.pos[1]
          ag.a_state[ag.__i_adjust__(m),2] = 0
          ag.a_state[ag.__i_adjust__(m),3] = 0
          if mtp == 6:
            ag.a_state[ag.__i_adjust__(m),2] = act[0]
            ag.a_state[ag.__i_adjust__(m),3] = act[1]
      #input()
      atp = np.zeros(self.num_agent_types)
      atp[a.a_type] = 1 
      target = np.zeros(self.max_agents)
      target[a.a_num] = 1
      self.radio = {
        "message": 
        np.concatenate(
          (
            np.array([
            a.pos[0],
            a.pos[1],
            act[0], 
            act[1],
            messages[m,5]
            ]), 
            messages[m,6:15],
            target,
            atp
          )
        ),
        "sender":[
          np.zeros(self.max_agents),
          np.zeros(len(self.agent_types)),
          self.agents[m].brain_name
        ],
        "queue_status":[],
        "message_legality":[]
      } 

  def __update_memory__(self):
    for a in self.agents:  
      a.__update_memory__(self)
  def step(self, actions):
    self.actions = actions
    self.__look_for_key_press__()
    self.__game_logic__(0.01)
    self.__update_memory__()
   #print(f"before chatter:\n {self.agents[self.player].a_state[:,0:2]}")
    #print(f"rewards in step: {self.rewards}")
    self.__chatter__(actions)
   #print(f"after chatter:\n {self.agents[self.player].a_state[:,0:2]}")
    state = self.__make_state__()
    if self.display:
      if self.player != -1:
        self.draw_from_pov(self.agents[self.player], state)
      else:
        self.draw_game()
    self.terminated = self.finished()
    self.frame_num+=1
    return state, self.rewards, self.terminated, self.truncated, self
  
  def __get_viewable_tiles__(self, agent):
    pos = agent.pos
    row, col, tile = agent.get_tile_from_pos(self)
    tile_pos = [row,col]
    mem=np.sum(agent.memory)
    viewable = np.zeros((int(self.max_agent_view_dist*2+1),int(self.max_agent_view_dist*2+1)))-1
    for r in range(tile_pos[0]-self.max_agent_view_dist, tile_pos[0]+self.max_agent_view_dist+1):
      for c in range(tile_pos[1]-self.max_agent_view_dist, tile_pos[1]+self.max_agent_view_dist+1):
        # Checks if tile is within view range and if it is in the map
        if not agent.destroyed and (((r-tile_pos[0])*self.tile_width)**2 + ((c-tile_pos[1])*self.tile_width)**2 <= agent.effective_view_range**2 
        and r>=0 and r<self.tile_map.shape[0] and c>=0 and c<self.tile_map.shape[1]):
          viewable[r-tile_pos[0]+self.max_agent_view_dist, c-tile_pos[1]+self.max_agent_view_dist] = self.tile_map[r,c]
          self.rewards[agent.a_num]+=(1-agent.memory[r,c])*self.explore_multiplier
          agent.memory[r,c]=1
    agent.memory*=0.99
    #self.rewards[agent.a_num] += (np.sum(agent.memory)-mem) / self.max_agent_view_dist / self.max_agent_view_dist * self.explore_multiplier
    return viewable, agent.memory
  
  def __get_viewable_objects__(self, a):
    return {"a_state": a.a_state, "s_state": a.s_state, "p_state":a.p_state}
  
  def __get_dynamic_map__(self,a):
    return np.zeros((int(self.max_agent_view_dist*2+1),int(self.max_agent_view_dist*2+1)))

  def __make_state__(self):
    map_state = np.zeros((len(self.agents),int(self.max_agent_view_dist*2+1),int(self.max_agent_view_dist*2+1)))#single channel no fire
    object_state = []
    self.radio['queue_status'] = []
    self.radio['message_legality'] = []
    memory=np.zeros((len(self.agents),self.tile_map.shape[0],self.tile_map.shape[1],2))
    for i,a in enumerate(self.agents):
      tiles, agent_memory = self.__get_viewable_tiles__(a)
      map_state[i, :, :] = tiles
      #map_state[i,:,:,1] = self.__get_dynamic_map__(a)
      object_state.append(self.__get_viewable_objects__(a))
      memory[i,:,:,0]=agent_memory
      memory[i,:,:,1]=self.tile_map
      self.radio['queue_status'].append(a.message_state)
      self.radio['message_legality'].append(a.legal_messages)

    return {"view":map_state,"object_state":np.array(object_state),"memory":np.array(memory),"radio":self.radio}

  def start(self):
    self.reset()
    return self.__make_state__(), self

  def leave_tracks(self, a):
    sol = sign_of_life("Track",pygame,a.pos,[200,150,120],self.cur_sol%self.max_sol,0.1) 
    #self.add_entity(sol)
    self.signs_of_life[self.cur_sol%self.max_sol] = sol
    self.cur_sol += 1
    
  def leave_clothes(self, a):
    #print("pop")
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

  def __game_logic__(self, delta_time):
    self.rewards=np.zeros(self.num_agents)
    for i,agent in enumerate(self.agents):
      if not agent.destroyed:
        self.rewards[i] -= 0.01
      agent.cur_action = self.actions[i,0:2]
    for i in self.active_objects:
      if i.destroyed:
        self.active_objects.remove(i)
      else:  
        i.update(delta_time, self)
    #print(f"rewards after update: {self.rewards}")
    if self.finished():
      self.rewards += self.final_rewards
      #self.reset()

  def __draw_buttons__(self, a):
    #print(f"button {a.legal_messages}, {a.name}")
    for i,b in enumerate(self.buttons):
      b.render(self.draw_surface, a.legal_messages[i]>0)

  def __draw_messages__(self):
    msg = Message(self, "Human1",random.randint(0,7),100,100,0,0,"Human",to=1,poi_id=1)
    msg.render(self.my_font,self.draw_surface, self)

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
    self.__draw_buttons__()
    self.__draw_messages__()
    self.screen.blit(self.draw_surface, (0,0))
    # Flip the display
    if self.display:
      pygame.display.flip()
  
  def draw_from_pov(self, a, state): # a is agent
    self.screen.fill((0,0,0,0))
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
      dr = []
     #print("Drawing agents")
     #print(f"{a.a_state[:,0:2]}")
      for i in self.active_objects:
        i.render(color = i.color, screen = self.screen, pov=a)
        if self.debug_render:
          i.debug_render(color = i.color, screen = self.draw_surface)
      #print(f"dr: {dr}")
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
    self.__draw_buttons__(a)
    self.__draw_messages__()
    self.screen.blit(self.draw_surface, (0,0))
    # Flip the display
    if self.display:
      pygame.display.flip()
    #input()
  def handle_mouse_event(self, event):
    if event.type == pygame.MOUSEMOTION:
      for b in self.buttons:
        b.handle_move(pygame.mouse.get_pos())
    if event.type == pygame.MOUSEBUTTONDOWN and not self.clicked:
      for b in self.buttons:
        b.handle_press(pygame.mouse.get_pos())

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
    if obj.hidden:
      reward += obj.found_reward
    if obj.entity_type=="person_of_interest":
      if self.agent_type_names[agent.a_num] in obj.save_by:
        reward += obj.saved_reward
        obj.saved = True
    self.rewards[agent.id]+=reward
    self.final_rewards+=reward/self.num_agents
  
  # This is a static function so call sar_env.vectorize_state
  def vectorize_state(state,anum,radio=False):
    a1 = state['view'][anum].flatten()
    a2 = np.concatenate(
          (
            state['object_state'][anum]["a_state"].flatten(),
            state['object_state'][anum]["s_state"].flatten(),
            state['object_state'][anum]["p_state"].flatten(),
          )
        )
    a3 = state['memory'][anum].flatten()
    a4 = np.concatenate(
          (
            state['radio']["message"].flatten(),
            state['radio']["message_legality"][anum].flatten(),
            state['radio']["queue_status"][anum].flatten(),
            state['radio']['sender'][0],
            state['radio']['sender'][1]
          )
        )
    if not radio:
      a4 = np.zeros(a4.shape)
    return np.concatenate((a1,a2,a3,a4)).astype(np.double)

if __name__ == "__main__":
  agents = ["Human","RoboDog","Drone"]
  pois = ["Child", "Child", "Adult"]
  premade_map = np.load("../LevelGen/Island/Map.npy")
  game = sar_env(display=True, tile_map=premade_map, agent_names=agents, poi_names=pois,player=0)
  state, info = game.start()
  controller = player_controller(None)
  terminated = False
  #print(sar_env.vectorize_state(state,0,True).shape)
  while not terminated:
    actions = np.zeros((len(agents),14+len(agents)))
    for i,a in enumerate(agents):
      actions[i,0:2] = np.random.random(2)*2-1#controller.choose_action(state=state, game_instance=game)
      actions[i,2:] = np.random.random(12+len(agents))
    state, rewards, terminated, truncated, info = game.step(actions=actions)
    #print(sar_env.vectorize_state(state,0,True).shape)
    #input()
    game.wait(100)