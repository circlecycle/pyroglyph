
from Foundation import * 
from AppKit import *

from Viewable.Engine.Helpers import HTMLColorToRGB

class CocoaView(NSBox): 
  
  def vbl_init(self, node, canvasView):
    self.node = node
    self.lastFrame = None
    self.canvasView = canvasView
    
    #when these change, update fill colors by calling vbl_color()
    node.constrain(attr="opacity", func=self.vbl_color)
    node.constrain(attr="bgcolor", func=self.vbl_color)
    node.constrain(attr="fgcolor", func=self.vbl_color)
    
    #update rotation by calling _rotate()
    node.constrain(attr="rotate", func=self.vbl_rotate)
    
    #set the type of box
    self.setBoxType_(NSBoxCustom)
    self.setBorderType_(NSNoBorder)
    self.setTitlePosition_(NSNoTitle)

    #compute the color the first time around
    self.vbl_color()
    
  def isFlipped_(self):  
    """ this causes the view to have a flipped-y coordinate system """
    return True
      
  def mouseUp_(self, event): 
    """ fires a mouseup event on the owner node """
    global canvasView
    
    node = self.node
    mouseEvent = canvasView.convertPointToBase_(NSEvent.mouseLocation())
    node.mouseup = mouseEvent
  
  def mouseDown_(self, event):
    """ fires a mousedown event on the owner node """
    global canvasView
    node = self.node

    m = NSEvent.mouseLocation()
    c = canvasView.convertPointToBase_(NSEvent.mouseLocation())
    node.canvas.mousex = m.x
    node.canvas.mousey = m.y
    node.mousedown = m
    
  def vbl_color(self, val=False):
    #set the color to draw the view's background with
    node = self.node
    
    if type(node.bgcolor) != type(tuple()):
      node.bgcolor = HTMLColorToRGB(node.bgcolor)
  
    self.color = NSColor.colorWithCalibratedRed_green_blue_alpha_(
                 node.bgcolor[0], 
                 node.bgcolor[1], 
                 node.bgcolor[2],
                 node.opacity,
               )
               
    self.setFillColor_(self.color)
    
  def vbl_rotate(self, val=False):
    self.setFrameCenterRotation_(self.node.rotate)
    
  def vbl_update(self):
    node = self.node
    frame = NSIntegralRect(NSMakeRect(node.x, node.y, node.width, node.height))
    if self.lastFrame != frame:
      self.setFrame_(frame)
      self.lastFrame = frame
      
