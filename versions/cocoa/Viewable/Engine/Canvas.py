
#the Viewable module, copyright, James Robey, 2008
#contact, circlecycle@gmail.com

import sys, time, threading, re, imp, weakref, copy
from xml.dom.minidom import getDOMImplementation, parse, parseString
import Helpers, Animation, Cocoa

####### just keep canvas reference handy so that other modules can find it, without fuss #################### # # #  #   #    #
canvas = None

#accumulators
INITS_ACCUMULATOR = []
CLASSES_ACCUMULATOR = {}
CONSTRAINTS_ACCUMULATOR = []
GLOBALS_ACCUMULATOR = []
FONTS_ACCUMULATOR = []

###################################################################################
####### NOTE the following class is recursive! #################### # # #  #   #    #
####### it is also the main entry point to starting the program 
####### it takes in a DOM and spits out a namespace fully equiped
####### with all of the LZX goodness, ready to go.
###################################################################################
    
class Node:
  """
    The basic recursive namespace building block that is initalized from a dom element.
    Node dispatches all of the namespace building behavior. 
    
    Usage (new canvas):   Canvas.Node(canvasElement)
          (new children): Canvas.Node(nodeElem, parent=parent)
  """  
  
  #constants
  USES_INNER_XML_TYPE = ['class', 'replicate', 'dataset', 'comment']
  CLASS_DECORATOR_NODES = ['attribute', 'handler', 'method', 'thread', 'class']
  CLASS_TAGS = ['class']
  TAG_NAME_REMAP = {'import':'_import', 'class':'_class'}
  NOT_CONSTRAINT_REGEX = re.compile("^(?!.*\$)")
  CONSTRAINT_REGEX = re.compile("^.*\$\{.*\}$")
  ONCE_CONSTRAINT_REGEX = re.compile("^.*\$\once{.*\}$")
  i = 0
  
  def __init__(self, elem, parent=False, after=False, attrs={}, topmostnode=True):
    """ All of this languages best moments happen in this function, 
        including all of the recursive magique.
    """
    
    global INITS_ACCUMULATOR, CLASSES_ACCUMULATOR, GLOBALS_ACCUMULATOR, CONSTRAINTS_ACCUMULATOR
    
    try:
      ####### initialze a Node with it's basic "private" attributes #################### # # #  #   #    #
    
      self.__dict__['childNodes'] = []
      self.__dict__['childViews'] = []
      self.__dict__['vbl_handlers'] = {}
      self.__dict__['vbl_displaytype'] = 'node'
      self.__dict__['vbl_elem'] = elem
      self.__dict__['vbl_classname'] = elem.tagName
      self.__dict__['vbl_after'] = after
      
      #cocoa view backing
      self.__dict__['vbl_cocoaview'] = None
    
      ####### expose useful "public" references #################### # # #  #   #    #
    
      self.__dict__['self'] = self
      self.__dict__['parent'] = parent
      self.__dict__['init'] = False
      self.__dict__['late'] = False
      self.__dict__['focus'] = False
  
      #add attributes from the "attrs" argument - as if it was "on the tag"
      #[setattr(self, key, attrs[key]) ]
      for key in attrs.keys():
        self.__dict__[key] = attrs[key]
          
      ####### initialize a node in it's namespace by running either the canvas  #################### # # #  #   #    #
      ####### or node variety of init function on it. This is base init         #################### # # #  #   #    #
      ####### not the level of initialization the tags themselved provide.      #################### # # #  #   #    #
  
      #if it has no parent, it's the canvas
      if not parent:  
        self.__initNameSpaceForCanvas()
        
      #else if we are initing a real object (not handler, method, class, etc)
      elif self.vbl_classname not in self.CLASS_DECORATOR_NODES:           
        
        ####### if this node represents something other then a base tag (defined in Classes) #################### # # #  #   #    #
        ####### copy over the dom nodes that the inherited classes provide.                   #################### # # #  #   #    #
        
        if CLASSES_ACCUMULATOR.has_key(self.vbl_classname):
          self.__buildclass(elem, CLASSES_ACCUMULATOR[self.vbl_classname])
        
        #initialize the node's namespace  
        self.__initNameSpaceForNode()
        
    
      ####### place global references to useful things into this nodes's namespace.  #################### # # #  #   #    #
      for obj in GLOBALS_ACCUMULATOR:
        self.__dict__[obj[0]] = obj[1]
      
      ####### copy attributes from dom onto node, finding constraints along the way #################### # # #  #   #    #
      
      if elem.attributes:
        for attr in elem.attributes.keys():
          value = elem.attributes[attr].value.strip()
        
          #THIS IS THE CONSTRAINT MAGIC. this will store a detected constraint away for
          #the second stage of processing done elsewhere.
          #or, if no constraint, just place the xml attribute's value into the nodes namespace
        
          if not elem.tagName in self.CLASS_TAGS:
            #no constraint found, set and carry on
            if self.NOT_CONSTRAINT_REGEX.search(value):
              self.__dict__[attr] = value
            
            #normal constraint found, add to processor
            elif self.CONSTRAINT_REGEX.search(value):
              CONSTRAINTS_ACCUMULATOR.append([self, (attr, value[2:-1], "always")])
            
            #constrain run once at init time, add to processor
            elif self.ONCE_CONSTRAINT_REGEX.search(value):
              CONSTRAINTS_ACCUMULATOR.append([self, (attr, value[6:-1], "once")])
            
      #the construct phase - this is equivalent to the "construct phase" - do work needed to initialize a 
      #node. This is different, of course, from the "init" event objects get when all of their children 
      #are also init'd
      self.__construct__()
    
      #if the node contains other nodes process them, or if just XML data skip it.
      if self.vbl_classname not in self.USES_INNER_XML_TYPE:
        #apply traits, if given, on any node that has them (essentially just a new class(es) of a given name)
        if self['traits']:
          for trait in [x.strip() for x in self['traits'].split(',') if x]:
            self.create(parseString("<%s/>"%trait).documentElement, topmostnode=False)
      
        ####### for each child elem present, recurse and make a new node (class) of a given type #################### # # #  #   #    #
        for child in elem.childNodes:
          #only look at element nodes (text nodes may comment in the future)
          if child.nodeType == child.ELEMENT_NODE:
            self.create(child, topmostnode=False)
          
        #We're ready to run construct stage handlers
        self.touch('construct')
        
      #node is finished, add the node to a list that get init events wherein the
      #order added gives the correct evaluation order naturally.
      INITS_ACCUMULATOR.append(self)
    
      if self.vbl_classname != 'canvas':
        self.touch('childNodes')
        
      #if this is the canvas (or the topmostnode of a parse operation), finish up by
      #sending out all init events and finally evaluating all collected constraints.
      if topmostnode:
        self._doinits()
      
    except Exception, msg:
      raise str("\n"+("-"*60)+"\nIn the tag:\n"+self.toxml()+"\nError: "+`msg`)
      
    #and.. we are done with the whole requested namespace! whew!
    
  ###################################################################################
  ######## end of the nodes recursive function #################### # # #  #   #    #
  ###################################################################################
  
  def __construct__(self):
    """ Classes that inherit from Node should use __construct__ for their initialization statements. 
        If they are subclassed-subclasses, they must call subclassed.__construct__(self) before leaving 
        the __construct__ method.
        
        NOTE: Node()'s __construct__ should not be called by direct subclasses - it will be called automatically - 
        this stub exists to preserve the recursive property of the class.
    """
    pass
    
  def __initNameSpaceForCanvas(self):
    global GLOBALS_ACCUMULATOR
    ####### set the this node as the global canvas for later reference #################### # # #  #   #    #
    globals()['canvas'] = self
    self.__dict__['canvas'] = self
    
    #the canvas starts dirty (needs to be redrawn)
    self.__dict__['dirty'] = True
    
    ####### the GLOBALS_ACCUMULATOR will hold references that are injected  #################### # # #  #   #    #
    ####### into every nodes' namespace. The canvas (of course) applies     #################### # # #  #   #    #
    
    GLOBALS_ACCUMULATOR.append(('canvas', self))
    
    ####### as do all the modules in the import attribute, which are imp #################### # # #  #   #    #
    
    [GLOBALS_ACCUMULATOR.append( ( x.strip(), _import(x.strip()) ) ) 
      for x in self.vbl_elem.getAttribute('import').split(',') 
        if x]
        
    ####### canvas specific initializations (since canvas is the plainest #################### # # #  #   #    #
    ####### Node there is no class)                                       #################### # # #  #   #    #
    
    ####### the drawing system wants to calculate positions accumulated on the parent #################### # # #  #   #    #
    ####### so all subnodes of the canvas will get these (makes sense, the canvas is  #################### # # #  #   #    #
    ####### always at 0,0,0 with visibility=true and opacity=1.                       #################### # # #  #   #    #
    
    self.applydefaults( {'title': "Viewable Application", 'framerate': 60.0, 'maxsize':"",
                         'bgcolor': '0xffffff', 'fgcolor': '0x000000',
                         'width':640, 'height':480, 'x':0, 'y':0, 'z':0,
                         'focusable':True, 'opacity':0, 'visible':False, 'transparent':False,
                         '_absX':0, '_absY':0, '_absZ':0, '_absV':True, '_absA':1, '_absFC':'0x000000',
                         'init':False, 'focused':self, 'lastFocused':None, '_uidcount':0, 'sizing':'off', 'rotate':0 } )
                     
    self.constrain(attr="focused", func=Events.handleFocused)
    
    #do platorm specific initializations.
    
    if Helpers.platform == Helpers.COCOA:
      self.__dict__['vbl_cocoaview'] = Cocoa.CocoaCanvas(self)
      #self.constrain(attr="title", func=Cocoa.changeWinTitle)
    
    elif Helpers.platform == Helpers.GL:
      self.constrain(attr="title", func=InitGL.changeWinTitle)
      
  def update(self):
    """empty because nodes have no visual update method, but we call it"""
    return True
                               
  def __initNameSpaceForNode(self):
    """ set values dealing with being a parent and also a child in the hiearchy """
    
    global canvas
      
    #place this onto the parents childNodes array (respect insertion point if specified)
    if self.vbl_after and self.vbl_after in self.parent.childNodes:
      self.parent.childNodes.insert(self.parent.childNodes.index(self.vbl_after), self)
    else:
      self.parent.childNodes.append(self)

    #if a name has been given on this node, make sure it's snuggled into it's parent's namespace
    if self.vbl_elem.hasAttribute('name'):  
      self.parent.__dict__[self.vbl_elem.getAttribute('name')] = self
      
    #if the child has an id place a reference to it under the canvas #################### # # #  #   #    #
    if self.vbl_elem.hasAttribute('id'):  
      canvas.__dict__[self.vbl_elem.getAttribute('id')] = self
        
  def setname(self, name):
    """ set or reset the name of this Node to a new one (on the parent Node)"""
    
    self.parent.__dict__[name] = self
    if getattr(self, 'name', False) and self.parent.__dict__.has_key(self.name):
      del self.parent.__dict__[self.name]
    self.__dict__['name'] = name

  #need to change the name in the global namespace when this happens
  def setid(self, name):
    """ set or reset the id of this Node to a new one (in the global namespace)"""
    
    g = self.canvas
    g[value] = self
    if getattr(self, 'id', False) and g.has_key(self.id):
      del g[self.id]
    self.__dict__['id'] = value
        
  def constrain(self, attr=None, func=None, set=False):
    """ make a constraint, that is, add to vbl_handlers on a target node a pointer
        to a function to call when it value changes. Setting set to 
        true (the default) also sets that value on the node. This is because
        before the init is completed, there may not be value to set!
    """
    
    #place a pointer to this new function as a listener on the node pointed to by the handler
    if not self.vbl_handlers.has_key(attr):
      self.__dict__['vbl_handlers'][attr] = []
    self.__dict__['vbl_handlers'][attr].append(func)
    
    #if the constraint is made after initialization, set its value immediately from the target
    if set: func(self[attr])
            
  def applydefaults(self, defaults):
    """
      For each key given in a 'default' dictionary, use it either as a default, 
      or as a casting type if the value is still a string form the DOM (aka the 
      first pass through the system)
    """
    #__construct__ float attributes if not present (convert from string if they are)
    for key in defaults.keys():
      #if no value is given use the default. 
      if not self.__dict__.has_key(key):  
        default = defaults[key]
        
      #Otherwise convert it to what it is supposed to be which in the case 
      #of True and False is streamlined for convienence (and a casting issue 
      #with bools)
      else:
        currval = self.__dict__[key]
        #do we need to cast it? (aka is still a string?)
        if type(currval) is type(u''):             
          #catch and convert True
          if currval.lower() == 'true':  
            default = True
          #catch and convert False
          elif currval.lower() == 'false':
            default = False
          #otherwise cast the value according to it's set default
          else:
            default = type(defaults[key])(currval)
        else:
          default = currval
      
      #set the value on the tag and move on.
      self.__dict__[key] = default
      
  def __getitem__(self, attr):
    """make it possible to get interior nodes dictionary style"""
    return getattr(self, attr, None)
      
  def __setitem__(self, attr, val):
    """make it possible to set interior nodes dictionary style"""
    setattr(self, attr, val)
    
  def create(self, elem, parent=None, after=False, attrs={}, topmostnode=True, msg=False):
    """ Create a new element, using the element dom, parent, and any attributes """
    
    parent = parent or self
  
    if type(elem) is type(""):
      elem = parseString('<%s/>'%elem).documentElement
    else:
      #IMPORTANT: if this isn't done then node operations will compound themselves
      #leading to very bad results (exponetial replication, for instance)
      elem = elem.cloneNode(deep=True)

    #the following is the same mechanism as in the nodes module (todo, functionize it?)
    tagname = elem.tagName

    #if it's a reserved python word annotate it:
    if self.TAG_NAME_REMAP.has_key(tagname):
      tagname = self.TAG_NAME_REMAP[tagname]

    #make the new objects in the tree using the element
    try:    func = getattr(Classes, tagname)
    except: raise "Error: A tag (class) is not defined:", tagname
  
    return func(elem, parent=parent, after=after, attrs=attrs, topmostnode=topmostnode)
    
  def delete(self):
    """ deletion is more complicated then normal because the namespace keeps many references.
        the solution is to use weak references where appropiate. the name and id references,
        the childNodes and childViews are real references, because we can always detect and
        remove those. others like Events.focused and self are weak. this will be enough to scrap 
        the object, one hopes! """
        
    #remove from parent's namespace if there
    if getattr(self, 'name', False) and self.parent.__dict__.has_key(self.name):
      del self.parent.__dict__[self.name]
      
    #remove from the global scope if applicable
    if getattr(self.canvas, 'id', False) and self.canvas.has_key(self.id):
      del self.canvas[self.id]
      
    #remove references from childNodes and childViews as appropiate
    if self in self.parent.childNodes:
      del self.parent.childNodes[self.parent.childNodes.index(self)]
    
    #only do this if the tag is a view as well (in both lists)
    if self in self.parent.childViews:
      del self.parent.childViews[self.parent.childViews.index(self)]
    
    #self.parent.vbl_elem.removeChild(self.vbl_elem)
    
    #finally delete thyself
    del self
    
  def __setattr__(self, attr, value):
    """ and.. the very heart of delegates, events, constraints, etc! """
    
    #set the value
    self.__dict__[attr] = value
    
    #set the canvas as being dirty - that is, something changed and we need to redraw!
    #this is an optimaztion that may be removed with runtimes other then openGL.
    self.canvas.__dict__['dirty'] = True

    #distribute this value to all other listeners for this attribute
    if self.vbl_handlers.has_key(attr):
      [listener(value) for listener in self.vbl_handlers[attr]]
    
    if self['vbl_cocoaview']:  
      self.vbl_cocoaview.vbl_update()
        
  def touch(self, attr):
    """ set off the handlers for a given attribute without changing 
        it's value (self.x = self.x would be similar.)
    """
    
    #distribute this value to all other listeners for this attribute
    if self.vbl_handlers.has_key(attr):
      [listener(self[attr]) for listener in self.vbl_handlers[attr]]
      
  def animate(self, attrname, to, dur):
    """stub that creates and returns a new Animator object for this node 
       the animator object automatically registers with the animation
       event loop. 
    """
    return Animation.Animator(self, attrname, self[attrname], to, dur)
        
  def __buildclass(self, elem, classNode):
    """ recursive class to build out a classses inheritance inner node set from 
        accumulated doms. That is, each time a class is made it's inner dom is 
        saved. to make the LZX inheritance model, all inner nodes from each
        class in the chain need to be inserted into the current element to make
        the class have all that has been requested via the extends attribute.
    """
    
    global CLASSES_ACCUMULATOR
    
    #retrieve classes' dom
    classElem = classNode.vbl_elem
    
    #copy over any missing attributes from the class dom's top node - skip 'name'!!
    [elem.setAttribute(attrname, classElem.attributes[attrname].value) 
      for attrname in classElem.attributes.keys() 
        if not elem.getAttribute(attrname) and attrname != 'name']
        
    #insert all XML from the class definition before the first node of the instance
    nodes = classElem.childNodes[:]
    nodes.reverse()
    [elem.insertBefore(subnode.cloneNode(deep=True), elem.firstChild) 
      for subnode in nodes
        if subnode.nodeType == subnode.ELEMENT_NODE]
    
    extends = classElem.getAttribute('extends').strip()
    if extends and CLASSES_ACCUMULATOR.has_key(extends):
      self.__buildclass(elem, CLASSES_ACCUMULATOR[extends])
        
      
  def _evaluateconstraints(self, val=False):
    """ when a constraint is detected it is added to singleton list without any action
        being taken. After the first stage of initialization, go back and give all those
        constraints values (now that everything exists)
    """
    
    global CONSTRAINTS_ACCUMULATOR, EARLY_CONSTRAINTS_ACCUMULATOR
    
    #save then erase 'em pending the next round.    
    constraints = CONSTRAINTS_ACCUMULATOR[:]
    CONSTRAINTS_ACCUMULATOR = []
    
    for nodeToProcess in constraints:
      node, constraint = nodeToProcess
      #get the constraint info
      attr, entry, ofType = constraint

      #split it into form one and form two parts
      entry = entry.split('->')

      #if they only provide the shortened form double into long form aka ${parent.x->parent.x}
      if len(entry) > 1:  watch, perform = entry
      else:               watch, perform = entry[0], entry[0]

      #make a constraint (or multiple constraints!!) using the normal "always" syntax
      if ofType == "always":
        pathsToCheck = []
        #handle form one
        constraintPaths = [x.strip() for x in watch.split(',') if x]
        for constraintPath in constraintPaths:
          fullpath = constraintPath.split('.')
          target = fullpath[-1]
          path = '.'.join(fullpath[:-1])
          pathsToCheck.append([path, target])

        #for each constraint make a new function to handle it
        for constraintPath in pathsToCheck:
          path, target = constraintPath
          #resolve the object
          obj = eval(path, node.__dict__)
          #if its a direct method link, set it
          #make the function in the node's namespace'
          funcname = "_dele_%s_%s"%(path.replace('.', '_'), target)
          funcbody = "def %s(value): self.%s = %s"%(funcname, attr, perform)
          #make the function and make a constraint to it
          exec funcbody in node.__dict__
          obj.constrain(attr=target, func=node.__dict__[funcname], set=True)
          
      #make a constraint, this one is for once (don't make a constraint)
      elif ofType == "once":
        setattr(node, attr, eval(watch, node.__dict__))
    

  def _doinits(self, msg=""):
    global INITS_ACCUMULATOR
    """ simply set init=true on all nodes accumluated, sending out the init events appropiately. """
    
    #use a copy so that other node calls can start building their own chains!
    toinit = INITS_ACCUMULATOR[:]
    INITS_ACCUMULATOR = []
    
    ##do all the outstanding early actions
    [setattr(node, 'early', True) for node in toinit]  
    
    ##do all the outstanding inits
    [setattr(node, 'init', True) for node in toinit]  
    
    #now that init statements have been run do the constraints:
    self._evaluateconstraints()
    
    #and the things for late (after everything has inited)
    [setattr(node, 'late', True) for node in toinit]  
    
  def toxml(self):
    """ print this node using the ORIGINAL DOM used to make this object (doesn't reflect updates to namespace) """
    dom = getDOMImplementation()
    doc = dom.createDocument(None, None, None)
    doc.appendChild(self.vbl_elem)
    tagContents = doc.toprettyxml()
    return tagContents[tagContents.index('\n'):]
    
  
