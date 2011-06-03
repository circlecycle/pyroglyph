"""
Numpy arrays with pyglet's vertex lists.
"""

import pyglet, random
from pyglet import *
from vbo import *

#let's begin

# this integrates numpy arrays into pyglet.graphics (from above)!
install()

#make a new opengl window
window = pyglet.window.Window(width=640, height=480)

@window.event
def on_resize(x, y):
    glViewport(0, 0, x, y)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()      
    glOrtho(0, x, 0, y, -1, 1) 
    glMatrixMode(GL_MODELVIEW)
    glLineWidth(1.)

@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    moveQuads()
    batch.draw()

@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.ESCAPE:
        sys.exit()
    
@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    pass
    
#make a new batch of VBOs!
batch = pyglet.graphics.Batch()
#how many boxes to draw?
boxes = 1000
#how many boxes should we animate out of the whole?
boxes_to_move = 100
#where we store our VBO's for reference
quads = []    
#our needs for geometry are embarassingly simple. This square is used for everything.
box = square()

#when this is called edit our VBO's such that some number of them animate
setupDone = False
def moveQuads():
    global setupDone, boxes
    for i, quad in enumerate(quads):
        if setupDone and i < (boxes - boxes_to_move): 
            continue
        x, y, s = random.randint(0, 640), random.randint(0, 480), random.randint(1, 100)
        v = square()
        v = dot(scale(s), v)
        v = dot(translate(x, y), v)
        quad.vertices[:] = v
    setupDone = True

#finally make a few VBOs to play with, which are really nothing more then what you 
#get back when the batch object returns a reference to geometry we pass in.
for i in range(boxes):
    quads.append(
        batch.add(
            4, GL_QUADS, None,
            ('v4f', box.transpose().flat),
            ('c4B', color(random.randint(0, 255), 0, 0, 255).transpose().flat)
        )
    )

#run the pyglet main loop, sit back, and enjoy!
try:
    pyglet.app.run()
except KeyboardInterrupt:
    sys.exit()
