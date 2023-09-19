import numpy as np
from entity import entity
from controllers import player_controller
import math

class searcher(entity):
  # Speed is how many times per frame the agent can move
  def __init__(self, agent_blueprint, a_num, name, num, a_type, game):
    entity.__init__(self, game, np.array([200,200],dtype=np.float32), 50, 5, entity_type="learnable_agent")
    self.name = name+str(num)
    self.a_num = a_num
    self.a_type = a_type
    self.poi=-1
    # These next 4 will be instantiated by the game on start
    self.memory = None
    self.a_state = None
    self.p_state = None
    self.s_state = None
    self.commanded = 0
    self.command_dir = np.zeros(2)
    self.command_frame = 2**31-1
    self.message_state = np.zeros(3) # sent, denied, not attempted
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
    if self.commanded>0 and self.command_frame <= game_instance.frame_num:
      self.cur_action = self.command_dir
      self.commanded -= 1
    self.take_action(game_instance)
    self.pos[0] = max(min(self.pos[0],game_instance.map_pixel_width-0.01),0)
    self.pos[1] = max(min(self.pos[1],game_instance.map_pixel_height-0.01),0)
    row, col, self.tile = self.get_tile_from_pos( game_instance)

  def __i_adjust__(self,i):
    if i==self.a_num:
      return len(self.a_state)-1
    if i>self.a_num:
      return i-1
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
    adjust = 0
    for i,obj in enumerate(game_instance.agents):
      ia = i-adjust
      if i == self.a_num:
        adjust=1
        ia = len(game_instance.agents)-1
      
      self.a_state[ia,5] *= 0.99
      if np.sum(np.square(self.pos - obj.pos)) < self.effective_view_range*self.effective_view_range:
        # x,y,alive,a_type one hot coded
        #self.a_state[ia] = np.zeros(game_instance.num_agent_types+6)
        self.a_state[ia,2] = obj.pos[0] - self.a_state[ia,0]
        self.a_state[ia,3] = obj.pos[1] - self.a_state[ia,1]
        self.a_state[ia,0] = obj.pos[0]
        self.a_state[ia,1] = obj.pos[1]
        self.a_state[ia,4] = 1-int(obj.destroyed)
        self.a_state[ia,5] = 1.0
        self.a_state[ia,ia+4] = 1
      else:
        self.a_state[ia,0] = self.a_state[ia,0] + self.a_state[ia,2]
        self.a_state[ia,1] = self.a_state[ia,1] + self.a_state[ia,3]
        self.a_state[ia,0] = max(min(self.a_state[ia,0], game_instance.map_pixel_width),0)
        self.a_state[ia,1] = max(min(self.a_state[ia,1], game_instance.map_pixel_height),0)
    # Sign of life memory
    for i,sol in enumerate(game_instance.signs_of_life):
      if sol is None:
        continue
      self.s_state[i,3]*=0.99
      if np.sum(np.square(self.pos - sol.pos)) < self.effective_view_range*self.effective_view_range:
        if sol.hidden:
          game_instance.found(sol, self)
          sol.hidden = False
          self.legal_messages[1] = 1
          #print(f"legal: {self.legal_messages}, name: {self.name}")
        self.s_state[i] = [sol.pos[0],sol.pos[1],sol.time_active/100.0,1.0]
    
    for i,poi in enumerate(game_instance.pois):
      self.p_state[i,-1]*=0.99
      if np.sum(np.square(self.pos - poi.pos)) < self.effective_view_range*self.effective_view_range:
        if not poi.saved:
          self.poi = i
          game_instance.found(poi, self)
          poi.hidden = False
          self.poi = i
          if poi.saved:
            self.legal_messages[4] = 1
          else:
            self.legal_messages[3] = 1
          # x,y,destroyed,saved,age,recency
        self.p_state[i] = [poi.pos[0],poi.pos[1],1-int(poi.destroyed), 1-int(poi.saved), poi.time_active/100.0,1]

  def update(self, delta_time, game_instance):
    self.__handle_action__(game_instance)
    self.time_active+=1
    arr = np.array([self.pos[0],self.pos[1],0,0, 0,1.0,0,0,0])
    arr[6+self.a_type]=1 # 6 + num agent types
    self.a_state[-1] = arr
    if self.time_active>self.active_time:
      self.destroy()
      return
    self.__update_memory__(game_instance)

  def render(self, color, screen, pov=None, debug=False):
    if pov is None:
      self.game.draw.circle(screen, color, center=(float(self.pos[0]), float(self.pos[1])), radius=self.size)
      h = max(int(self.size/5),2)
      trect = self.game.Rect(self.pos[0]-self.size,self.pos[1]-self.size-h, int(self.size*2-self.size*2*self.time_active/self.active_time),h)
      self.game.draw.rect(screen, (0,100,250), trect)
    elif pov.a_state[pov.__i_adjust__(self.a_num),4]>0:
      x = float(pov.a_state[pov.__i_adjust__(self.a_num),0])
      y = float(pov.a_state[pov.__i_adjust__(self.a_num),1])
      self.game.draw.circle(screen, 
                            np.array(color)*float(pov.a_state[pov.__i_adjust__(self.a_num),5]),
                            center=(x,
                            y),
                            radius=self.size)
      h = max(int(self.size/5),2)
      trect = self.game.Rect(x-self.size,y-self.size-h, int(self.size*2-self.size*2*self.time_active/self.active_time),h)
      self.game.draw.rect(screen, (0,100,250), trect)


  def debug_render(self, color, screen, debug=False):
    self.game.draw.circle(screen, (250,250,250,100), center=(float(self.pos[0]), float(self.pos[1])), radius=self.effective_view_range)
  