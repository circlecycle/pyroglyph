from xml.etree.ElementTree import fromstring, tostring

class ObjectGraph:
    def __init__(self, elem):
        self.elem = elem
        
    def flatten(self):
        self.lines = []
        self.walk(self.elem)
        return self.lines
        
    def walk(self, elem, path=['self']):
        unnamedCounter = 0
        for node in elem.getchildren():
            if node.tag == 'class': continue
            
            #get the class name
            classname = node.tag
            
            #get the text of the node, if any
            if node.text and node.text.strip():
              node.attrib['text'] = node.text            
            else:
              node.attrib['text'] = ""

            #assign a name if one has not been provided.
            name = node.get('name')
            if not name:
              name = "%s_%s_anon"%(classname, unnamedCounter)
              unnamedCounter += 1
              
            #Get the context of the call (o)
            realPath = '.'.join(path)
                
            self.lines.append("""%s.%s = %s(%s, %s)"""%(realPath, name, classname, realPath, `attributes`)) 
            self.walk(node, path=path+[name])
        
        
        
if __name__ == '__main__':
    xml = """\
      <application>
        <class name="twoviews">
          <view name="one" x="10" y="10"/>
          <view x="20" y="20"/>
        </class>
        
        <view width="10" height="10">
          <button name="somename" text="hi">
            <handler on="mousedown">
              print 'button clicked'
            </handler>
          </button>
          <button text="hi"/>
          <handler on="mousedown">
            print "mousedown"
          </handler>
        </view>
        
        <button name="button" text="hi"/>
        
      </application>"""
    
    elem = fromstring(xml)
    
    og = ObjectGraph(elem)
    print '\n'.join(og.flatten())