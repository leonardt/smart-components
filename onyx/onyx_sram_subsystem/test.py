import sys
import magma as m
import hwtypes as hw


class Foo(m.Generator2):
    def __init__(self):
        self.io = m.IO(
            wake_ack=m.Out(m.Bit),
        )
        self.io.wake_ack @= m.Bit(1)
        
class Bar(m.Generator2):
    def __init__(self):
        self.io = m.IO(
            wake_ack=m.Out(m.Bits[16]),
        )
        self.foo = Foo()()
        
        @m.inline_combinational()
        def controller():
            data_to_client = m.Bits[16](self.foo.wake_ack)
            # data_to_client = self.foo.wake_ack
            self.io.wake_ack @= data_to_client
Bar()            
