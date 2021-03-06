import sys, weakref
from pyglet.window import key, mouse
from pyglet import clock
import InitGL, ViewProjector, Nodes
import pdb

lastKeyPressed = ()
lastMouseOver = None

#delegate called when global focus is set
def handleFocused(focused=None): 
  lastFocused = Nodes.canvas.lastFocused
  if lastFocused != focused:
    
    #assign the new focus a weakproxy so it doesnt hang around unnecessarily
    Nodes.canvas.__dict__['focused'] = weakref.proxy(focused)
    
    #send a focus off event to the last focused object 
    if Nodes.canvas['lastFocused']: lastFocused.focus = False
    
    #save the new focus for next loop
    Nodes.canvas.lastFocused = focused
    
    #send a focus on event to the new object
    focused.focus = True

def on_mouse_press(x, y, button, modifiers): 
  Nodes.canvas.mousex, Nodes.canvas.mousey = x, Nodes.canvas.height-y    
  Nodes.canvas.focused = ViewProjector.findFocus()
  Nodes.canvas.focused.mousedown = (button, modifiers)

def on_key_press(symbol, modifiers):
  global lastKeyPressed
  #for now escape quits
  if symbol == key.ESCAPE: InitGL.win.has_exit = True
  lastKeyPressed = (symbol, modifiers)
  Nodes.canvas.focused.keydown = (symbol, modifiers)
  #set up keyrate timer - on_key_release removes it
  clock.schedule_once(repeatKey, 0.4)
  
def repeatKey(val=False):
  global lastKeyPressed
  clock.unschedule(repeatKey)
  Nodes.canvas.focused.keydown = lastKeyPressed
  clock.schedule_once(repeatKey, 0.03)
  
def on_key_release(symbol, modifiers):
  clock.unschedule(repeatKey)
  Nodes.canvas.focused.keyup = (symbol, modifiers)
  
def on_mouse_release(x, y, button, modifiers): 
  Nodes.canvas.mousex, Nodes.canvas.mousey = x, Nodes.canvas.height-y
  Nodes.canvas.focused.mouseup = (button, modifiers)
    
def on_mouse_drag(x, y, dx, dy, buttons, modifiers): 
  Nodes.canvas.mousex, Nodes.canvas.mousey = x, Nodes.canvas.height-y
  Nodes.canvas.focused.mousedrag = (dx, dy, buttons, modifiers)
    
def on_mouse_scroll(x, y, scroll_x, scroll_y): 
  Nodes.canvas.mousex, Nodes.canvas.mousey = x, Nodes.canvas.height-y
  Nodes.canvas.focused.mousedown = (scroll_x, scroll_y)
  
#! EXPERMENTAL and currently disabled because it's too slow
def on_mouse_motion(x, y, lx, ly):
  global lastMouseOver
  Nodes.canvas.__dict__['mousex'] = x
  Nodes.canvas.__dict__['mousey'] = Nodes.canvas.height-y
  over = ViewProjector.findFocus()
  if lastMouseOver and over != lastMouseOver:
    lastMouseOver.touch('mouseout')
  lastMouseOver = over
  over.touch('mouseover')
  
  
def Error(node, msg, notice):
  """ just a simple way of presenting nicer errors (especially later on when there is a builtin debug screen) """
  if node:  tagContents = "In the tag: "+node.toxml()
  else:     tagContents = ""
  raise Exception, str("\n"+("-"*60)+"\n"+tagContents+"\nError: "+`msg`+'\n\nNotice:\n'+notice)
  
