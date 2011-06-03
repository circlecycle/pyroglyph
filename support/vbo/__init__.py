"""
Numpy arrays with pyglet's vertex lists.
"""

import numpy
import ctypes
from pyglet.gl import *
from pyglet.graphics import vertexbuffer, vertexdomain

_installed = False
_VertexList = vertexdomain.VertexList

dot = numpy.dot

ctypes.pythonapi.PyBuffer_FromReadWriteMemory.restype = ctypes.py_object

def install():
    """
    Globally hooks in numpy arrays for pyglet.graphics.
    """
    global _installed
    if _installed:
       return 

    vertexdomain.VertexList = VertexList
    vertexbuffer.create_buffer = _with_numpy(
        vertexbuffer.create_buffer)
    vertexbuffer.create_mappable_buffer = _with_numpy(
        vertexbuffer.create_mappable_buffer)

        
def as_numpy_array(c_array):
    """
    Return a view of the c array as a numpy array, with the
    underlying memory shared.
    """
    return numpy.frombuffer(
        ctypes.pythonapi.PyBuffer_FromReadWriteMemory(
                c_array, ctypes.sizeof(c_array._type_) * len(c_array)),
        dtype=c_array._type_)


def _with_numpy(func):
    """
    Decorates the create_buffer and create_mappable_buffer in
    pyglet.grpahics.vertexbuffer that reinstantiates their returned
    vertex buffers with their equivalents in this module.
    """
    def new_func(
        size,
        target=GL_ARRAY_BUFFER,
        usage=GL_DYNAMIC_DRAW,
        vbo=True):
        a = func(size, target, usage, vbo)
        if type(a) == vertexbuffer.MappableVertexBufferObject:
            return NumpyMappableVertexBufferObject(size, target, usage)
        elif type(a) == vertexbuffer.VertexArray:
            return NumpyVertexArray(size)
        return a

    new_func.__name__ = func.__name__
    new_func.__dict__ = func.__dict__
    new_func.__doc__ = func.__doc__
    new_func._decorated_func = func

    return new_func


class NumpyVertexArray(vertexbuffer.VertexArray):
    def get_region(self, start, size, ptr_type):
        region = super(NumpyVertexArray, self).get_region(
            start, size, ptr_type)
        region.array = as_numpy_array(region.array)
        return region


class NumpyMappableVertexBufferObject(vertexbuffer.MappableVertexBufferObject):
    def get_region(self, start, size, ptr_type):
        region = super(NumpyMappableVertexBufferObject, self).get_region(
            start, size, ptr_type)
        region.array = as_numpy_array(region.array)
        return region


class VertexList(_VertexList):
    def _get_shaped_array(self, attribute_name):
        """
        Shapes and transposes the arrays retrieved by the
        vertexattribute property descriptors to reflect the
        vertex/attribute counts.
        """
        array = getattr(super(VertexList, self), '_get_%s' % attribute_name)()
        count = self.domain.attribute_names[attribute_name].count
        if len(array.shape) == 1:
            array.shape = (len(array) / count, count)
            array = array.transpose()
        getattr(self, '_%s_cache' % attribute_name).array = array
        return array

    def _get_colors(self):
        return self._get_shaped_array('colors')

    def _get_fog_coords(self):
        return self._get_shaped_array('fog_coords')

    def _get_edge_flags(self):
        return self._get_shaped_array('edge_flags')

    def _get_normals(self):
        return self._get_shaped_array('normals')

    def _get_secondary_colors(self):
        return self._get_shaped_array('secondary_colors')

    def _get_tex_coords(self):
        return self._get_shaped_array('tex_coords')

    def _get_vertices(self):
        return self._get_shaped_array('vertices')

    colors = property(
        _get_colors, _VertexList._set_colors,
        doc=_VertexList.colors.__doc__)

    fog_coords = property(
        _get_fog_coords, _VertexList._set_fog_coords,
        doc=_VertexList.fog_coords.__doc__)

    edge_flags = property(
        _get_edge_flags, _VertexList._set_edge_flags,
        doc=_VertexList.edge_flags.__doc__)

    normals = property(
        _get_normals, _VertexList._set_normals,
        doc=_VertexList.normals.__doc__)

    tex_coords = property(
        _get_tex_coords, _VertexList._set_tex_coords,
        doc=_VertexList.tex_coords.__doc__)

    vertices = property(
        _get_vertices, _VertexList._set_vertices,
        doc=_VertexList.vertices.__doc__)

# geometry
def square(size=1):
    return numpy.array(
        ((-size, -size, size,  size),
         (-size,  size, size, -size),
         ( 0,  0, 0,  0),
         ( 1,  1, 1,  1)),
        dtype=GLfloat)
        
def scale(size=1):
    return numpy.array(
        ((size, 0 , 0 , 0),
         (0 , size, 0 , 0),
         (0 , 0 , 1, 0),
         (0 , 0 , 0 , 1)),
        dtype=GLfloat)

def translate(x, y):
    return numpy.array(
        ((1, 0 , 0 , x),
         (0 , 1, 0 , y),
         (0 , 0 , 1, 0),
         (0 , 0 , 0 , 1)),
        dtype=GLfloat)

def color(r,g,b,a=255):
    return numpy.array(
        ((r, r, r, r),
         (g, g, g, g),
         (b, b, b, b),
         (a, a, a, a)),
        dtype='uint8')

def rotate(dx, dy, amt=.01):
    angle = dx*dy;
    rotate = numpy.array(
       ((cos(angle*amt), -sin(angle*amt), 0., 0.),
        (sin(angle*amt), cos(angle*amt),  0., 0.),
        (0., 0., 1., 0.),
        (0., 0., 0., 1.)),
       dtype=GLfloat)
    return rotate