###################################################################################
######## end of the node class #################### # # #  #   #    #
###################################################################################
      
#################################################################################
### HELPER FUNCTIONS ############################################################
#################################################################################
  
def normalize_python(node=None, dom=None, buf=None, prefix=None, definition=False):
  """
    This analyzes a piece of python script to derive the proper first
    indent (by looking at the first line) and adjusts the rest accordingly.
    Pass either a dom or a string, with an _unindented_ prefix and then 
    definition line that wraps the code for later execution into a namespace.
  """
  #get text element value from one of the possible ones
  if dom:     value = ''.join([x.nodeValue for x in node.childNodes])
  elif node:  value = ''.join([x.nodeValue for x in node.vbl_elem.childNodes])
  else:       value = buf
  
  value = value.split('\n')
  
  #find indent
  for line in value:
    if not line.strip(): continue
    else: 
      indent = len(line) - len(line.lstrip())
      break
      
  #if the python material is contained in a definition, 
  #add that definition and increase the indent to compensate
  script = []
  definitionIndent = ""
  if definition: 
    definitionIndent = "    "
    script.append(definition)
    
  #normalize script tab depth, adding an indent if wrapped in a defintion
  for line in value:
    strippedline = line.strip()
    if not strippedline or strippedline[0] == '#': continue
    script.append("%s%s"%(definitionIndent, line[indent:]))
  script = '\n'.join(script)
  
  #apply a prefix if given (at the end - it's not indented so it's the right time, after adjustment above)
  if prefix:  
    script = "%s\n%s"%(prefix, script)
  return script
  
def _import(name):
    """ Given a module name, import it programmatically (this doesn't import if already done) """
    
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
    
#these need to be imported last (important!) because they use values stored in this module
import Events, Classes
  
