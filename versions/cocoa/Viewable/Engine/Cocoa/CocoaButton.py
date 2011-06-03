

from Foundation import * 
from AppKit import *

from Viewable.Engine.Helpers import HTMLColorToRGB

class CocoaButton(NSButton): 
  
  def vbl_init(self, node, canvasView):
    self.node = node
    self.lastFrame = None
    self.canvasView = canvasView
    
    #update rotation by calling _rotate()
    node.constrain(attr="rotate", func=self.vbl_rotate)
    
    self.setTitle_(node['text'])
    
  def isFlipped_(self):  
    """ this causes the view to have a flipped-y coordinate system """
    return True
      
  def mouseUp_(self, event): 
    """ fires a mouseup event on the owner node """
    
    node = self.node
    mouseEvent = self.canvasView.convertPointToBase_(NSEvent.mouseLocation())
    node.mouseup = mouseEvent
  
  def mouseDown_(self, event):
    """ fires a mousedown event on the owner node """
    node = self.node

    m = NSEvent.mouseLocation()
    c = self.canvasView.convertPointToBase_(NSEvent.mouseLocation())
    node.canvas.mousex = m.x
    node.canvas.mousey = m.y
    node.mousedown = m
    
  def vbl_rotate(self, val=False):
    self.setFrameCenterRotation_(self.node.rotate)
    
  def vbl_update(self):
    node = self.node
    frame = NSIntegralRect(NSMakeRect(node.x, node.y, node.width, node.height))
    if self.lastFrame != frame:
      self.setFrame_(frame)
      self.lastFrame = frame
      
