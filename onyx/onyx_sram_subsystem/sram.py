import magma as m
import hwtypes as hw
from onyx_sram_subsystem.init_mem import InitMem


class SRAM(m.Generator2):
    class CMD(m.Enum):
        INIT = 0

    def __init__(self, height, T):
        addr_width = m.bitutils.clog2(height)
        self.io = m.IO(
            WE=m.In(m.Enable),
            RE=m.In(m.Enable),
            ADDR=m.In(m.Bits[addr_width]),
            WDATA=m.In(T),
            RDATA=m.Out(T),
            command=m.In(m.Bits[8])
            # TODO: Add command enable
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

        # TODO: This would make a nice coroutine generator
        state = m.Register(m.Bits[8])()

        @m.inline_combinational()
        def controller():
            state.I @= state.O
            mem.RE @= self.io.RE
            mem.WE @= self.io.WE
            # TODO: comparison to Enum (magma or python) fails, likely an env
            # issue?
            # if self.io.command == SRAM.CMD.INIT:
            if self.io.command == 1:
                state.I @= 1
            # TODO: Off-by-one in init mem logic?
            # elif state.O == 1:
            #     mem.WE @= init_seq[0]["WE"]
            #     mem.RE @= init_seq[0]["RE"]
            #     state.I @= 2
            elif state.O == 1:
                mem.WE @= init_seq[1]["WE"]
                mem.RE @= init_seq[1]["RE"]
                state.I @= 2
            elif state.O == 2:
                mem.WE @= init_seq[2]["WE"]
                mem.RE @= init_seq[2]["RE"]
                state.I @= 0
