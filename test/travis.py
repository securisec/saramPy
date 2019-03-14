from saramPy import Saram, SaramHelpers, __version__
from pprint import pprint

def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))

s = Saram(
    token='Some Token',
    user='SomeUser',
    local=True
)

test = 'Test'

dump(s)

s.run_command('ls')
s.script_read_self(comment='comment')
s.script_dump(comment='comment')
s.variable_output(test, comment='comment')
print()
print()
print('Version:', __version__)