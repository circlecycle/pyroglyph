
from xml.dom.minidom import parse, parseString
import Nodes, ViewProjector, Events, Basetags, InitGL, Nodes, Helpers
import sys, os, weakref, time, pyglet

class _class(Nodes.Node):
  """
    for each class tag encoutered, assemble and execute one class definition in Basetags,
    dynamically accumlating and building the given programs' class space.
    
    this could be computed and 'rendered' instead of being done in real time!!
  """
  def __construct__(self):
    name = self._elem.getAttribute('name')
    Nodes.CLASSES_ACCUMULATOR[name] = self
    extends = self._elem.getAttribute('extends') or "view"
    definition = "class %s(%s):\n  def __construct__(self): %s.__construct__(self)"%(name, extends, extends)
    exec definition in globals()
    self.delete()

class node(Nodes.Node):
  """ 
    A node is an unaltered version of the Nodes.Node class so we just pass it, 
    this just allows us to have a <node> tag.
  """
  def __construct__(self):
    pass
    
def registerView(view):
  ViewProjector.add()

class view(Nodes.Node):
  def __construct__(self):
    ns = self.__dict__    
    
    #set the display type of the node to view
    ns['_displaytype'] = 'view'
    
    #if color is absent, the view is transparent (which is different then visible, which hides children too)
    self.computeTransparency()
    
    #if width or height aren't given initially, note this for autosizing  
    #note that we have to check the DOM for this value because constraints
    #may prevent the associated namespace value from being set until init time!
    if not self._elem.getAttribute('width'): ns['_nowidth'] = True
    if not self._elem.getAttribute('height'): ns['_noheight'] = True
      
    ####### APPLY DEFAULTS #################### # # #  #   #    #
    
    #(which doesn't override - but typecasts! - preexisting string attrs on the element)
    self.applydefaults( { 'width':0, 'height':0, 'image':'', 'aligned':'',
                          'x':0, 'y':0, 'z':0.0, 'sizing':'auto',
                          'bgcolor':'white', 'opacity':1.0,
                          'visible':True, 'focusable':True, } )
                          
    ####### AUTO SIZING #################### # # #  #   #    #
    
    #if this view has a image attached, go fetch and attach it
    if self['image']:
      ns['_image'] = eval(self.image, self.__dict__)
      
      #further, if autosizing is on and no width/height given, use the w/h of the image instead
      if 'auto' in self.sizing or 'once' in self.sizing:
        if self['_nowidth']: self.width = self._image.img.width  
        if self['_noheight']: self.height = self._image.img.height
    
    #else determine whether we recieve size from our children
    elif 'auto' in self.sizing and self._classname != 'import':
      if self['_nowidth']: 
        self.constrain(attr="childViews", func=self._computeWidth)

      if self['_noheight']: 
          self.constrain(attr="childViews", func=self._computeHeight)

    #Either way, always notify the parent of changes if the parents sizing is set to auto
    if 'auto' in self.parent.sizing and 'skip' not in self.sizing and self.parent._classname != 'import':
      if self.parent['_nowidth']:
        self.constrain(attr="width", func=self.parent._computeWidth)
        self.constrain(attr="x", func=self.parent._computeWidth)

      if self.parent['_noheight']:
        self.constrain(attr="height", func=self.parent._computeHeight)
        self.constrain(attr="y", func=self.parent._computeHeight)                                                    
                                 
    #when either of these changes, check for transparency of the view
    self.constrain(attr='bgcolor', func=self.computeTransparency)
    self.constrain(attr='image', func=self.computeTransparency)
    
    #setup up a constraint to run _init on init
    self.constrain(attr="init", func=self._init)
    
    #setup up a constraint to run _init on init)
    self.constrain(attr="late", func=self._late)
        
    #add this node into the childViews array of the parent.
    #if a specific insertion point was requested, honor it.
    if self._after and self._after in self.parent.childViews:
      self.parent.childViews.insert(self.parent.childViews.index(self._after), self)
    else:
      self.parent.childViews.append(self)
      
    #touch the parent childViews attribute to signify a new node is ready.
    self.parent.touch('childViews')
      
  def _init(self, val=False):
    #if sizing == 'once' then we want to compute the size of this object once:
    if 'once' in self.sizing or 'skip' in self.sizing:
      self._computeSize()
      
  def _late(self, val=False):
    #use the aligned attribute to set up constraints that vertically or horizontally center the view
    if self.aligned:
      #if the view is aligned horizontally "center"
      if 'center' in self.aligned:
        self.parent.constrain(attr="width", func=self._center, set=True)

      #if the view is aligned vertically "middle"
      if 'middle' in self.aligned:
        self.parent.constrain(attr="height", func=self._middle, set=True)
        
  def _center(self, val=False):
    self.x = (self.parent.width/2)-(self.width/2)

  def _middle(self, val=False):
    self.y = (self.parent.height/2)-(self.height/2)
    
  #this is called by delegate whenever the bgcolor changes
  def computeTransparency(self, val=False):
    if self['bgcolor'] or self['image']: 
      self.transparent = False
    else:
      self.transparent = True

  def bringToFront(self):
    if self.parent.childViews.index(self) < len(self.parent.childViews) - 1:
      del self.parent.childViews[self.parent.childViews.index(self)]
      self.parent.childViews.append(self)
      self.parent.touch('childViews')
    
  def sendToBack(self):
    if self.parent.childViews.index(self) > 0:
      del self.parent.childViews[self.parent.childViews.index(self)]
    self.parent.childViews.insert(0, self)
    self.parent.touch('childViews')
    
  def getLayer(self):
    return self.parent.childViews.index(self)
    
  def setLayer(self, position):
    del self.parent.childViews[self.parent.childViews.index(self)]
    self.parent.childViews.insert(position, self)
    self.parent.touch('childViews')
    
  def _computeWidth(self, val=False):
    w = self.getWidth()
    if self.width != w: self.width = w
    
  def _computeHeight(self, val=False):
    h = self.getHeight()
    if self.height != h: self.height = h
    
  def _computeSize(self, val=False):
    w = self.getWidth()
    if self.width != w: self.width = w
    h = self.getHeight()
    if self.height != h: self.height = h
  
  def getWidth(self):
    views = [v.x+v.width for v in self.childViews if v.sizing != 'skip']
    if views: return max(views)
    else:     return self.width
      
  def getHeight(self):
    views = [v.y+v.height for v in self.childViews if v.sizing != 'skip']
    if views: return max(views)
    else:     return self.height
    
  def absx(self, x):
    return x - self.parent._absX
    
  def absy(self, y):
    return y - self.parent._absY
    
