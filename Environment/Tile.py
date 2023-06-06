import numpy as np

class Tile(object):
  def __init__(self, id, name = "default_tile_name", num_agent_types=3, agent_speed_multipliers = None, agent_visibility_multipliers = None, agent_traversable = None, flamable=True, color=[150,150,150]):
    if agent_speed_multipliers is not None:
      self.speeds = np.array(agent_speed_multipliers)
    else:
      self.speeds = np.ones(num_agent_types)

    if agent_visibility_multipliers is not None:
      self.visibilities = np.array(agent_visibility_multipliers)
    else:
      self.visibilities = np.ones(num_agent_types)

    if agent_traversable is not None:
      self.traversability = np.array(agent_traversable)
    else:
      self.traversability = np.ones(num_agent_types)

    self.flamable = flamable
    self.color = color

    self.id = id
    self.name = name
    self.num_agent_types = num_agent_types

  def wave_function_legality(self, x: int, y: int, map_state) -> int:
    """Load in the file for extracting text."""
    return 1