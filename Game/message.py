import numpy as np

class Message():
  messages = None
  cur_message=-1

  def __init__(self, game, name, m_type:int=0, x:float=0, y:float=0, dx:float=0,dy:float=0,agent_type="Human",brain_type="vpg", to=-1, poi_id=-1, magnitude=5):
    # message encoding: [int message_type, float x, float y, float dx, float dy]
    self.game_instance = game
    self.x = x
    self.y = y
    self.dx = dx
    self.dy = dy
    self.m_type = m_type
    self.name = name
    self.agent_type = agent_type
    self.brain_type = brain_type
    self.to = to #agent id
    self.poi_id = poi_id
    self.magnitude = magnitude
    self.hr_message = self.to_string()
    self.mr_message = self.to_ai()
    self.n_lines = 124//game.my_font.get_height()
    
    if Message.messages is None:
      Message.messages = [""]*self.n_lines
    
  def __send__(self):
    Message.cur_message = (Message.cur_message+1)%self.n_lines
    Message.messages[Message.cur_message] = self.hr_message

  def to_ai(self):
    return

  def dir_to_cardinal(self, dx, dy):
    s2 = np.sqrt(2)
    dir_dict = {
      "north": np.array([0,-1]),
      "north-east": np.array([1,-1]) / s2,
      "east": np.array([1,0]),
      "south-east": np.array([1,1]) / s2,
      "south": np.array([0,1]),
      "south-west": np.array([-1,1]) / s2,
      "west": np.array([-1,0]),
      "north-west": np.array([-1,-1]) / s2,
    }
    dir = "north"
    aprox = 5
    for k in dir_dict.keys():
      temp = np.sum(np.square(np.array([dx,dy]) - dir_dict[k]))
      if temp < aprox:
        aprox = temp
        dir = k
    return dir

  def to_string(self):
    encodings = [
      f" SoS! ",
      f" Sign of Life found!",
      f" Found {self.game_instance.pois[self.poi_id].name}",
      f" Needs a {self.game_instance.pois[self.poi_id].save_by} to be saved",
      f" Target Saved: {self.game_instance.pois[self.poi_id].name}",
      f" Roger",
      f" I want to go {self.magnitude} {self.dir_to_cardinal(self.dx,self.dy)} <{self.dx:.2f} {self.dy:.2f}>",
      f" {self.to} Should go {self.magnitude} {self.dir_to_cardinal(self.dx,self.dy)} <{self.dx:.2f},{self.dy:.2f}>"
    ]
    return f"{self.name} ({self.brain_type}) [{int(self.x)}, {int(self.y)}]: "+encodings[self.m_type]
  
  def render(self, font, screen, game):
    n=0
    for n in range(self.n_lines):
      #print(Message.messages)
      #print(f"{Message.cur_message-n} : {Message.messages[Message.cur_message-n]}")
      text_surface = font.render(Message.messages[Message.cur_message-n], False, (0, 0, 0))
      screen.blit(text_surface, (10,game.map_pixel_height+game.button_height+(self.n_lines-n-1)*font.get_height()))
      n+=1
    