import gc
import sys
from gevent.pywsgi import WSGIServer
import weakref




EMPTY_BYTES_SIZE = sys.getsizeof(b'')
def allocate_bytes(size):
    bytes_len = (size - EMPTY_BYTES_SIZE)
    return b'x' * bytes_len

class Foo():
    def __init__(self, name):
        self.name = name
    def populate(self):
        self.xxx = allocate_bytes(50*1024*1024)



from flask import Flask
app = Flask(__name__)

from memory_profiler import profile as mprofile

@mprofile
def cycle_ref():
    foo1 = Foo('foo1')
    foo1.populate()
    foo2 = Foo('foo2')
    foo2.populate()
    foo1.other = foo2
    foo2.other = foo1

@mprofile
def weak_ref():
    foo1 = Foo('foo1')
    foo1.populate()
    foo2 = Foo('foo2')
    foo2.populate()
    foo1.other = foo2
    ref_foo1 = weakref.ref(foo1)
    print(ref_foo1().name)
    foo2.other = ref_foo1


@mprofile
def dynamic_class():
    type1 = type("Geeks", (object, ), {
        "string_attribute": "Geeks 4 geeks !",
        "int_attribute": 1706256,
        "xxx": allocate_bytes(50*1024*1024)
    })

@mprofile
def static_class():
    aa = Foo('name')
    aa.populate()

@app.route("/")
def hello():
    gc.disable()
    weak_ref()
    # cycle_ref()
    # dynamic_class()
    # static_class()
    # print(gc.collect())
    return "Hello, World!"

@app.route("/gc")
def garbage_collect():
    gc.collect()
    return 'manually gc'

http_server = WSGIServer(('0.0.0.0', 6001), app)
http_server.serve_forever()