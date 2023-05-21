# Simple pygame program
# Import and initialize the pygame library
import pygame
pygame.init()

import time
from player import player
import numpy as np
# Set up the drawing window
screen = pygame.display.set_mode([500, 500])

class Tile():
  def __init__(self, agent_speeds = [1,1,1], agent_visibe = [1,1,1], border_tiles=["Plains", "Hills","River","Mountain","Ocean","Forest","HillyForest","Shore"], flamable=True, color=[150,150,150]):
    self.agent_speeds = np.array(agent_speeds)
    self.agent_visibe = np.array(agent_visibe)
    self.flamable = flamable
    self.color = color
  def legal(self, )

class Searcher():
  # Speed is how many times per frame the agent can move
  def __init__(self, speed=0.1, comspeed=1.0/30.0, view_range=4, view_resolution=1, operation_time=200):
    self.speed = speed
    self.comspeed = comspeed
    self.view_range = view_range
    self.view_resolution = view_resolution
    self.operation_time = operation_time
    self.time_left = operation_time


class game_instance():
  # Run until the user asks to quit  
  tile_names = ["Plains", "Hills","River","Mountain","Ocean","Forest","HillyForest","Shore"]
  agent_names = ["Human", "RoboDog", "Drone"]
  tile_types = {
    "Plains": Tile(border_tiles=["Plains","Hills","River","Forest","HillyForest"]),
    "Hills": Tile(border_tiles=["Plains", "Hills","River","Mountain","HillyForest"], agent_speeds = [1,0.5,1]),
    "River": Tile(border_tiles=["Plains", "Hills","River","Mountain","Ocean","Shore"], agent_speeds = [1,1,1]),
    "Mountain": Tile(border_tiles=["Hills","River","Mountain","HillyForest"], agent_speeds = [1,1,1]),
    "Ocean": Tile(border_tiles=["Ocean","Shore"], agent_speeds = [1,1,1]),
    "Forest": Tile(border_tiles=["Plains","River","Forest","HillyForest"], agent_speeds = [1,1,1]),
    "HillyForest": Tile(border_tiles=["Hills","Mountain","Forest","HillyForest"], agent_speeds = [1,1,1]),
    "Shore": Tile(border_tiles=["Plains","River","Ocean","Shore"], agent_speeds = [1,1,1]),
  }
  Agent_types = {
    "Human": Searcher(view_resolution=3),
    "RoboDog": Searcher(speed=0.05, comspeed=1.0/5.0, view_range=3, view_resolution=2, operation_time=150),
    "Drone": Searcher(speed=0.5, comspeed=1.0/5.0, view_range=12, view_resolution=1, operation_time=100)
  }

  
  def __init__(self, screen, display=False, objects=[], map=None, map_size = [32,32]):
    self.display = display
    self.running = True
    self.objects = objects
    self.screen = screen
    self.player_input = {'W': False, 'A': False, 'S':False, 'D': False}
    self.mouse_pos=None
    self.clicked=False
    self.current_id=1
    if map is None:
      self.map = self.generate_map(map_size)


  def generate_map(self, map_size)

  def add_entity(self, obj):
    obj.id = self.current_id
    self.current_id += 1 
    self.objects.append(obj)

  def get_entity_by_id(self, id):
    for i in self.objects:
      if i.id == id:
        return i
    return None

  def game_logic(self, delta_time):
    for i in self.objects:
      if i.destroyed:
        self.objects.remove(i)
      else:  
        i.update(delta_time, self)

  def draw_game(self):
    # Fill the background with white
    if self.display:
      self.screen.fill((255, 255, 255))

    # Draw a solid blue circle in the center
    if self.display:
      for i in self.objects:
        if i.team == "red":
          i.render(color = (255,0,0), screen = self.screen)
        if i.team == "grey":
          i.render(color = (125,125,125), screen = self.screen)
        if i.team == "green":
          i.render(color = (0,255,0), screen = self.screen)
      #pygame.draw.circle(screen, (0, 0, 255), (self.x, self.y), 75)

    # Flip the display
    if self.display:
      pygame.display.flip()
  
  def handle_mouse_event(self, event):
    if event.type == pygame.MOUSEBUTTONDOWN and not self.clicked:
      self.mouse_pos = pygame.mouse.get_pos()
      self.clicked = True
    elif event.type == pygame.MOUSEBUTTONUP:
      self.clicked = False
 
  # Set the state of user input
  def handle_key_press(self, event):
    handled = False
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_w:
        self.player_input['W'] = True
      if event.key == pygame.K_a:
        game.player_input['A'] = True
      if event.key == pygame.K_s:
        game.player_input['S'] = True
      if event.key == pygame.K_d:
        game.player_input['D'] = True
      handled=True
    elif event.type == pygame.KEYUP:
      if event.key == pygame.K_w:
        game.player_input['W'] = False
      if event.key == pygame.K_a:
        game.player_input['A'] = False
      if event.key == pygame.K_s:
        game.player_input['S'] = False
      if event.key == pygame.K_d:
        game.player_input['D'] = False
      handled=True
    return handled
game = game_instance(screen= screen, display=True, objects=[
  player("red", pygame, np.array([100,200], dtype="float32"), speed=20, size=20),
  player("green", pygame, np.array([400,400], dtype="float32"), speed=3, size=10),
  player("grey", pygame, np.array([250,250], dtype="float32"), speed=10, size=30)
  ],)

fps=30
start = time.time()
prev_time = time.time()
frame_time = 0

while game.running:
  delta_time = time.time() - prev_time
  prev_time = time.time()
  frame_time+=delta_time
  # Did the user click the window close button?
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      game.running = False
    game.handle_key_press(event)
    game.handle_mouse_event(event)
    
      # Done! Time to quit.
  game.game_logic(delta_time)

  if frame_time >= 1/fps:
    game.draw_game()
    frame_time=0
  
pygame.quit()