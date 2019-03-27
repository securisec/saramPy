from saramPy import Saram, __version__
from pprint import pprint
from saramPy.api import SaramAPI

def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))

s = Saram(
    token='Some Token',
    local=True
)

a = SaramAPI()

test = 'Test'

dump(s)
print('='*50)
dump(a)

s.run_command('ls')
s.script_read_self(comment='comment')
s.script_dump(comment='comment')
s.variable_output(test, comment='comment')
print()
print()
print('Version:', __version__)