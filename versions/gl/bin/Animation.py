
import Nodes, ViewProjector, math

#singleton to hold all outstanding animations
animateSchedules = {}

def doAnimations(dt):
  global animateSchedules
  framerate = Nodes.canvas.framerate
  
  for key in animateSchedules.keys():
    a = animateSchedules[key] 
    
    #if we finished last time around, set the final value if nescessary
    #and erase the animation
    if a.finished:
      if a.what[a.attrname] != a.targetValue:
        a.what[a.attrname] = a.targetValue
      del animateSchedules[key]
      continue   
    
    #exactly how far to move this frame.
    inc = (a.inc*dt)
    
    #if we are going up, test for end
    if a.goingUp:
      #are we at or near enough target value?
      if a.targetValue <= a.what[a.attrname]+inc: 
        a.finished = True
        continue
      
    #if we are going down, test for end
    else:
      #are we at or near enough target value?
      if a.targetValue >= a.what[a.attrname]+inc: 
        a.finished = True
        continue
  
    #move the object, now adjusted for how much time elapsed to make nice animations
    a.what[a.attrname] += inc
    
    if ['x', 'y', 'width', 'height'].count(a.attrname):
      v = ViewProjector.viewToVertice(a.what.x, a.what.y, a.what.width, a.what.height)  
      ViewProjector.self.quads[a.what.viewindex].vertices = v


class Animator:
  """
    This class advertises a thread
  """
  def __init__(self, what, attrname, start, end, dur):
    global animateSchedules
    
    #normalize start/end into low/high
    if start > end: goingUp = False
    else:           goingUp = True

    #get the low and high of the start and end
    low, high = min(start, end), max(start, end)
    
    #floatify arguments
    high, low, dur = float(high), float(low), float(dur)

    #calulate the increment factor for this framerate
    inc = ((high-low)/dur)
    
    if not goingUp:
        inc = -inc
        targetValue = low
    else:
        targetValue = high
        
    #save the animation properties
    self.uid = "%s%s"%(id(what), attrname)
    self.what = what
    self.attrname = attrname
    self.targetValue = targetValue
    self.inc = inc
    self.goingUp = goingUp
    self.finished = False
        
    #add this to the animations to be deployed
    animateSchedules[self.uid] = self
    
  def stop(self):
    global animateSchedules
    if animateSchedules.has_key(self.uid):
      del animateSchedules[self.uid]
    
    

