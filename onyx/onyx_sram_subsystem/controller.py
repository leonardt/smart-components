import magma as m


def make_APBIntf(addr_width: int, data_width: int):
    class APBIntf(m.Product):
        PADDR = m.Out(m.UInt[addr_width])
        PSEL = m.Out(m.Bit)
        PENABLE = m.Out(m.Bit)
        PWRITE = m.Out(m.Bit)
        PWDATA = m.Out(m.UInt[data_width])
        PREADY = m.In(m.Bit)
        PRDATA = m.In(m.UInt[data_width])
        PSLVERR = m.In(m.Bit)
    return APBIntf


class Controller(m.Generator2):
    def __init__(self,
                 id: int = 0x5A5A5A5A,
                 addr_width: int = 32,
                 data_width: int = 32):

        # TODO: What width will this be? We may need multiple addresses
        col_cfg_T = m.Bits[data_width]

        self.io = m.IO(power_gate=m.Out(m.Bit),
                       deep_sleep=m.Out(m.Bit),
                       col_cfg=m.Out(col_cfg_T))
        self.io += m.IO(
            **dict(m.Flip(make_APBIntf(addr_width, data_width)).field_dict.items())
        )
        self.io += m.clock_io.gen_clock_io(reset_type=m.AsyncResetN)

        read_data = m.Register(m.UInt[data_width], reset_type=m.AsyncResetN)()

        pready = m.Register(m.Bit, reset_type=m.AsyncResetN)()
        pslverr = m.Register(m.Bit, reset_type=m.AsyncResetN)()

        setup_phase = self.io.PSEL & ~self.io.PENABLE
        wr_en = setup_phase & self.io.PWRITE
        rd_en = setup_phase & ~self.io.PWRITE

        self.io.PRDATA @= read_data.O
        self.io.PREADY @= pready.O
        self.io.PSLVERR @= pslverr.O

        deep_sleep = m.Register(m.Bit)()
        power_gate = m.Register(m.Bit)()
        col_cfg = m.Register(col_cfg_T)()

        self.io.deep_sleep @= deep_sleep.O
        self.io.power_gate @= power_gate.O
        self.io.col_cfg @= col_cfg.O

        @m.inline_combinational()
        def logic():
            deep_sleep.I @= deep_sleep.O
            power_gate.I @= power_gate.O
            col_cfg.I @= col_cfg.O

            if wr_en:
                if self.io.PADDR[2:4] == 0:
                    deep_sleep.I @= self.io.PWDATA[0]
                elif self.io.PADDR[2:4] == 1:
                    power_gate.I @= self.io.PWDATA[0]
                elif self.io.PADDR[2:4] == 2:
                    col_cfg.I @= self.io.PWDATA

            read_data.I @= read_data.O
            if rd_en:
                if self.io.PADDR[2:4] == 0:
                    read_data.I @= m.bits(deep_sleep.O, data_width)
                elif self.io.PADDR[2:4] == 1:
                    read_data.I @= m.bits(power_gate.O, data_width)
                elif self.io.PADDR[2:4] == 2:
                    read_data.I @= col_cfg.O

            pready.I @= False
            if rd_en:
                pready.I @= True

            pslverr.I @= False
            if rd_en & (self.io.PADDR[2:4] > 2):
                pslverr.I @= True


