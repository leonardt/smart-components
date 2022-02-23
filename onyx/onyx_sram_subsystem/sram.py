import magma as m
import hwtypes as hw
from onyx_sram_subsystem.init_mem import InitMem


class SRAM(m.Generator2):
    def __init__(self, height, T):
        addr_width = m.bitutils.clog2(height)
        self.io = m.IO(
            WE=m.In(m.Enable),
            RE=m.In(m.Enable),
            ADDR=m.In(m.Bits[addr_width]),
            WDATA=m.In(T),
            RDATA=m.Out(T),
        ) + m.ClockIO()

        init_seq = (
            m.generator.ParamDict(WE=hw.Bit(0), RE=hw.Bit(0)),
            m.generator.ParamDict(WE=hw.Bit(1), RE=hw.Bit(1)),
            m.generator.ParamDict(WE=hw.Bit(0), RE=hw.Bit(0)),
        )
        # TODO: Should support 0 read latency (with no read enable)
        mem = InitMem(height, T, 1, init_seq)()
        mem.WADDR @= self.io.ADDR
        mem.WDATA @= self.io.WDATA

        mem.RADDR @= self.io.ADDR
        self.io.RDATA @= mem.RDATA

        mem.RE @= self.io.RE
        mem.WE @= self.io.WE
