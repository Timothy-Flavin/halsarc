# halsarc Heterogeneous Agents Learning Search and Rescue Communication 
This project is intended to serve as a flexible engine for search-type tasks in multi-agent reinforcement learning.
The api is broken down into sections for generating levels, defining agent and person of interest parameters, and finally the environment api and state encodings. 

# Instalation 

```pip install -i https://test.pypi.org/simple/ halsarc```

### File Structure

Every Level has 4 required files in order for the game to load and process them: **Agents.json**, **POI.json**, **Map.npy**, and **Tiles.json**.

### Agents.json
This file describes the different kind of searhcing agents that can be drawn from when starting a level. These attributes are subject to change (mostly additions), but you will be notified if they are.
```
{
  "AgentType1": {
    "view_range": number,      //radius of agent vision in number of tiles
    "speed": number,           //speed of agent, 1 is base
    "active_time": number,     // how much time an agent can stay active in "hours" 
    "grounded":true,           // if false, the agent's vision will not be affecred by elevation
    "color":[255,195,170,255], // Color that the agent is rendered
    "speeds": {                // Speed multipliers for traversing different tiles
      "grass":1.0,
      "river":0.2,
      "ocean":0.2,
      "forest":1.0,
      "mountain":0.7,
      "peak":0.4,
      "shore": 1.0
    },
  },
"AgentType2": ...
}
```

### POI.json
This file is used to describe the persons or points of interest in the world which are being searched for. So far only persons of interest are implemented.

```
{
  "HiddenName1":{   
    "speed":number,               // Speed that this entity moves
    "active_time":number,        // time before this entity disappears forever
    "color":[200,180,80,255],  // color to be rendered after found
    "moves":"random",          // used to denote the kind of movement. Only random implemented so far
    "speeds": {                // Speed multipliers on different tiles
      "grass":1.0,
      "river":0.2,
      "ocean":0.2,
      "forest":1.0,
      "mountain":0.7,
      "peak":0.4,
      "shore": 1.0
    },
  },
  "HiddenName2": { ... }, ...
}
```

### Tiles.json
This file describes the kinds of tiles which are present in the level. Each tile will need to be present in each of the agent's and Hidden Entities tile dependant attibute lists. If a tile is present in the Tiles.json file but not entities lists, an exception will be thrown. 

```
[
  {
    "name": "grass",
    "color": [0,255,0,255],      // how the tile is rendered
    "flammable": true,           // whether or not fire can spread here. Not Yet Implemented
    "altitude": 1.0,             // If a grounded agent is on this tile, how high it will be
    "cover":0.0                  // if this tile offeres a baseline cover
  },
  {
    "name": "river",
    "color": [100,100,255,255],
    "flammable": false,
    "altitude": 0.8,
    "cover":0.0
  },
  ...
]
```

### Generating map.npy from scratch
By Running PngToMap.py and supplying a level folder with a map.png present, a map will be generated in the form of a numpy array of tile id's for the game to use. 
Just change the `level_name="Island"` to the folder you create

## Game use

The environment uses the PettingZoo API from FarmaFoundation. An Example of how to initiate and run the eonvironment is shown here:

```
agents = ["Human","RoboDog","Drone"]   # Agents list by name which will participate
pois = ["Child", "Child", "Adult"]     # hidden entities by name
premade_map = np.load("../LevelGen/Island/Map.npy")
max_agents = 3 # this should be >= len(agents)

env = sar_env(max_agents=max_agents,display=True, tile_map=premade_map, agent_names=agents, poi_names=pois,seed=random.randint(0,10000),player=player_num,explore_multiplier=0.1)
state, info = env.start()             # Get initial state and game instance to choose actions

# The environment comes with three methods of vectorizing the state in order of decreasing complexity
state_sizes = [env.vec_state_size, self.vec_state_small_size, self.boid_state_size] 
controller = player_controller(None)   # Can be whatever you want it to be. This one does keyboard events
terminated = False

while not terminated:
  actions = np.zeros((len(agents),14+max_agents))
  for i,a in enumerate(agents):
    actions[i,:2] = controller.choose_action(state=state, game_instance=env)
  state, rewards, terminated, truncated, info = env.step(actions=actions)
```

### Actions Encoding

Agents can move and attempt to send messages on the radio. Movement is decided by the first two actions and whether
a message send is attempted is decided by the third action taken as a boolean value. The type of message is one of 
8 available message types: 
SoS, Sign of life found, PoI found, PoI needs X, Target saved, Roger, I want to go, You should go. Most messages are
broadcast, but for some applicablt messages a target is given. Commands may be followed using the Roger message type.

```
[
  0 xdir:float, # from -1 to 1 how much to move in the x direction
  1 ydir:float, # from -1 to 1 how much to move in the y direction
  2 message:boolean, # 0 to 1, if greater 0.5 means a message send will be attempted 
  3 xcommanddir, # if commanding another agent, this is the x direction used
  4 ycommanddir, # this is the y direction used
  5 magnitude:float, # this is for how many frames the command will stick rounded down
  6:14 one_hot_message_type, # argmax of (this dot legal messages) will decide the message type
  14:14+max_agents one_hot_target # the argmax of this will be the target of the message if applicable
]
```

### State vectorization

#### Radio state

#### Map Part
The map part consists of a grid for each agent with two channels of size `H = W = 2*max_effective_view_range + 1` where each grid is centered at it's agent. The max effective view range is the farthest that any of the agents could possibly see. For grounded agents this means the agent with the highest view range on the highest altitude tile. The channels are static and dynamic where static is tile id and dynamic is whether or not the tile has an ongoing event such as fire. For now dynamic is always zero. The final shape of this part is then `[num_agents, 4, W, H]`. The 4 refers to the 3 channels the agent can see. The first is altitude of the local tiles, the second is movespeed multipliers for the nearest tyles, and the last is a layer where PoI's leave tracks where each tile measures recency.  

#### Object Part
The object part of the state comes as an array `[num_agents, num_objects, 4]` 
