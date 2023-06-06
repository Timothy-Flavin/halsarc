from River import RiverTile
from Grass import GrassTile
from Tile import Tile
import numpy as np
import random

class GameMap:
  def __init__(self, size, tiles):
    self.size = size # map size: width x height
    self.tiles = tiles # type tile. containes the rules for generating the level
    self.map_tiles = np.ones((size[0],size[1], len(tiles)), dtype=np.int32) # W x H x num_tile_types
    self.final_tile_types = np.ones((size[0],size[1]), dtype=np.int32) # final map after wfc
    self.checkpoints = [] # saves of the map before each random decision that can be returned to
    self.checkpoints.append(np.copy(self.map_tiles))  
    self.checkpoint_decisions = []  # the random choice that was made after a checkpoint
  

  def set_tile(self, r, c, ty, verbose=False):
    if verbose:
      print(f"setting tile {r},{c} to {ty}: {self.tiles[ty].name}")
    self.map_tiles[r,c,:] = np.zeros(len(self.tiles))
    self.map_tiles[r,c,ty] = -1

  def update_tile_legality(self, x, y, z):
    for r in range(self.size[1]):
      for c in range(self.size[0]):
        for t in range(len(self.tiles)):
          if self.map_tiles[r,c,t] == 1:
            self.map_tiles[r,c,t] = self.tiles[t].wave_function_legality(r,c,self.map_tiles)
          if self.map_tiles[r,c,t] == 1: # if this tile is legal check if it would make the just placed tile illegal
            temp = self.map_tiles[r,c]
            self.map_tiles[r,c] = np.zeros(len(self.tiles))
            self.map_tiles[r,c,t] = -1
            legal = self.tiles[z].wave_function_legality(x,y,self.map_tiles)
            self.map_tiles[r,c] = temp
            if legal != 1:
              self.map_tiles[r,c,t] = 0
    
  def wave_function_collapse(self, verbose=False):
    x=0
    y=0
    z=0
    while True:
      if verbose:
        input("Next step?")
        print(np.sum(self.map_tiles))
        print(f"num check: {len(self.checkpoints)}")
      if np.sum(self.map_tiles) == -1*self.size[0]*self.size[1]: # if all tiles are 0s and -1 then we have a final map
        if verbose:
          print("done finding tiles")
        self.final_tile_types = np.argmin(self.map_tiles, axis=2)
        return True
      moves = np.sum(self.map_tiles, axis=2)
      if verbose:
        print(moves)
      if np.where(moves==0)[0].shape[0] == 0: # If there are legal moves left
        forced_moves = np.where(moves==1)
        if forced_moves[0].shape[0] > 0: # If we have tiles with only 1 possible move
          if verbose:
            print(f"forced move at {forced_moves[0][0]}, {forced_moves[1][0]}")
          x, y, z = forced_moves[0][0], forced_moves[1][0], np.argmax(self.map_tiles[forced_moves[0][0],forced_moves[1][0],:])
          self.set_tile(x,y,z)
        else:
          self.checkpoints.append(np.copy(self.map_tiles))
          possible_moves = np.where(moves > 1)
          possible_moves = np.where(moves[possible_moves] == min(moves[possible_moves]))
          if verbose:
            print(f"Possible moves: {possible_moves}")
          rand_choice = random.randrange(0,possible_moves[0].shape[0])
          rand_type = random.randrange(0,len(self.tiles))
          if verbose:
            print(f"Random move at {possible_moves[0][rand_choice]}, {possible_moves[1][rand_choice]}: {rand_type}")
          self.checkpoint_decisions.append([possible_moves[0][rand_choice], possible_moves[1][rand_choice], rand_type])
          x, y, z = possible_moves[0][rand_choice], possible_moves[1][rand_choice], rand_type
          self.set_tile(x,y,z)

        self.update_tile_legality(x,y,z)
      else: # if there are tiles with no legal moves
        if verbose:
          print("no legals, going back to checkpoint")
        if len(self.checkpoint_decisions) == 0:
          return False
        self.map_tiles = self.checkpoints.pop()
        bad_move = self.checkpoint_decisions.pop()
        self.map_tiles[bad_move[0],bad_move[1],bad_move[3]] = 0

      