

import sys
from xml.dom.minidom import parse, parseString
from Engine import Canvas, Cocoa, Helpers

def parse(xml=None):
    """
        Given a well formed xml document, parse it and return
        the canvas node that becomes the active namespace of the
        Viewable application.
    """
    
    # if they used a hashbang remove it to get a wellformed document
    
    if not xml:
        xml = file(Helpers.basepath+'Applications/cocoa.lzx').read()
    
    if xml.startswith("#!"):
      xml = xml[xml.index('\n'):]
    
    # parse the xml into a minidom object (no xmlish namespaces allowed with it!)
    try:                    
      documentElement = parseString(xml).documentElement
    except Exception, msg:  
      raise "The input program is not well-formed XML: "+`msg`
    
    #initialize the entire program namespace in this one fell swoop!
    canvas = Canvas.Node(documentElement)
    Cocoa.start()
  