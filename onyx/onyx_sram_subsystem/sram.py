import magma as m


class Memory(m.Generator2):
    def __init__(self, height, T):
        # TODO: Read latency?
        # Check Alex's email for
        #  * interface
        #  * redundancy
        addr_width = m.bitutils.clog2(height)
        self.io = m.IO(
            RADDR=m.In(m.Bits[addr_width]),
            RDATA=m.Out(T),
            WADDR=m.In(m.Bits[addr_width]),
            WDATA=m.In(T),
            WE=m.In(m.Enable),
            RE=m.In(m.Enable),
        ) + m.ClockIO()

