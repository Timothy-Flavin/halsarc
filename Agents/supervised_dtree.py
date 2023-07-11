import numpy as np
import pickle
from sklearn.tree import DecisionTreeClassifier as dtree

har = np.load("../Game/human_action_record.npy")
hrr = np.load("../Game/human_reward_record.npy")
filename = "../Game/human_state_record.pkl"
hsr=pickle.load(open('../Game/human_state_record.pkl','rb'))
agents = pickle.load(open('../Game/agents.pkl','rb'))

print(agents)
print(hsr[0])
print(har.shape)
print(hrr.shape)


def action_to_class(action):
  if action[0]==0 and action[1]==0:
    return 0 # none
  if action[0] == 0 and action[1] < 0:
    return 1 # w
  if action[0] > 0 and action[1] < 0:
    return 2 # wd
  if action[0] > 0 and action[1] == 0:
    return 3 # d
  if action[0] > 0 and action[1] > 0:
    return 4 # ws
  if action[0] == 0 and action[1] > 0:
    return 5 # s
  if action[0] < 0 and action[1] > 0:
    return 6 # as
  if action[0] < 0 and action[1] == 0:
    return 7 # a
  if action[0] < 0 and action[1] < 0:
    return 8 # aw
  

print("entering loop")
data = {}
for i,a in enumerate(agents):
  actions = np.array([action_to_class(a) for a in har[:,i]]) # all the actions for agent a
  states = np.array([np.concatenate((h['view'][i].flatten(),h['object_state'][i].flatten(),h['memory'][i].flatten())) for h in hsr]) # all the states agent a saw
  rewards = hrr[:,i] 
  print(rewards.shape)

  data[a] = { 'actions':actions[rewards!=0], 'states':states[rewards!=0,:] }
  print(data[a]['actions'].shape)
  print(data[a]['states'].shape)
trees={}
for a in agents:
  trees[a] = dtree()
  trees[a].fit(data[a]['states'], data[a]['actions'])
  print(f"Done Training Tree {a}")

def class_to_action(action):
  if action == 0: # none
    return np.array([0,0])
  if action == 1: # w
    return np.array([0,-1])
  if action == 2: # wd
    return np.array([1,-1])
  if action == 3: # d
    return np.array([1,0])
  if action == 4: # ds
    return np.array([1,1])
  if action == 5: # s
    return np.array([0,1])
  if action == 6: # sa
    return np.array([-1,1])
  if action == 7: # a
    return np.array([-1,0])
  if action == 8: # aw
    return np.array([-1,-1])


# Time to play the game with these trees
import sys
sys.path.insert(1, '../Game') # lets us import game from another folder
from game import sar_env
import pickle

agents = ["Human","RoboDog","Drone"]
pois = ["Child", "Child", "Adult"]
premade_map = np.load("../LevelGen/Island/Map.npy")
game = sar_env(display=True, tile_map=premade_map, agent_names=agents, poi_names=pois)
state, info = game.start()
terminated = False

while not terminated:
  actions = np.zeros((len(agents),2))
  messages = np.zeros((len(agents),2))
  for i,a in enumerate(agents):
    tree_state = [np.concatenate((state['view'][i].flatten(),state['object_state'][i].flatten(),state['memory'][i].flatten()))]
    #print(class_to_action(trees[a].predict(tree_state)))
    actions[i] = class_to_action(trees[a].predict(tree_state)) # gets the tree's prediction class back to an action
  state, rewards, terminated, truncated, info = game.step(actions=actions, messages=messages)

for a in agents:
  pred = trees[a].predict([np.concatenate((hsr[0]['view'][i].flatten(),hsr[0]['object_state'][i].flatten(),hsr[0]['memory'][i].flatten()))])
  print(pred)