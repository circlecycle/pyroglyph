class x:
  def __init__(self):
    a = """\
if self['%s']:
    self['%s'] = type(self['%s'])(self['%s'])
else:
    self['%s'] = type(%s)(%s)\
"""%('x', 'x', 'x', 'x', 'x', 'x', 'x')
    print a
    
x()

  