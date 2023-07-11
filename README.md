# Department-Training
A group of agents is called a department and this repo is a MARL experiment using pygame to train some agents

## Level Gen
### File Structure

Every Level has 4 required files in order for the game to load and process them: **Agents.json**, **Hidden_Entities.json**, **Map.npy**, and **Tiles.json**.

### Agents.json
This file describes the different kind of searhcing agents that can be drawn from when starting a level. These attributes are subject to change (mostly additions), but you will be notified if they are.
```
{
  "AgentName1": {
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
    "visibilities":{            // Level of detail seen in different tiles
      "grass":1.0,
      "river":1.0,
      "ocean":1.0,
      "forest":0.8,
      "mountain":1.0,
      "peak":1.0,
      "shore": 1.0
    }
  },
"AgentName2": ...
}
```

### Hidden_Entities.json
This file is used to describe the persons or points of interest in the world which are being searched for. So far only persons of interest are implemented.

```
{
  "HiddenName1":{   
    "speed":0.3,               // Speed that this entity moves
    "active_time":10.0,        // time before this entity disappears forever
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
    "camo":0.5                 // Difficulty to be spotted, this is weighed against the visibility modifiers of the agents
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

### Generating a level from scratch
By Running PngToMap.py and supplying a level folder with a map.png present, a map will be generated in the form of a numpy array of tile id's for the game to use.
Just change the `level_name="Island"` to the folder you create

## Game use

The environment uses the PettingZoo API from FarmaFoundation. An Example of how to initiate and run the eonvironment is shown here:

```
agents = ["Human","RoboDog","Drone"]   # Agents list by name which will participate
pois = ["Child", "Child", "Adult"]     # hidden entities by name
premade_map = np.load("../LevelGen/Island/Map.npy")
game = sar_env(display=True, tile_map=premade_map, agent_names=agents, poi_names=pois)
state, info = game.start()             # Get initial state and game instance to choose actions
controller = player_controller(None)   # Can be whatever you want it to be. This one does keyboard events
terminated = False

while not terminated:
  actions = np.zeros((len(agents),2))
  messages = np.zeros((len(agents),2)) # In Progress implementation
  for i,a in enumerate(agents):
    actions[i] = controller.choose_action(state=state, game_instance=game)
  state, rewards, terminated, truncated, info =game.step(actions=actions, messages=messages)
```

### Actions Shape
Right now, the only actions are x and y direction magnitudes so the actions array is `[len(agents),2]`. This will change if more actions such as resting are added. messages are not yet defined. The state comes in two parts, the map part and the object part. 

#### Map Part
The map part consists of a grid for each agent with two channels of size `H = W = 2*max_effective_view_range + 1` where each grid is centered at it's agent. The max effective view range is the farthest that any of the agents could possibly see. For grounded agents this means the agent with the highest view range on the highest altitude tile. The channels are static and dynamic where static is tile id and dynamic is whether or not the tile has an ongoing event such as fire. For now dynamic is always zero. The final shape of this part is then `[num_agents, W, H, 2]`. 

#### Object Part
The object part of the state comes as an array `[num_agents, num_objects, 4]` 
