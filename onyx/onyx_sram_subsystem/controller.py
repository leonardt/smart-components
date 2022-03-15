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
                 num_r_cols: int,
                 num_v_cols: int,
                 magic_id: int = 0x5A5A5A5A,
                 addr_width: int = 32,
                 data_width: int = 32):

        rcf_len = m.bitutils.clog2safe(num_v_cols)
        self.io = m.IO(power_gate=m.Out(m.Bit),
                       deep_sleep=m.Out(m.Bit),
                       wake_ack=m.In(m.Bit),
                       RCE=m.Out(m.Bits[num_r_cols]),
                       **{f"RCF{i}A": m.Out(m.Bits[rcf_len])
                          for i in range(num_r_cols)})
        self.io += m.IO(
            **dict(m.Flip(make_APBIntf(addr_width,
                                       data_width)).field_dict.items())
        )
        self.io += m.clock_io.gen_clock_io(reset_type=m.AsyncResetN)

        read_data = m.Register(m.UInt[data_width], reset_type=m.AsyncResetN)()

        self.io.PREADY @= 1
        pslverr = m.Register(m.Bit, reset_type=m.AsyncResetN)()

        setup_phase = self.io.PSEL & ~self.io.PENABLE
        wr_en = setup_phase & self.io.PWRITE
        rd_en = setup_phase & ~self.io.PWRITE

        self.io.PRDATA @= read_data.O
        self.io.PSLVERR @= pslverr.O

        deep_sleep = m.Register(m.Bit,
                                reset_type=m.AsyncResetN)(name="deep_sleep_reg")
        power_gate = m.Register(m.Bit,
                                reset_type=m.AsyncResetN)(name="power_gate_reg")
        RCE = m.Register(m.Bits[num_r_cols],
                         reset_type=m.AsyncResetN)(name="RCE_reg")

        rcf_regs = [
            m.Register(m.Bits[rcf_len],
                       reset_type=m.AsyncResetN)(name=f"RCF{i}A_reg")
            for i in range(num_r_cols)
        ]
        # TODO: Will the memory hold this high or pulse it? Assume pulse for
        # now and hold register high until cleared by a read
        wake_ack = m.Register(m.Bit, reset_type=m.AsyncResetN)()

        self.io.deep_sleep @= deep_sleep.O
        self.io.power_gate @= power_gate.O

        # TODO: Need to validate data_width vs num_r_cols/num_v_cols for
        # read/write logic
        self.io.RCE @= RCE.O

        for i in range(num_r_cols):
            getattr(self.io, f"RCF{i}A").wire(rcf_regs[i].O)
            rcf_regs[i].I @= m.mux([
                rcf_regs[i].O,
                self.io.PWDATA[:m.bitutils.clog2safe(num_v_cols)]
            ], self.io.PADDR[2:5] == (3 + i))

        read_data.I @= m.mux([
            m.bits(deep_sleep.O, data_width),
            m.bits(power_gate.O, data_width),
            m.zext_to(RCE.O, data_width),
        ] + [m.zext_to(reg.O, data_width) for reg in rcf_regs] + [
            m.bits(wake_ack.O, data_width),
            magic_id
        ], self.io.PADDR[2:5])

        @m.inline_combinational()
        def logic():
            deep_sleep.I @= deep_sleep.O
            power_gate.I @= power_gate.O
            wake_ack.I @= wake_ack.O

            RCE.I @= RCE.O

            if self.io.wake_ack:
                wake_ack.I @= True

            if rd_en & (self.io.PADDR[2:5] == 3):
                wake_ack.I @= False

            if wr_en:
                if self.io.PADDR[2:5] == 0:
                    deep_sleep.I @= self.io.PWDATA[0]
                elif self.io.PADDR[2:5] == 1:
                    power_gate.I @= self.io.PWDATA[0]
                elif self.io.PADDR[2:5] == 2:
                    RCE.I @= self.io.PWDATA[:num_r_cols]

            pslverr.I @= False
            if rd_en & (self.io.PADDR[2:5] > 4 + num_r_cols):
                pslverr.I @= True

            # TODO: We could report write errors too?

        # Avoid verilator UNUSED error for unused bits
        self.io.PADDR.unused()
        self.io.PWDATA.unused()


if __name__ == "__main__":
    m.compile("build/Controller", Controller(2, 32 / 4))
