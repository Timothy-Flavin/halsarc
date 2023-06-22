#import sys
import math
#sys.path.append('../Environment')

# Simple pygame program
# Import and initialize the pygame library
import pygame
pygame.init()

import time
from player import player
import numpy as np
import random
import json
# Set up the drawing window
screen = pygame.display.set_mode([64*10, 48*10])
from searcher import searcher

class game_instance():

  def __init__(self, screen, display=False, objects=[], tile_map=None, map_size = [32,32]):
    self.draw_surface = pygame.Surface((screen.get_width(),screen.get_height()),pygame.SRCALPHA)
    self.display = display
    self.running = True
    self.objects = objects
    self.screen = screen
    self.player_input = {'W': False, 'A': False, 'S':False, 'D': False}
    self.mouse_pos=None
    self.clicked=False
    self.current_id=1
    random.seed(0)
    self.tile_map = tile_map
    self.debug_render = False
    self.tile_width = 1.0*screen.get_height()/tile_map.shape[0]
    self.clock = pygame.time.Clock()

    agent_blueprint = json.load(open("../LevelGen/Agents.json"))
    self.tiles = json.load(open("../LevelGen/Tiles.json"))
    #print(agent_blueprint)
    self.agents = []
    for agent in agent_blueprint:
      self.agents.append(searcher(agent, pygame)) 
      self.objects.append(self.agents[-1])

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
    self.screen.fill((0,0,0,255))
    self.draw_surface.fill((0,0,0,0))
    # Fill the background with white
    if self.display:
      self.screen.fill((255, 255, 255,0))
      for r in range(self.tile_map.shape[0]):
        for c in range(self.tile_map.shape[1]):
          trect = pygame.Rect(screen.get_width()*c/self.tile_map.shape[1],screen.get_height()*r/self.tile_map.shape[0], screen.get_width()/self.tile_map.shape[1],screen.get_height()/self.tile_map.shape[0])
          pygame.draw.rect(self.screen, self.tiles[self.tile_map[r,c]]["color"], trect)
    # Draw a solid blue circle in the center
    if self.display:
      for i in self.objects:
        i.render(color = i.color, screen = self.screen)
        if self.debug_render:
          i.debug_render(color = i.color, screen = self.draw_surface)
      #pygame.draw.circle(screen, (0, 0, 255), (self.x, self.y), 75)
    #self.draw_surface.fill((255,255,255,100),special_flags=pygame.BLEND_RGBA_MULT)
    self.screen.blit(self.draw_surface, (0,0))
    # Flip the display
    if self.display:
      pygame.display.flip()
    self.clock.tick(60)
  
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
      if event.key == pygame.K_SPACE:
        self.debug_render = True
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
      if event.key == pygame.K_SPACE:
        self.debug_render = False
      handled=True
    return handled




premade_map = np.load("../LevelGen/HandMadeMap.npy")
game = game_instance(screen= screen, display=True, objects=[
  
  ],tile_map=premade_map, map_size=[premade_map.shape[0], premade_map.shape[1]])

  #player("red", pygame, np.array([100,200], dtype="float32"), speed=20, size=20),
  #player("green", pygame, np.array([400,400], dtype="float32"), speed=3, size=10),
  #player("grey", pygame, np.array([250,250], dtype="float32"), speed=10, size=30) 

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
  

  if frame_time >= 1/fps:
    game.game_logic(delta_time)
    game.draw_game()
    frame_time=0
  
pygame.quit()