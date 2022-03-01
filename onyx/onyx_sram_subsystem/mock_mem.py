import magma as m

# I am not making the read latency a generator param
# as it is not parameter of Chisel provided by Gedeon
READ_LATENCY: int = 1

class SRAMBase(m.Generator2):
    # *args, **kwargs for inheritance reasons
    def __init__(self,
            addr_width: int,
            data_width: int,
            has_byte_enable: bool,
            *args,
            **kwargs,
            ):
        self._init_attrs(addr_width, data_width, has_byte_enable, *args, **kwargs)
        self._init_io()
        self._instance_mem()


    def _init_attrs(self,
            addr_width: int,
            data_width: int,
            has_byte_enable: bool,
            *args,
            **kwargs
            ):

        if addr_width <= 0:
            raise ValueError()

        if data_width <= 0:
            raise ValueError()

        if has_byte_enable:
            raise NotImplementedError('Byte Enable not currently supported')

        self.addr_width = addr_width
        self.data_width = data_width
        self.has_byte_enable = has_byte_enable

    def _init_io(self):
        T = m.Bits[self.data_width]

        self.io = m.IO(
            CEn = m.In(m.Enable),
            WDATA = m.In(T),
            WEn = m.In(m.Enable),
            RDATA = m.Out(T),
            REn = m.In(m.Enable),
        ) + m.ClockIO()

        if self.has_byte_enable:
            self.io += m.IO(
                WBEn = m.Bits[data_width/8]
            )

    def _instance_mem(self):
        self.memory = m.Memory(
            1 << self.addr_width,
            m.Bits[self.data_width],
            read_latency=READ_LATENCY,
            has_read_enable=True
        )()

    def _read(self, addr):
        self.memory.RE @= self.re
        self.memory.RADDR @= addr
        return self.memory.RDATA

    def _write(self, addr, data):
        self.memory.WE @= self.we
        self.memory.WADDR @= addr
        self.memory.WDATA @= data

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
            *args,
            **kwargs,
            ):

        super().__init__(addr_width, data_width, has_byte_enable, *args, **kwargs)

        self.io.RDATA @= self._read(self.io.ADDR)
        self._write(self.io.ADDR, self.io.WDATA)

    def _init_io(self):
        super()._init_io()
        self.io += m.IO(
            ADDR = m.In(m.Bits[self.addr_width]),
        )


class SRAMDouble(SRAMBase):
    def __init__(self,
            addr_width: int,
            data_width: int,
            has_byte_enable: bool,
            *args,
            **kwargs,
            ):

        super().__init__(addr_width, data_width, has_byte_enable, *args, **kwargs)

        self.io.RDATA @= self._read(self.io.RADDR)
        self._write(self.io.WADDR, self.io.WDATA)

    def _init_io(self):
        super()._init_io()
        self.io += m.IO(
            WADDR = m.In(m.Bits[self.addr_width]),
            RADDR = m.In(m.Bits[self.addr_width]),
        )


