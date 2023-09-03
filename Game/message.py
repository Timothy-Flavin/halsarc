

class Message():
  def __init__(self, game, x:float, y:float, m_type:int=0, info:int=0, length:int=1):
    # message encoding: [float x, float y, int message_type, int info, string hr_message]
    self.game_instance = game
    self.x = x
    self.y = y
    self.m_type = m_type
    self.info = info
    self.length = length
    self.hr_message = self.to_string()
  
  def to_string(self):
    encodings = [
      f" SoS",
      f" Sign of Life {self.game_instance.sol_types[self.m_type].name}",
      f" Target Found {self.game_instance.pois[self.info].name}",
      f" Need {self.game_instance.items[self.info].name}",
      f" Target Saved: {self.game_instance.pois[self.info]}",
      f" Roger"
    ]
    return f"[{self.x}, {self.y}]"+encodings[self.m_type]