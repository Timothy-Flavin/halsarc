import numpy as np
from game import sar_env
import pickle
import os

class player_recorder():
  def __init__(self, agents, pois, level_dir):
    self.agents = agents #["Human", "RoboDog", "Drone"]
    self.pois = pois#["Child", "Child", "Adult"]
    self.premade_map = np.load(f"{level_dir}/Map.npy")

  def record(self):
    self.game = sar_env(display=True, tile_map=self.premade_map, agent_names=self.agents, poi_names=self.pois)
    state, info = self.game.start()
    terminated = False
    dirs = ['w','a','s','d','wd','ds','sa','aw','']
    active_player = 0
    ai_type="trees"

    sk_agents={}
    print("record player path")
    print(__file__)
    fdirs = os.listdir(__file__+f"../Agents/{ai_type}")
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

    def class_to_action(action):
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



    import time
    state_record = []  # keeps a memory of the game states
    action_record = [] # keeps a memory of all the actions taken
    reward_record = [] # keeps a memory of the resulting rewards
    deltat = 100
    begin_sim=False

    while not terminated:
      start = time.time_ns()
      # Don't step the environment until input is recorded
      if not begin_sim:
        info.look_for_key_press()
        if (info.player_input["W"] 
        or info.player_input["A"] 
        or info.player_input["S"]  
        or info.player_input["D"]):
          begin_sim=True
      else:
        state_record.append({
          'view':state['view'][active_player],
          'object_state':state['object_state'][active_player],
          'memory':state['memory'][active_player],
        })
        actions = np.zeros((len(self.agents),2))
        messages = np.zeros((len(self.agents),2))
        for i,a in enumerate(self.agents):
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
          elif a in sk_agents:
            sk_state = [np.concatenate((state['view'][i].flatten(),state['object_state'][i].flatten(),state['memory'][i].flatten()))]
            actions[i] = class_to_action(sk_agents[a].predict(sk_state))
          else:
            actions[i] = player_controls(dir) # if not a player and no skmodel then do action ''
        state, rewards, terminated, truncated, info = self.game.step(actions=actions, messages=messages)
        ##print(actions.shape)
        #print(actions[active_player].shape)
        #input()
        action_record.append(np.copy(actions[active_player]))
        reward_record.append(np.copy(rewards[active_player]))
      
      elapsed = (time.time_ns()-start)//1000000
      info.wait(deltat-elapsed)
      #time.sleep(100-elapsed)

    action_record = np.array(action_record)
    reward_record = np.array(reward_record)
    print(f"action shape: {action_record.shape}")

    try:
      al = np.load(self.agents[active_player]+"_action_record.npy")
      print(f"loaded shape: {al.shape}")
      print(f"game shape: {al.shape}")
      action_record = np.concatenate((al, action_record))
      print(f"after concat shape: {action_record.shape}")
    except:
      print("No action record found for: " + self.agents[active_player])

    try:
      reward_record = np.concatenate((np.load(self.agents[active_player]+"_reward_record.npy"), reward_record))
    except:
      print("No reward record found for: " + self.agents[active_player])

    np.save(self.agents[active_player]+"_action_record",action_record)
    np.save(self.agents[active_player]+"_reward_record",reward_record)
    filehandler = open("agents.pkl", 'wb') 
    pickle.dump(self.agents, filehandler)
    oldstate=[]

    try:
      filehandler = open(self.agents[active_player]+"_state_record.pkl", 'rb') 
      oldstate = pickle.load(filehandler)
    except:
      print("")
    s=oldstate+state_record
    print(len(s))
    filehandler = open(self.agents[active_player]+"_state_record.pkl", 'wb') 
    pickle.dump(oldstate+state_record, filehandler)

