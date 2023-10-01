import numpy as np
from halsarc.Game.game import sar_env
import pickle
import os
import time

class player_recorder():
  def __init__(self, player, agents, pois, premade_map, max_agents, exp_reward=0.005, data_folder="./human_data/"):
    self.data_folder = data_folder
    self.max_agents = max_agents
    self.agents = agents #["Human", "RoboDog", "Drone"]
    self.pois = pois#["Child", "Child", "Adult"]
    self.premade_map = premade_map
    self.exp_reward= exp_reward
    self.active_player = player
    if not os.path.exists(data_folder):
      os.mkdir(data_folder)

  def player_controls(self,inp):
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

  def class_to_action(self,action):
    if action == 0: # none
      return np.array([0,-1])
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


  def record(self):
    print(self.premade_map.shape)
    self.game = sar_env(display=True, 
                        tile_map=self.premade_map, 
                        agent_names=self.agents, 
                        poi_names=self.pois,
                        max_poi=3,
                        explore_multiplier=self.exp_reward,
                        player=self.active_player)
    state, info = self.game.start()
    terminated = False
    dirs = ['w','a','s','d','wd','ds','sa','aw','']
    ai_type="trees"

    sk_agents={}
    print("record player path")
    print(os.path.dirname(os.path.dirname(__file__))+f"/Agents/{ai_type}")
    f = os.path.dirname(os.path.dirname(__file__))+f"/Agents/{ai_type}"
    fdirs = os.listdir(os.path.dirname(os.path.dirname(__file__))+f"/Agents/{ai_type}")
    for f in fdirs:
      print(f)
      try:
        filehandler = open(f"../Agents/{ai_type}/{f}", 'rb') 
        name = f.split("_")[0]
        print(name)
        print(f)
        sk_agents[name]=(pickle.load(filehandler))
      except:
        print("crap") 

    
    state_record = []  # keeps a memory of the game states
    action_record = [] # keeps a memory of all the actions taken
    reward_record = [] # keeps a memory of the resulting rewards
    deltat = 200
    begin_sim=False

    while not terminated:
      start = time.time_ns()
      # Don't step the environment until input is recorded
      if not begin_sim:
        info.__look_for_key_press__()
        if (info.player_input["W"] 
        or info.player_input["A"] 
        or info.player_input["S"]  
        or info.player_input["D"]):
          begin_sim=True
      else:
        
        actions = np.zeros((len(self.agents),14+info.max_agents))
        messages = np.zeros((len(self.agents),14+info.max_agents+len(info.agent_types)))
        for i,a in enumerate(self.agents):
          dir=''
          if self.active_player == i:
            if info.player_input["W"]:
              dir+="w"
            if info.player_input["A"]:
              dir+="a"
            if info.player_input["S"]:
              dir+="s"
            if info.player_input["D"]:
              dir+="d"
            actions[i,0:2] = self.player_controls(dir)
          elif a in sk_agents:
            sk_state = [np.concatenate((state['view'][i].flatten(),state['object_state'][i].flatten(),state['memory'][i].flatten()))]
            actions[i] = self.class_to_action(sk_agents[a].predict(sk_state))
          else:
            actions[i,0:2] = self.player_controls(dir) # if not a player and no skmodel then do action ''
        
        if not self.game.agents[self.active_player].destroyed or terminated or truncated:
          state_record.append(state)

        state, rewards, terminated, truncated, info = self.game.step(actions=actions)
        ##print(actions.shape)
        #print(actions[self.active_player].shape)
        #input()
        if not self.game.agents[self.active_player].destroyed or terminated or truncated:
          action_record.append(np.copy(info.actions[self.active_player]))
          reward_record.append(np.copy(rewards[self.active_player]))
        
      
      elapsed = (time.time_ns()-start)//1000000
      if not self.game.agents[self.active_player].destroyed:
        info.wait(deltat-elapsed)
      #time.sleep(100-elapsed)

    action_record = np.array(action_record)
    reward_record = np.array(reward_record)
    print(f"action shape: {action_record.shape}")

    try:
      al = np.load(self.agents[self.active_player]+"_action_record.npy")
      print(f"loaded shape: {al.shape}")
      print(f"game shape: {al.shape}")
      action_record = np.concatenate((al, action_record))
      print(f"after concat shape: {action_record.shape}")
    except:
      print("No action record found for: " + self.agents[self.active_player])

    try:
      reward_record = np.concatenate((np.load(self.agents[self.active_player]+"_reward_record.npy"), reward_record))
    except:
      print("No reward record found for: " + self.agents[self.active_player])

    np.save(f"{self.data_folder}{self.agents[self.active_player]}_action_record.npy",action_record)
    np.save(f"{self.data_folder}{self.agents[self.active_player]}_reward_record.npy",reward_record)
    filehandler = open(f"{self.data_folder}agents.pkl", 'wb') 
    pickle.dump(self.agents, filehandler)
    oldstate=[]

    try:
      filehandler = open(f"{self.data_folder}{self.agents[self.active_player]}_state_record.pkl", 'rb') 
      oldstate = pickle.load(filehandler)
    except:
      print("no old state dump found")
    s=oldstate+state_record
    print(len(s))
    filehandler = open(f"{self.data_folder}{self.agents[self.active_player]}_state_record.pkl", 'wb') 
    pickle.dump(oldstate+state_record, filehandler)


if __name__=="__main__":
  premade_map = np.load('../LevelGen/Island/Map.npy')
  print(premade_map.shape)
  rcdr = player_recorder(player=1,
                         agents=['Human','Drone','RoboDog'],
                         pois=['Child','Child','Adult'],
                         premade_map=premade_map,
                         max_agents=3,
                         data_folder="./recorded_data/")
  rcdr.record()