class rect(view):
  """make a view that isn't focusable by default, hence, a rectangle."""
  def __construct__(self):
    #initialize the base class (important!)
    view.__construct__(self)
    #and remove the ability to focus.
    self.focusable = False    
    
class text(view):
  """ make a text object that will be rendered on the screen"""
  def __construct__(self):
    #initialize the base class (important!)
    view.__construct__(self) 
    
    #a place to hold the pyglet text object we will manipulate
    self.__dict__['_txt'] = None
    #override the display type of the node to view
    self.__dict__['_displaytype'] = 'text'
    #text never starts transparent, unlike views
    self.__dict__['transparent'] = False
    
    #apply more defaults to the node (the only thing we dont need is w/h)
    self.applydefaults( {'text':"",
                         'wrap':False,
                         'font':'Arial', 
                         'valign':'top', 
                         'halign':'left'} )
                         
    #if the text or font changes recompute the text object    
    self.constrain(attr="text", func=self._textSize, set=True)  
    self.constrain(attr="font", func=self._textSize, set=False)  
        
  def _textSize(self, val=False):    
    if self.text: txt = str(self.text)
    else:         txt = ' '
    
    self.__dict__['_txt'] = pyglet.font.Text(InitGL.fonts[self.font], text=txt, halign=self.halign, valign=self.valign)                             
                                
    if not self.text:
      self.width = 0
    else:
      if int(self._txt.width) != int(self.width):
        if self.wrap:   self._txt.width = int(self.width)
        else:           self.width = int(self._txt.width)

    if self._txt.height != self.height:
      self.height = int(self._txt.height)
      
    #if the parent's autosizing attribute is set to auto or skip, recalculate parent's size
    if 'skip' in self.parent.sizing or 'auto' in self.parent.sizing:
        self.parent._computeSize()
  
