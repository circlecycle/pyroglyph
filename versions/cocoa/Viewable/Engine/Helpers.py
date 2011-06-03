
import cPickle as pickle
import sys, Events

COCOA = 0
GL = 1

#which platform are we using?
platform = COCOA

#where is the code?
basepath = "/System/Library/Frameworks/Python.framework/Versions/2.5/Extras/lib/python/Viewable/"

#where are the libraries for the langauge?
baselibs = "/System/Library/Frameworks/Python.framework/Versions/2.5/Extras/lib/python/Viewable/Library"

def loadColors(pickleColors=False):  
  global basepath
  #if this is set to true regenerate the colors DB from the rgb.txt file
  
  if pickleColors:
    colors = {}
    colorFile = file(basepath+'Engine/rgb.txt').readlines()

    for line in colorFile:
      buf =  [x.strip() for x in line.split(' ') if x]
      r, g, b = [float(x)/255.0 for x in buf[:3]]
      name = ' '.join(buf[3:])
      colors[name] = (r,g,b)

    fp = file(basepath+'Engine/rgb.pkl', 'w')
    pickle.dump(colors, fp)
    fp.close()

  else:
    fp = file(basepath+'Engine/rgb.pkl')
    colors = pickle.load(fp)
    fp.close()
    
  return colors
  
  
def HTMLColorToRGB(colorstring):
  global colors
  """ convert 0xRRGGBB to an (R, G, B) tuple """
  colorstring = colorstring.strip()

  try:
    #if it's a hex value
    if colorstring.startswith('0x'): 
      colorstring = colorstring[2:]
      r, g, b = [int(n, 16)/255.0 for n in (colorstring[:2], colorstring[2:4], colorstring[4:])]

    #else if it's a color name
    elif colors.has_key(colorstring):
      r, g, b = colors[colorstring]

    #its a normalized color value:
    else:
      r, g, b = [float(x.strip()) for x in colorstring.split(',')]

  except Exception, msg:
    #if we are here it's an error, for sure.
    Events.Error(None, msg, "RGB value '%s' is not a valid color value")

  return (r, g, b)


#This function, if True is passed, will reparse rgb.txt into rgb.pkl. 
#otherwise it loads the pickle rgb.pkl - which is presumably much faster -
#to be used when a string color is specified.
colors = loadColors()