# Simple pygame program
# Import and initialize the pygame library
import pygame
pygame.init()

import time
from player import player
import numpy as np
# Set up the drawing window
screen = pygame.display.set_mode([500, 500])

class game_instance():
  # Run until the user asks to quit
  def __init__(self, screen, display=False, objects=[]):
    self.display = display
    self.running = True
    self.objects = objects
    self.screen = screen
    self.player_input = {'W': False, 'A': False, 'S':False, 'D': False}

  def game_logic(self, delta_time):
    for i in self.objects:
      if i.destroyed:
        self.objects.pop(i)
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
    if game.handle_key_press(event):
      continue
      # Done! Time to quit.
  game.game_logic(delta_time)

  if frame_time >= 1/fps:
    game.draw_game()
    frame_time=0
  
pygame.quit()