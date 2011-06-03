
import sys, weakref
from pyglet.window import key, mouse
from pyglet import clock
import Canvas

lastKeyPressed = ()
lastMouseOver = None
  
def Error(node, msg, notice):
  """ just a simple way of presenting nicer errors (especially later on when there is a builtin debug screen) """
  if node:  tagContents = "In the tag: "+node.toxml()
  else:     tagContents = ""
  raise Exception, str("\n"+("-"*60)+"\n"+tagContents+"\nError: "+`msg`+'\n\nNotice:\n'+notice)
  
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
