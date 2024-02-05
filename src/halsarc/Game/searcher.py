import numpy as np
from halsarc.Game.entity import entity
from halsarc.Game.controllers import player_controller
import math

class searcher(entity):
  # Speed is how many times per frame the agent can move
  def __init__(self, agent_blueprint, a_num, name, num, a_type, game, game_instance):
    entity.__init__(self, game, np.array(game_instance.start_pos,dtype=np.float32), 50, 5, entity_type="learnable_agent")
    self.name = name+str(num)
    self.a_num = a_num
    self.a_type = a_type
    self.poi=-1
    self.save_target = -1
    # These next 4 will be instantiated by the game on start
    self.memory = np.zeros((game_instance.tile_map.shape[0], game_instance.tile_map.shape[1]))
    self.a_state = np.zeros((game_instance.max_agents,4)) # x,y,dx,dy,alive,recency,[atype] one hot coded
    self.p_state = np.zeros(3) # x,y,saveable
    self.command_accepted = -1 # who are we listening to rn
    self.commanded = np.zeros(game_instance.max_agents)# How many frames are left in the command
    self.commanded_by = np.zeros(game_instance.max_agents) # who has given us commands
    self.command_dir = np.zeros((game_instance.max_agents,2)) # where we goin
    #print(self.commanded)
    #print("\n\n\n")
    #self.command_frame = 2**31-1 # 
    #self.message_state = np.zeros(3) # sent, denied, not attempted
    self.brain_name = "vpg"
    
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
    self.legal_messages = np.zeros(8)
    self.legal_messages[6] = 1 # can always share intention
    self.legal_messages[7] = 1 # can always send command
    #self.memory = np.zeros(game.tile_map.shape[0], game.tile_map.shape[1])
    #print(list(agent_blueprint["speeds"].keys()))
    for k in list(agent_blueprint["speeds"].keys()):
      self.speeds[k] = agent_blueprint["speeds"][k]
      self.tile_names.append(k)
    for k in list(agent_blueprint["visibilities"].keys()):
      self.visibilities[k] = agent_blueprint["visibilities"][k]

  def __handle_action__(self, game_instance):
    if self.command_accepted>-1 and \
    self.commanded[self.command_accepted]>0: # and \ # If we have frames left in the command
      self.cur_action = self.command_dir[self.command_accepted] # direction of the command we got
      self.commanded[self.command_accepted] -= 1
    if self.commanded[self.command_accepted] <= 0: # once the command is over, reset the command slot
      self.command_accepted = -1
      self.commanded[self.command_accepted] = 0# How many frames are left in the command
      self.commanded_by[self.command_accepted] = 0 # who has given us commands
      self.command_dir[self.command_accepted] = np.zeros(2) 
      
    self.take_action(game_instance)
    self.pos[0] = max(min(self.pos[0],game_instance.map_pixel_width-0.01),0)
    self.pos[1] = max(min(self.pos[1],game_instance.map_pixel_height-0.01),0)
    row, col, self.tile = self.get_tile_from_pos(game_instance)

  def __i_adjust__(self,i):
    #print(f"Agent: {self.a_num}, i {i}")
    if i==self.a_num:
      return 0
    if i<self.a_num:
      return i+1
    return i

  def __update_memory__(self, game_instance):
    self.altitude = self.tile['altitude']
    self.speed_multiplier = self.speeds[self.tile['name']]
    if self.speed_multiplier == 0:
      self.legal_messages[0] = 1
    self.visibility_multiplier = self.visibilities[self.tile['name']]
    if not self.grounded:
      self.speed_multiplier = 1.0
      self.altitude = 1.0
    self.effective_view_range = self.view_range*self.altitude*game_instance.tile_width

    # Agent memory, the last agent is always this agent
    adjust = 1
    for i,obj in enumerate(game_instance.agents):
      ia = i+adjust
      if i == self.a_num:
        adjust=0
        ia = 0#len(game_instance.agents)-1
      
      if np.sum(np.square(self.pos - obj.pos)) < self.effective_view_range*self.effective_view_range:
        # x,y,alive,a_type one hot coded
        #self.a_state[ia] = np.zeros(game_instance.num_agent_types+6)
        self.a_state[ia,2] = 0#obj.pos[0] - self.a_state[ia,0]
        self.a_state[ia,3] = 0#obj.pos[1] - self.a_state[ia,1]
        if ia == 0:
          self.a_state[ia,2:4] = self.cur_action
        self.a_state[ia,0] = obj.pos[0]
        self.a_state[ia,1] = obj.pos[1]
      else:
        self.a_state[ia,0] = self.a_state[ia,0] + self.a_state[ia,2]
        self.a_state[ia,1] = self.a_state[ia,1] + self.a_state[ia,3]
        self.a_state[ia,0] = max(min(self.a_state[ia,0], game_instance.map_pixel_width),0)
        self.a_state[ia,1] = max(min(self.a_state[ia,1], game_instance.map_pixel_height),0)
      #print(
      #  f"speed: {math.sqrt(self.a_state[ia,2]**2 + self.a_state[ia,3]**2)/(obj.speed*obj.speed_multiplier)} from mul: {(obj.speed*obj.speed_multiplier)}")
    #poi
    for i,poi in enumerate(game_instance.pois):
      if np.sum(np.square(self.pos - poi.pos)) < self.effective_view_range*self.effective_view_range:
        if not poi.saved:
          game_instance.found(poi, self)
          #print(f"hidden: {poi.hidden}, saved: {poi.saved}, h: {game_instance.pois[i].hidden}, s: {game_instance.pois[i].saved}")
          poi.hidden = False
          self.poi = i
          if poi.saved:
            #print("Searcher knows saved")
            self.legal_messages[4] = 1
            self.p_state = np.zeros(3)
            #input()
          else:
            self.legal_messages[3] = 1
            self.p_found = game_instance.norm_pos(poi.pos)
    #print(f"{self.name} pois: \n{self.p_state}")
  
  def update(self, delta_time, game_instance):
    self.__handle_action__(game_instance)
    self.time_active+=1
    #arr = np.array([self.pos[0],self.pos[1],0,0, 0,1.0,0,0,0])
    #arr[6+self.a_type]=1 # 6 + num agent types
    #self.a_state[-1] = arr
    if self.time_active>self.active_time:
      self.destroy()
      return
    
  def render(self, color, screen, pov=None, debug=False):
    #if pov is not None:
      #print(f"agent {self.a_num} recency: {pov.a_state[pov.__i_adjust__(self.a_num),4]}")
      #print(self.destroyed)
    if pov is None:
      self.game.draw.circle(screen, color, center=(float(self.pos[0]), float(self.pos[1])), radius=self.size)
      h = max(int(self.size/5),2)
      trect = self.game.Rect(self.pos[0]-self.size,self.pos[1]-self.size-h, int(self.size*2-self.size*2*self.time_active/self.active_time),h)
      self.game.draw.rect(screen, (0,100,250), trect)
    else:# pov.a_state[pov.__i_adjust__(self.a_num),4]>0:
      
     #print(f"drawing {self.a_num} from pov: {pov.a_num} as {pov.__i_adjust__(self.a_num)}")
      x = float(pov.a_state[pov.__i_adjust__(self.a_num),0])
      y = float(pov.a_state[pov.__i_adjust__(self.a_num),1])
     #print(f"{pov.a_state[pov.__i_adjust__(self.a_num),4]:.2f} pos: [{self.pos[0]:.1f},{self.pos[1]:.1f}], memory: [{x:.1f},{y:.1f}]")
      self.game.draw.circle(screen, 
                            np.array(color),#*float(pov.a_state[pov.__i_adjust__(self.a_num),5]),
                            center=(x,
                            y),
                            radius=self.size)
      h = max(int(self.size/5),2)
      trect = self.game.Rect(x-self.size,y-self.size-h, int(self.size*2-self.size*2*self.time_active/self.active_time),h)
      self.game.draw.rect(screen, (0,100,250), trect)


  def debug_render(self, color, screen, debug=False):
    self.game.draw.circle(screen, (250,250,250,100), center=(float(self.pos[0]), float(self.pos[1])), radius=self.effective_view_range)
  