from Tile import Tile

# Human, Dog, Drone
class RiverTile(Tile):
  def __init__(self, id, land_ids, num_agent_types=3, agent_speed_multipliers = None, agent_visibility_multipliers = None, agent_traversable = None, flamable=True, color=[150,150,150]):
    super(RiverTile, self).__init__(id, "RiverTile", 3, [0.25,0,1], [1,1,1], [1,0,1], False, [0,0,255])
    self.land_ids = land_ids

  def wave_function_legality(self, y: int, x: int, map_state):
    possible_river = 0
    confirmed_river = 0
    total_river = 0
    for yi in range(y-1,y+1):
      if yi>-1 and yi<map_state.shape[1]:
        for xi in range(x-1,x+1):
          if xi==x and yi==y:
            continue
          if xi>-1 and xi<map_state.shape[0]:
            total_river += 1
            if map_state[yi,xi,self.id] == 1:# and (yi==y or xi==x):
              possible_river += 1
            elif map_state[yi,xi,self.id] == -1:#  and (yi==y or xi==x):
              confirmed_river += 1
    if possible_river + confirmed_river > 0 and possible_river + confirmed_river < 5:
      return 1
    else:
      return 0

  def old_wfl(self, x: int, y: int, map_state):
    num_river_bordering = 0 # number of tiles that could be river but not other legal borders
    num_land_possible = 0 # number of bordering tiles that could be legal borders
    num_bordering = 0 # number of tiles bordering total 
    river_border_possible = False # if there is still a legal river tile in this tile's space

    for yi in range(y-1,y+1):
      if yi>-1 and yi<map_state.shape[0]:
        for xi in range(x-1,x+1):
          # Skip checking itself
          if xi==x and yi==y:
            continue
          if xi>-1 and xi<map_state.shape[1]:
            num_bordering +=1
            land_possible = False
            for lid in self.land_ids:
              if map_state[y,x,lid]:
                num_land_possible += 1
                land_possible=True
                break
            if map_state[y,x,self.id] and not land_possible:
              num_river_bordering += 1
            if map_state[y,x,self.id]: 
              river_border_possible = True
    if num_river_bordering < 4 and river_border_possible and num_river_bordering + num_land_possible == num_bordering:
      return 1
    else:
      return 0
            
              
