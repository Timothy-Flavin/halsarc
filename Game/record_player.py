import numpy as np
from game import sar_env
import pickle

agents = ["Human", "RoboDog", "Drone"]
pois = ["Child", "Child", "Adult"]
premade_map = np.load("../LevelGen/Island/Map.npy")
game = sar_env(display=True, tile_map=premade_map, agent_names=agents, poi_names=pois)
state, info = game.start()
terminated = False
dirs = ['w','a','s','d','wd','ds','sa','aw','']
active_player = 1

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

import time
state_record = []  # keeps a memory of the game states
action_record = [] # keeps a memory of all the actions taken
reward_record = [] # keeps a memory of the resulting rewards
deltat = 0.1

while not terminated:
  start = time.time_ns()
  state_record.append({
    'view':state['view'][active_player],
    'object_state':state['object_state'][active_player],
    'memory':state['memory'][active_player],
  })
  #print(state_record[-1]['view'].shape)
  #print(state_record[-1]['object_state'].shape)
  #print(state_record[-1]['memory'].shape)
  actions = np.zeros((len(agents),2))
  messages = np.zeros((len(agents),2))
  for i,a in enumerate(agents):
    
    dir=''
    if active_player == i:
      if info.player_input["W"]:
        dir+="w"
      if info.player_input["A"]:
        dir+="a"
      if info.player_input["S"]:
        dir+="s"
      if info.player_input["D"]:
        dir+="d"
    actions[i] = player_controls(dir)
  state, rewards, terminated, truncated, info = game.step(actions=actions, messages=messages)
  ##print(actions.shape)
  #print(actions[active_player].shape)
  #input()
  action_record.append(np.copy(actions[active_player]))
  reward_record.append(np.copy(rewards[active_player]))
  elapsed = (time.time_ns()-start)//1000000
  #print(elapsed)

  info.wait(20-elapsed)
  #time.sleep(100-elapsed)

action_record = np.array(action_record)
reward_record = np.array(reward_record)
print(f"action shape: {action_record.shape}")

try:
  al = np.load(agents[active_player]+"_action_record.npy")
  print(f"loaded shape: {al.shape}")
  print(f"game shape: {al.shape}")
  action_record = np.concatenate((al, action_record))
  print(f"after concat shape: {action_record.shape}")
except:
  print("No action record found for: " + agents[active_player])

try:
  reward_record = np.concatenate((np.load(agents[active_player]+"_reward_record.npy"), reward_record))
except:
  print("No reward record found for: " + agents[active_player])

np.save(agents[active_player]+"_action_record",action_record)
np.save(agents[active_player]+"_reward_record",reward_record)
filehandler = open("agents.pkl", 'wb') 
pickle.dump(agents, filehandler)
oldstate=[]

try:
  filehandler = open(agents[active_player]+"_state_record.pkl", 'rb') 
  oldstate = pickle.load(filehandler)
except:
  print("")
s=oldstate+state_record
print(len(s))
filehandler = open(agents[active_player]+"_state_record.pkl", 'wb') 
pickle.dump(oldstate+state_record, filehandler)

