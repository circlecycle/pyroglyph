import sys, threading
import cPickle as pickle
from xml.dom.minidom import parse, parseString
import sys, pyglet, Events, InitGL, Nodes, pdb

#as an aid to external scripts provide a reference to the canvas here.
#the "real" (internally referenced) canvas exists in Nodes.canvas
canvas = None

def run(programXml):
  global canvas
  # kill the hash bang to get a wellformed document
  if programXml.startswith("#!"):
    programXml = programXml[programXml.index('\n'):]

  # parse the xml into a minidom object (no xmlish namespaces allowed with it!)
  try:                    
    canvasElement = parseString(programXml).documentElement
  except Exception, msg:  
    Events.Error(None, msg, "Error parsing XML of program")

  #make an invisible window (so we have context while we make nodes, 
  #mostly for text objects to tell their size before hand)
  title = canvasElement.getAttribute('title') or 'Pyroglyph Application'
  
  #load default font, so that it's present implicitly...
  InitGL.fonts['Arial'] = pyglet.font.load('Arial', 12, bold=False, italic=False)
  
  #initialize the entire program namespace in this one fell swoop!
  canvas = Nodes.Node(canvasElement)
  
  #This starts GL and the dom tree scanner. This "tree scanner" (dom traversal depth first) reads the dom parsed 
  #from the program input to render the screen.
  InitGL.mainloop(canvas)
  