class label(text):
  def __construct__(self):
    #initialize the base class (important!)
    text.__construct__(self)
    self.focusable = False
      
class _import(view):
  """ Given a partial xml document (no top node) in the src attribute, import all naked subnodes into
      the namespace of this tag! Means that libraries have no root element, and that this can be 
      refereced like a pythonic package (no namespace cluttering!!)
  """
  def __construct__(self):
    view.__construct__(self)
    
    if not self['src']:
      Events.Error(None, "", "Error: import statement missing src")
    
    #look for a parent import tag 
    vp, found = self, False
    while vp.parent:
      vp = vp.parent
      if vp._classname == 'import':
        found = vp._includePath
        break
        
    #if we have found a parent import path use it as our new base
    if found: self.__dict__['_includePath'] = "%s/%s"%(found, self.src)
    else:     self.__dict__['_includePath'] = "%s/%s"%(Nodes.baselibs, self.src)
    
    #if it's a filename this will work
    try:    
      fname = "%s"%self._includePath
      buf = file(fname).read()
      #the actual importPath is the parent, not the invoked file's full path name
      self.__dict__['_includePath'] = '/'.join(self._includePath.split('/')[-1]) 
        
    #otherwise if it's a dir, it will find the library.lzx file
    except: 
      fname = "%s/library.lzx"%self._includePath
      buf = file(fname).read()
      
    #...or it was a bad file name and we got an exception...
    
    #or else now we should have a <library> element
    try:
      domToLoad = parseString(buf).documentElement
    except Exception, msg:
      Events.Error(None, msg, "Error parsing import statement: %s"%(fname))
      
    #the library element may have an import directive, do this the same way 
    #the canvas does the "import" attribute:
    modsToLoad = [( x.strip(), Nodes._import(x.strip()) ) 
                    for x in domToLoad.getAttribute('import').split(',') 
                      if x and x not in Nodes.GLOBALS_ACCUMULATOR]
                      
    #except we have to set new modules on this tag because we missed the init pass already
    [setattr(self, x, y) for x, y in modsToLoad]
    #and also place it in the the accumulator for any future tags to use as well.
    [Nodes.GLOBALS_ACCUMULATOR.append(x) for x in modsToLoad]
                      
    #for each child elem present, recurse and make a new Node if indicated (some types don't recurse!)
    [self.create(child, topmostnode=False) 
      for child in domToLoad.childNodes 
        if child.nodeType == child.ELEMENT_NODE]
    
class comment(Nodes.Node):
  """ this wraps inner xml but does nothing with it effectively commenting out
      whatever is inside of it.
  """
  def __construct__(self):
    #get rid of this node as soon as it's found - a comment disappears!
    self.delete()
  
class method(Nodes.Node):
  """ use the method tag to define a callable function that is activated
      whose functional contents come from the inner python contained within the tag.
  """
  def __construct__(self):
    #extract, contain, and properly indent python content
    funcname = self._elem.getAttribute('name')
    args = self._elem.getAttribute('args')
    script = Nodes.normalize_python(node=self, definition="def %s(%s):"%(funcname, args))
    
    #run the code (which will define a function where we need it)
    try:  exec script in self.parent.__dict__
    except Exception, msg: Events.Error(self, msg, "bad syntax in python block")

class handler(Nodes.Node):
  """ use the handler tag to define a callable function that is activated
      when a target value changes and whose functional contents come from 
      the inner python contained within the tag.
  """
  def __construct__(self):    
    #extract, wrap, and properly indent python content
    self.funcname = self['name'] or "_%s_%s"%(self.on, self.canvas._uidcount)
    self.canvas.__dict__['_uidcount'] += 1
    args = self['args'] or "value"
    script = Nodes.normalize_python(node=self, definition="def %s(%s):"%(self.funcname, args))

    #run the code (which will define a function where we need it)
    try:  exec script in self.parent.__dict__
    except Exception, msg: Events.Error(self, msg, "bad syntax in python block")
    
    #if a reference is given adjust the target to that, otherwise use the parent per normal
    if self['reference']:
      self.parent.constrain(attr='early', func=self._reference)
    else:
      self.parent.constrain(attr=self.on, func=self.parent.__dict__[self.funcname])
    
  def _reference(self, val=False):
    target = eval(self.reference, self.parent.__dict__)
    target.constrain(attr=self.on, func=self.parent.__dict__[self.funcname])
    
    
