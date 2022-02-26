import magma as m

# I am not making the read latency a generator param
# as it is not paramater of Chisel provided by Gedeon
READ_LATENCY: int = 1

class SRAMBase(m.Generator2):
    def __init__(self,
            addr_width: int,
            data_width: int,
            has_byte_enable: bool,
            ):

        if addr_width <= 0:
            raise ValueError()

        if data_width <= 0:
            raise ValueError()

        if has_byte_enable:
            raise NotImplementedError('Byte Enable not currently supported')

        height: int = 1 << addr_width

        T = m.Bits[data_width]

        self.io = m.IO(
            CEn = m.In(m.Enable),
            WDATA = m.In(T),
            WEn = m.In(m.Enable),
            RDATA = m.Out(T),
            REn = m.In(m.Enable),
        ) + m.ClockIO()

        if has_byte_enable:
            self.io += m.IO(
                WBEn = m.Bits[data_width/8]
             )

        self.memory = m.Memory(height, T,
            read_latency=READ_LATENCY,
            has_read_enable=True)()

        self.memory.RE @= self.re
        self.memory.WE @= self.we


        self.memory.WDATA @= self.io.WDATA
        self.io.RDATA @= self.memory.RDATA

    @property
    def ce(self):
        return ~self.io.CEn

    @property
    def re(self):
        return self.ce & self.io.REn

    @property
    def we(self):
        return self.ce & self.io.WEn

class SRAMSingle(SRAMBase):
    def __init__(self,
            addr_width: int,
            data_width: int,
            has_byte_enable: bool,
            ):

        super().__init__(addr_width, data_width, has_byte_enable)

        self.io += m.IO(
            ADDR = m.In(m.Bits[addr_width]),
        )

        self.memory.RADDR @= self.io.ADDR
        self.memory.WADDR @= self.io.ADDR

class SRAMDouble(SRAMBase):
    def __init__(self,
            addr_width: int,
            data_width: int,
            has_byte_enable: bool,
            ):

        super().__init__(addr_width, data_width, has_byte_enable)

        self.io += m.IO(
            WADDR = m.In(m.Bits[addr_width]),
            RADDR = m.In(m.Bits[addr_width]),
        )

        self.memory.RADDR @= self.io.WADDR
        self.memory.WADDR @= self.io.RADDR

