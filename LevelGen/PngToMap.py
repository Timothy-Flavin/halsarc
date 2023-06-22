from PIL import Image
import numpy as np
import json

im = Image.open("map1.png")
print(im)
rawmap = np.array(im)
print(rawmap)
print(rawmap.shape)

tile_list = json.load(open("Tiles.json"))
numpy_map = np.zeros((rawmap.shape[0],rawmap.shape[1]), np.int64)-1

for r in range(rawmap.shape[0]):
  for c in range(rawmap.shape[1]):
    for i,tile in enumerate(tile_list):
      if rawmap[r,c,0] == tile["color"][0] and rawmap[r,c,1] == tile["color"][1] and rawmap[r,c,2] == tile["color"][2]:
        numpy_map[r,c] = i

for r in range(rawmap.shape[0]):
  print(numpy_map[r,:])
np.save("HandMadeMap.npy",numpy_map)