class thread(Nodes.Node):
  """ use the thread tag to define a callable function that starts a thread whose
      functional contents come from the inner python contained within the tag
  """
  def __construct__(self):
    #extract, contain, and properly indent python content
    funcname = self._elem.getAttribute('name')
    args = self._elem.getAttribute('args')
    prefix = "def %s(%s): import threading; t = threading.Thread(target=_thread_%s, args=[%s]); t.setDaemon(True); t.start();"%(funcname, args, funcname, args)
    definitionLine = "def _thread_%s(%s):"%(funcname, args)
    script = Nodes.normalize_python(node=self, prefix=prefix, definition=definitionLine)

    #run the code (which will define a function where we need it)
    try:  exec script in self.parent.__dict__
    except Exception, msg: Events.Error(self, msg, "bad syntax in python block\s%s"%script)

class script(Nodes.Node):
  """ use the script tag to immediately execute inner python at the scope 
      of the parent node 
  """
  def __construct__(self):
    #extract and properly indent python content
    script = Nodes.normalize_python(node=self)
    #run th' junks
    try:  exec script in self.parent.__dict__
    except Exception, msg: Events.Error(self, msg, "bad syntax in python block")
    
class attribute(Nodes.Node):
  """
    use the attribute tag to coerce a variable to some type instead of normal xml string attribute
    although this may seem to have something to do with handlers, etc, it really doesn't - an xml attribute
    becomes a handler by having a handler (or constraint) defined on it, not declartively by this.
  """
  def __construct__(self):
    #set the xml attribute as they ask for. no value = no op. 
    if not self.__dict__.has_key('type'):
      self.__dict__['type'] = "expression"
      
    #if the value doesn't exist on the parent tag then make it.
    if self.__dict__.has_key('value') and not self.parent.__dict__.has_key(self.name):
      if self.__dict__['type'] == 'string': 
        value = str(self.value)
      elif self.__dict__['type'] == 'number':
        value = float(self.value)
      elif self.__dict__['type'] == 'expression':
        value = eval(self.value, self.parent.__dict__)
      #make it  
      self.parent.__dict__[self.name] = value
      
    #if the value on the element exists, cast it
    elif self.parent.__dict__.has_key(self.name):
      #cast to string
      if self.__dict__['type'] == 'string': 
        self.parent.__dict__[self.name] = str(getattr(self.parent, self.name))
      #cast to float
      elif self.__dict__['type'] == 'number':
        self.parent.__dict__[self.name] = float(getattr(self.parent, self.name))
      #cast to expression (eval a string if needed)
      elif self.__dict__['type'] == 'expression':
        #if the type of the attribute is string, it needs casting (eval'ing'!) too.
        if type(getattr(self.parent, self.name)) == type(u""):
          self.parent.__dict__[self.name] = eval(getattr(self.parent, self.name), self.parent.__dict__)
    
class font(Nodes.Node):
  """ Load a font into the system for later reference by text tags"""
  def __construct__(self):
    self.applydefaults( { 'face':'Arial', 
                                'height':16,
                                'size':24, 
                                'bold':False, 
                                'italic':False, } )
                                
    ####### if the canvas is init'd (gl is now up) add the font   #################### # # #  #   #    #
    ####### else accumulate it to be run once GL is up!           #################### # # #  #   #    #
    
    InitGL.fonts[self.name] = pyglet.font.load(self.face, self.size, bold=self.bold, italic=self.italic)
      
