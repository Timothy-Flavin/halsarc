import numpy as np
from TerrainGeneration import GameMap 
from River import RiverTile 
from Grass import GrassTile 

# arr = np.array([
#   [1,2,3],
#   [4,5,6],
#   [7,8,9],
# ])
# print(arr)
# print(arr[0,1])
# print(arr[2,0])
# exit()

test_map = GameMap([10,10], [GrassTile(0), RiverTile(1, [0])])
test_map.wave_function_collapse()

print(test_map.final_tile_types)