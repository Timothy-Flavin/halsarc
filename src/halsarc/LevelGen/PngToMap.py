from PIL import Image
import numpy as np
import json

def convert_to_npy(level_name):
  im = Image.open(f"{level_name}/map.png")
  rawmap = np.array(im)
  print(f"making map with shape: {rawmap.shape}")

  tile_list = json.load(open(f"{level_name}/Tiles.json"))
  numpy_map = np.zeros((rawmap.shape[0],rawmap.shape[1]), np.int64)-1

  for r in range(rawmap.shape[0]):
    for c in range(rawmap.shape[1]):
      for i,tile in enumerate(tile_list):
        if rawmap[r,c,0] == tile["color"][0] and rawmap[r,c,1] == tile["color"][1] and rawmap[r,c,2] == tile["color"][2]:
          numpy_map[r,c] = i
  #for r in range(rawmap.shape[0]):
    #print(numpy_map[r,:])
  np.save(f"{level_name}/Map.npy",numpy_map)