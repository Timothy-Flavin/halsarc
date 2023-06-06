from Tile import Tile

# Human, Dog, Drone
class GrassTile(Tile):
  def __init__(self, id, num_agent_types=3, agent_speed_multipliers = None, agent_visibility_multipliers = None, agent_traversable = None, flamable=True, color=[150,150,150]):
    super(GrassTile,self).__init__(id, "GrassTile", 3, [1,1,1], [1,1,1], [1,1,1], False, [0,255,0])

  def wave_function_legality(self, x: int, y: int, map_state):
    return 1
            
              
