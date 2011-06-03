
import time, sys
from Foundation import * 
from AppKit import * 
from Viewable.Engine.Animation import doAnimations

#global window pointers - these must exist before other imports from Cocoa*
window = None
frame = None
canvasView = None
ap = None
timer = None
canvas = None

import CocoaView, CocoaButton

class FrameIncrementDelegate(NSObject):  
  """ this guy is called by cocoa timer to effectuate animation"""
  
  lastFiredAt = False

  def tick_(self):
    dt = time.time() - (self.lastFiredAt or time.time())
    self.lastFiredAt = time.time()
    doAnimations(dt)
    
#A class that will get messsages for the application
class AppDelegate(NSObject): 
  def applicationDidFinishLaunching_(self, notification):
    global fid, timer, canvas
    fid = FrameIncrementDelegate.alloc().init()
    timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(1.0/canvas.framerate, fid, 'tick:',0,1)
    
  def windowWillClose_(self, notification):
    app.terminate_(self)

def View(node=None, parent=None, canvasv=None): 
  global canvasView
  #make view with dimensions
  rect = NSMakeRect(node.x, node.y, node.width, node.height)
    
  if node.vbl_classname == "button":
    cv = CocoaButton.CocoaButton.alloc().initWithFrame_(rect)
  else:
    cv = CocoaView.CocoaView.alloc().initWithFrame_(rect)
    
  if canvasv:
    cv.vbl_init(node, cv)
  else:
    cv.vbl_init(node, canvasView)
  
  #add the subview to the parent
  if parent: parent.vbl_cocoaview.addSubview_(cv)
  return cv
    
    
def CocoaCanvas(incomingCanvas):
  global app, canvasView, window, ap, canvas
  
  canvas = incomingCanvas
  
  #make the application
  app = NSApplication.sharedApplication() 
  
  #define the initial window size
  windowSize = NSMakeRect(0, 0, canvas.width, canvas.height)
  
  #make the window
  window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_( 
    windowSize, 
    NSTitledWindowMask | NSClosableWindowMask | NSResizableWindowMask | NSMiniaturizableWindowMask, 
    NSBackingStoreBuffered, 
    False)
      
  #make a new application delegate and set it on the window
  ap = AppDelegate.alloc().init()
  app.setDelegate_(ap)
  window.setDelegate_(ap)
  
  #set window color:
  wincolor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1)
  window.setBackgroundColor_(wincolor)
  window.setOpaque_(False)
  
  #window title
  window.setTitle_(canvas.title)
  
  #make the canvasView in the window
  canvasView = View(node=canvas, parent=None, canvasv=True)
  canvasView.setWantsLayer_(True)
  window.setContentView_(canvasView)
  
  #make sure all cocoa objects have a pointer to the canvas
  CocoaView.canvasView = canvasView
  
  #return the finished canvas object
  return canvasView
    
  
#make the application], set it's values, start event loop
def start():     
  window.display()
  window.orderFrontRegardless()
  app.run()
  
  


####### CODE SCRAPS #################### # # #  #   #    #

# #animation test:
# NSAnimationContext.currentContext().setDuration_(0.2)
# rect = NSMakeRect(mouse.x, mouse.y, self.owner.width, self.owner.height)
# 
# self.layer().setFrame_(rect)
# self.setFrame_(rect)
# 
# self.owner.mousedown = mouse
