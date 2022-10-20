import numpy as np

def encode_state(game_instance, id):
  pov_obj = game_instance.get_entity_by_id(id)
  return id
