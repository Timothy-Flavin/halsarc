import numpy as np
from game import sar_env
import pickle

agents = ["Human","RoboDog","Drone"]
pois = ["Child", "Child", "Adult"]
premade_map = np.load("../LevelGen/Island/Map.npy")
game = sar_env(display=True, tile_map=premade_map, agent_names=agents, poi_names=pois)
state, info = game.start()
terminated = False

def player_controls(inp):
  dx = 0
  dy = 0
  if 's' in inp:
    dy+=1
  if 'w' in inp:
    dy-=1
  if 'd' in inp:
    dx+=1
  if 'a' in inp:
    dx-=1
  temp = np.array([dx, dy], dtype="float32")
  if dx != 0 or dy != 0:
    temp/=np.linalg.norm(temp)
  return temp

state_record = []  # keeps a memory of the game states
action_record = [] # keeps a memory of all the actions taken
reward_record = [] # keeps a memory of the resulting rewards
while not terminated:
  state_record.append(state)
  print(state_record[-1]['view'].shape)
  print(state_record[-1]['object_state'].shape)
  print(state_record[-1]['memory'].shape)
  actions = np.zeros((len(agents),2))
  messages = np.zeros((len(agents),2))
  for i,a in enumerate(agents):
    dir = input(f"input for agent {a}")
    actions[i] = player_controls(dir)
  state, rewards, terminated, truncated, info =game.step(actions=actions, messages=messages)
  action_record.append(np.copy(actions))
  reward_record.append(np.copy(rewards))

action_record = np.array(action_record)
reward_record = np.array(reward_record)

np.save("human_action_record",action_record)
np.save("human_reward_record",reward_record)
filehandler = open("agents.pkl", 'wb') 
pickle.dump(agents, filehandler)
filehandler = open("human_state_record.pkl", 'wb') 
pickle.dump(state_record, filehandler)