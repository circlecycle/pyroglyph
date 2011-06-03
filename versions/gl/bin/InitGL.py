
import sys, time

### Pyglet imports
import pyglet
from pyglet.gl import *
from pyglet import clock, font, image, window
from pyglet.window import key, mouse

import Nodes, ViewProjector, Events, Animation, Helpers

win = pyglet.window.Window(visible=False, resizable=True, caption="Hi!")

#make a new batch of VBOs!
batch = pyglet.graphics.Batch()

fullscreen = False
fonts = {}

def changeWinTitle(val=False):
  global win
  win.set_caption(val)

def toggleFullscreen(force=None):
  global win, fullscreen
  if force == None: fullscreen = not fullscreen
  else:             fullscreen = force
  win.set_fullscreen(fullscreen)
  
# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene(w, h):
  #be sure to save the new screen height as needed on the canvas element!
  #Also, prevent a divide by zero if the window is too small 
  Nodes.canvas.height = int(h) or 1  
  Nodes.canvas.width = int(w) or 1

  glViewport(0, 0, Nodes.canvas.width, Nodes.canvas.height)
  glMatrixMode(GL_PROJECTION)
  glLoadIdentity()      
  
  #NOTE: this is the secret to a GL-based Rasterized XY layout!
  glOrtho(0, Nodes.canvas.width, 0, Nodes.canvas.height, -1, 1) 
  glMatrixMode(GL_MODELVIEW)

def mainloop(canvas):
  global win, fonts, fullscreen, batch
  
  #if a maxsize is given, use it
  if canvas.maxsize:
    mw, mh = [int(x.strip()) for x in canvas.maxsize.split(',')]
    win.set_maximum_size(mw, mh)
  #or use the given value
  else:
    mw, mh = canvas.width, canvas.height
    
  #if the given size is too big, resize to the biggest allowed
  if canvas.width > mw or canvas.height > mh:
    win.set_size(mw, mh)
  #or just use what they passed
  else:
    win.set_size(canvas.width, canvas.height)
    
  # if the canvas has the fullscreen attribute set make it fullsize
  if canvas._elem.getAttribute('fullscreen').lower() == 'true':
    toggleFullscreen(True)

  #set the window's events to go to the right methods in Event.py
  win.on_key_press = Events.on_key_press
  win.on_resize = ReSizeGLScene
  win.on_mouse_press = Events.on_mouse_press
  win.on_mouse_release = Events.on_mouse_release
  win.on_mouse_drag = Events.on_mouse_drag
  win.on_mouse_scroll = Events.on_mouse_scroll
  win.on_key_release = Events.on_key_release
  
  #! EXPERMENTAL and currently disabled because it's too slow
  #win.on_mouse_motion = Events.on_mouse_motion
      
  #retrieve the color of the canvas to use, or white by default
  cr, cg, cb = Helpers.HTMLColorToRGB(getattr(canvas, 'bgcolor', False) or "0xffffff")
  
  #set up some GL stuff..
  glClearColor(cr, cg, cb, 1.0)   # This will clear the background color to what the canvas is
  glEnable(GL_BLEND)              # Enables alpha blending
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) #does something! really!
  
  #enact the FPS cap (canvas.framerate)
  canvas.framerate = int(canvas.framerate)
  
  #schedule the animation routine to run each frame
  pyglet.clock.schedule_interval(Animation.doAnimations, 1./canvas.framerate)
  
  #we are done loading, show the window
  win.set_visible(True)
  
  #Traverse the Dom and register views with the VBO screen manager
  ViewProjector.register(canvas, batch)
  
  #run the pyglet main loop, sit back, and enjoy!
  pyglet.app.run()
  
@win.event
def on_draw():
  global batch
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
  batch.draw()
    
    
