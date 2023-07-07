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
"Adult":{   
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
```