class SRAMStateful(SRAMDouble):
    class CMD(m.Enum):
        NOP  = 0  # have a nop so that CMD actually has more than 1 cmd
        INIT = 1

    class State(m.Enum):
        SLEEP = 0
        BOOT = 1
        READY = 2

    def __init__(self,
            addr_width: int,
            data_width: int,
            has_byte_enable: bool,
            col_width: int = 4,
            debug: bool = False,
            *args,
            **kwargs
            ):

        super().__init__(addr_width, data_width, has_byte_enable, col_width, debug, *args, **kwargs)
        # set up some aliases
        State = type(self).State
        CMD = type(self).CMD
        state = self.state
        current_state = self.current_state

        @m.inline_combinational()
        def controller():
            mask_in = m.Bits[self.num_cols](0)
            mask_en = m.Bit(0)
            if self.io.CEn:
                next_state = State.SLEEP
            elif current_state == State.SLEEP:
                next_state = State.BOOT
            elif current_state == State.BOOT:
                if self.io.cmd == CMD.INIT:
                    next_state = State.READY
                    # TODO: validate mask?
                    mask_in = self.io.WDATA[:self.num_cols]
                    mesk_en = m.Bit(1)
                else:
                    # cmd == CMD.NOP
                    next_state = State.BOOT
            else:
                # current_state == READY
                next_state = State.READY
            state.I @= next_state
            self.mask_reg.I @= mask_in
            self.mask_reg.CE @= mask_en

        if debug:
            self.io.current_state @= self.current_state
            self.io.mask @= self.mask_reg.O
            self.io.next_state @= state.I.value()


    def _init_attrs(self,
            addr_width: int,
            data_width: int,
            has_byte_enable: bool,
            col_width: int,
            debug: bool,
            *args,
            **kwargs
            ):
        super()._init_attrs(
                addr_width,
                data_width,
                has_byte_enable,
                *args,
                **kwargs)

        if col_width <= 0:
            raise ValueError()

        if data_width % col_width != 0:
            raise ValueError()

        self.state = m.Register(init=type(self).State.SLEEP)()
        self.current_state = self.state.O
        self.col_width = col_width
        self.debug = debug
        self.mask_reg = m.Register(
            T=m.Bits[self.num_cols],
            has_enable=True
        )()

    def _init_io(self):
        super()._init_io()
        self.io += m.IO(
            cmd = m.In(type(self).CMD)
        )
        if self.debug:
            self.io += m.IO(
                current_state = m.Out(type(self).State),
                next_state = m.Out(type(self).State),
                mask = m.Out(m.Bits[self.num_cols])
            )


    @property
    def ce(self):
        return super().ce & (self.current_state == type(self).State.READY)

    @property
    def num_cols(self):
        return self.data_width//self.col_width

    def _instance_mem(self):
        self.cols = [
            m.Memory(
                1 << self.addr_width,
                m.Bits[self.col_width],
                read_latency=READ_LATENCY,
                has_read_enable=True
                )()
            for _ in range(self.num_cols + 1) # + 1 for redundancy
        ]

    def _read(self, addr):
        outputs = []
        shift = m.Bit(0)
        for i, mem in enumerate(self.cols):
            # this logic isn't strictly necessary
            # it disables the RE on the masked column
            # and only enables the redundant column if needed
            # Could just broadcast self.re
            if i < self.num_cols:
                shift |= self.mask_reg.O[i]
                mem.RE @= self.re & ~self.mask_reg.O[i]
            else:
                # redundancy column
                mem.RE @= self.re & shift

            mem.RADDR @= addr
            outputs.append(mem.RDATA)

        rdata = None
        # using these shift makes this potentially extensible to
        # multiple redundancy columns. Also makes write less crazy
        # as we don't need build a giant mux tree into the redundant
        # column's WDATA
        shift = m.Bit(0)
        for i in range(self.num_cols):
            shift |= self.mask_reg.O[i]
            if rdata is None:
                rdata = shift.ite(
                    outputs[i+1],
                    outputs[i]
                )
            else:
                rdata = rdata.concat(shift.ite(
                    outputs[i+1],
                    outputs[i]
                ))

        assert isinstance(rdata, m.Bits[self.data_width])

        return rdata

    def _write(self, addr, data):
        inputs = [
            data[i*self.col_width:(i+1)*self.col_width]
            for i in range(self.num_cols)
        ]

        assert all(isinstance(x, m.Bits[self.col_width]) for x in inputs)

        shift = m.Bit(0)
        for i, mem in enumerate(self.cols):
            # this logic isn't strictly necessary
            # similar to _read
            if i < self.num_cols:
                shift |= self.mask_reg.O[i]
                mem.WE @= self.we & ~self.mask_reg.O[i]
            else:
                mem.WE @= self.we & shift
            mem.WADDR @= addr

        # each input is either fed to the current column or the next
        # so each column gets its input either from current input or
        # the previous
        shift = m.Bit(0)
        for i, mem in enumerate(self.cols):
            if i == 0:
                # there is no "previous"
                shift |= self.mask_reg.O[i]
                mem.WDATA @= inputs[i]
            elif i < self.num_cols:
                shift |= self.mask_reg.O[i]
                mem.WDATA @= shift.ite(
                    inputs[i-1],
                    inputs[i]
                )
            else:
                # there is no "current"
                mem.WDATA @= inputs[i-1]
