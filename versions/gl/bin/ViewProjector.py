
### Pyglet imports
from pyglet.gl import *
from pyglet import clock, font, image, window
from pyglet.window import key

from xml.dom.minidom import parseString
import time, xml, InitGL, Events, Nodes, Helpers, vbo

class namespace:  pass
self = namespace()
self.views = [] 
self.quads = [] 

#todo: unroll this loop into findViewsFromDOMInDepthOrder to lose the method calls
def prepareDomForDrawing(root):
  """
  starting with the canvas, get a list of views from the DOM, 
  updating those views' inherited and computed values on the way.
  
  return a list of tuple reresenting views that need to be drawn.
  """
  self.views = []
  recurse(root.childViews)
  return self.views
  
def recurse(subnodes, dirty=False):
  cw, ch = Nodes.canvas.width, Nodes.canvas.height
  
  try:
    for v in subnodes: 
      ns = v.__dict__
      vp = v.parent 
    
      if vp:
        #compute basic absolute attributes
        ns['_absV'] = vp._absV and v.visible
        ns['_absA'] = vp._absA * v.opacity
        ns['_absX'] = v.x+vp._absX
        ns['_absY'] = v.y+vp._absY
      
        #if not visible we are done with this and everything beneath it - optimization
        if not v._absV or v._absA == 0 or v.x > cw or v.y > ch: 
          continue
      
        #if a fgcolor isn't given use the parent's
        if not v['fgcolor']:  ns['_absFC'] = vp._absFC
        else:                 ns['_absFC'] = str(v['fgcolor'])

      #or get the dimension values front and center!
      x, y = v._absX, v._absY
      a, w, h = v._absA, int(v.width), int(v.height)

      #if the color is uncomputed on the node compute it
      if v.bgcolor and type(v.bgcolor) != type(tuple()):
        ns['bgcolor'] = Helpers.HTMLColorToRGB(v.bgcolor)
      
      #pass a tuple type through or init it
      bgcolor = v.bgcolor
      if len(bgcolor) == 3:
        br, bg, bb = bgcolor
      else:
        br, bg, bb = (0, 0, 0)
        
      #if the values are different compute it out to a tuple again
      if type(v._absFC) != type(tuple()):
        ns['_absFC'] = Helpers.HTMLColorToRGB(v._absFC)
      fr, fg, fb = v._absFC
      
      #register this view to a now z-ordered list of views to be rendered.
      self.views.append((v, x, y, w, h, a, br, bg, bb, fr, fg, fb))

      #add subviews to be recursed on
      recurse(v.childViews)
    
  except Exception, msg:
    raise str("\n"+("-"*60)+"\nIn the tag:\n"+v.toxml()+"\nError: "+`msg`)
    
  
def findFocus():
  """ 
  from the last computed list of views find which object
  is under the current mouse position from the Events. x/y attrs
  """
  x, y = Nodes.canvas.mousex, Nodes.canvas.mousey
  
  #in _reverse_, for each view we encounter, test it. NOTE the three -1's yep that's how it works
  for i in range(len(self.views)-1, -1, -1):
    v = self.views[i][0]
    
    #enables the focusable keyword:
    if not v.focusable: continue
      
    #if the event lies in it's x y and width and height then it's focused
    vX, vY = v._absX, v._absY
    if x >= vX  and x <= vX+v.width:
      if y >= vY and y <= vY+v.height:
        return v
        
  #or if none found return the canvas
  return Nodes.canvas
  
#HAVE TO SEND A SIGNAL TO EACH CHILD WHEN A PARENT MOVES TO RECALCULATE POSITION.
#THIS AVOIDS THE CURRENTLY VERY NASTY SITUATION WHERE THE WHOLE DOM IS ITERATED OVER
#EVERY FRAME AS IT CURRENTLY REQUIRES

#prepareDomForDrawing(Nodes.canvas)

viewindex = 0

def register(v, batch, spacing=0):
  global viewindex
  box = viewToVertice(v.x, v.y, v.width, v.height)
  
  #if the color is uncomputed on the node compute it
  if v.bgcolor and type(v.bgcolor) != type(tuple()):
    r, g, b = Helpers.HTMLColorToRGB(v.bgcolor)
  color = vbo.color(r, g, b, v.opacity)
  
  print " "*spacing, v
  
  self.quads.append( 
      batch.add(
          4, GL_QUADS, None,
          ('v4f', box.transpose().flat),
          ('c4B', color.transpose().flat)
      )
  )
  
  for view in v.childViews:
    register(view, batch, spacing=spacing+1);
  
  v.viewindex = viewindex
  viewindex = viewindex + 1
    
def viewToVertice(x, y, w, h):
  v = vbo.dot(vbo.scale(w, h), vbo.square())
  v = vbo.dot(vbo.translate(x, y), v)
  return v