class replicate(view):
  """ 
    this little tag does a big job: handling replication. It is different then openlaszlo's in 
    that it is tag based instead of a "magic" attribute. It will place n clones (anythign inside the 
    tag) under the parent. it uses the "over" attribute to point to some iterable source, and "auto"
    to specify when the replication first occurs (at once, or after calling update() manually) 
  """
  def __construct__(self):
    view.__construct__(self) 
    
    self.applydefaults( { 'auto':'true', 'over':"[]" } )
                    
    #either use a name or make a uid
    name = self._elem.getAttribute('name')
    if not name:
      name = "_replicate_%s"%(self.canvas._uidcount)
      self.canvas.__dict__['_uidcount'] += 1
      self.setname(name)
    
    #don't make anything until init time
    self.constrain(attr='init', func=self._init)
    self.constrain(attr='over', func=self.update)
    
  def _init(self, val=False):
    if type(self.over) is type(""):
      self.over = eval(self.over, self.__dict__)
    
  def update(self, val=None):
    #erase all of the nodes from a previous replication. Maybe 
    #this should be better optimized to not delete nodes that 
    #don't need to be deleted? Also, note i'm making a copy of
    #childNodes to loop through. otherwise i'd be editing the list
    #as i read it - bad mojo.
    
    #oops gotta remember to erase things in both childViews... 
    for node in self.parent.childViews[:]:
      if node['_replicated'] == self.name:
        node.delete()
        
    #...and childNodes
    for node in self.parent.childNodes[:]:
      if node['_replicated'] == self.name:
        node.delete()
        
    #for each iterable element in 'over' create an object that has a pointer to each item
    for entry in self.over:
      for elem in self._elem.childNodes:
        if elem.nodeType == elem.ELEMENT_NODE:
          self.parent.create(elem, 
                             after=self, 
                             attrs={'data':entry, '_replicated':self.name}, )
                             
    self.parent.touch('childViews')
          
class image(Nodes.Node):
  """ a image tag stores image to be referenced later.
      Currently it is just for use with images and the image attributes of views
  """
  def __construct__(self):  
    self.constrain(attr='src', func=self._update, set=True)
    
  def _update(self, val=False):
    if self['src']:
      self.img = pyglet.image.load(self.src).texture
    
class dataset(Nodes.Node):
  """ a dataset is a tag that contains other tags - not treated as lzx but
      as xml to be used by other tags as a data image. 
  """
  
  def __construct__(self):
    #dataset has a url, a flag to set automatic request of data, and the data attribute to latch to data changes
    self.applydefaults({'url':'', 'auto':False, 'data':False})
    
    #if a url is given and auto is true, request data from this url. note that if no url is given, refresh should not be called.
    if(self.url and self.auto): 
      self.request()
      
    #else take the results of the request and advertise it on this tag as .childNodes. Touch the data attribute
    else:
      self.childNodes = [x for x in self._elem.childNodes if x.nodeType == x.ELEMENT_NODE]
      self.touch('data')
    
  def request(self, url=False):
    #if they pass a url (they don't have to) then use that to do this and future requests.
    if url: self.url = url
    #take the results of the request and advertise it on this tag as .childNodes
    self.childNodes = [x for x in self._elem.childNodes if x.nodeType == x.ELEMENT_NODE]
    self.touch('data')
    
class setall(Nodes.Node):
  """set all sibling nodes with a certain attribute and value (think all siblings x=10...)"""
  def __construct__(self):
    self.applydefaults( { 'attr':'', 'value':'', })
    if self.value:  self.value = eval(self.value, self.__dict__)
    self.parent.constrain(attr="init", func=self.update)
    self.parent.constrain(attr="attr", func=self.update)
    self.parent.constrain(attr="value", func=self.update)
    
  def update(self, val=None):
    [setattr(node, self.attr, self.value) for x in self.parent.childViews]


######################################################################    
####### EXAMPLE EXTENSION CLASS #################### # # #  #   #    #
######################################################################
class blueview(view):
  """Test inheriting from view"""
  def __construct__(self):
    #tamper with the tag to make a new one
    self.bgcolor = '0x0000ff'
    #don't forget to call your inherited classes __construct__ constructors too!
    view.__construct__(self) 
    

class timer(Nodes.Node):
  """given an interval and a method, call the method every"""
  def __construct__(self):
    self.applydefaults({'period':0.0, 'on':False})
    self.parent.constrain(attr='init', func=self._init)
    self.parent.constrain(attr='on', func=self._on, set=True)
    
  def _init(self,val=False):
    self.method = eval(self.method, self.__dict__)
    pyglet.clock.schedule_interval(self.method, self.period)
      
  def start(self):
    pyglet.clock.schedule_interval(self.method, self.period)
    
  def stop(self):
    pyglet.clock.unschedule(self.method)
  
  def _on(self, val=False):
    if val: self.start()
    else:   self.stop()
    
    
    
