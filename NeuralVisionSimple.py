import numpy as np

# enemies, allies, and projectiles will all be encoded as their
# x,y locations. to capture velocity use frame stacking the number
# of each will also be recorded as the first 4 columns of the 
# returned data

def encode_state(game_instance, id, n_allies, n_enemies, n_neutral, n_projectiles):
  enemies = []
  allies = []
  neutral = []
  projectiles = []
  pov_obj = game_instance.get_entity_by_id(id)

  # Sort the game objects into enemies and allies 
  for obj in game_instance.objects:
    if obj.entity_type == None:
      continue
    elif obj.entity_type == "projectile":
      if obj.team == pov_obj.team:
        continue
      else:
        projectiles.append(obj)
    elif obj.entity_type == "combatant":
      if obj.team == pov_obj.team:
        allies.append(obj)
      elif obj.team == "grey":
        enemies.append(obj)
      else:
        neutral.appen(obj)


  

