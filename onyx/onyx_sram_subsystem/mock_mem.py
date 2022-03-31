import magma as m

# I am not making the read latency a generator param
# as it is not parameter of Chisel provided by Gedeon
READ_LATENCY: int = 0


class SRAMBase(m.Generator2):
    # *args, **kwargs for inheritance reasons
    def __init__(
        self,
        addr_width: int,
        data_width: int,
        has_byte_enable: bool = False,
        *args,
        **kwargs,
    ):
        self._init_attrs(addr_width, data_width, has_byte_enable, *args,
                         **kwargs)
        self._init_io()
        self._instance_subcomponents()
        self._connect()

    def _init_attrs(self, addr_width: int, data_width: int,
                    has_byte_enable: bool, *args, **kwargs):

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
            CEn=m.In(m.Enable),
            WDATA=m.In(T),
            WEn=m.In(m.Enable),
            RDATA=m.Out(T),
            REn=m.In(m.Enable),
        ) + m.ClockIO()

        if self.has_byte_enable:
            self.io += m.IO(WBEn=m.Bits[data_width / 8])

    def _instance_subcomponents(self):
        self.memory = m.Memory(1 << self.addr_width,
                               m.Bits[self.data_width],
                               read_latency=READ_LATENCY,
                               has_read_enable=False)()

    def _connect(self):
        pass

    def _read(self, addr):
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

    def _init_io(self):
        super()._init_io()
        self.io += m.IO(ADDR=m.In(m.Bits[self.addr_width]), )

    def _connect(self):
        super()._connect()
        self.io.RDATA @= self._read(self.io.ADDR)
        self._write(self.io.ADDR, self.io.WDATA)


class SRAMDouble(SRAMBase):

    def _init_io(self):
        super()._init_io()
        self.io += m.IO(
            WADDR=m.In(m.Bits[self.addr_width]),
            RADDR=m.In(m.Bits[self.addr_width]),
        )

    def _connect(self):
        super()._connect()
        self.io.RDATA @= self._read(self.io.RADDR)
        self._write(self.io.WADDR, self.io.WDATA)


def _binary_to_unary(data: m.Bits):
    out_size = 1 << data.size
    return m.Bits[out_size](1) << data.zext(out_size - data.size)


def _tree_reduce(f, lst):
    n = len(lst)
    if n == 1:
        return lst[0]
    elif n == 2:
        return f(*lst)
    else:
        assert n >= 3
        return f(_tree_reduce(f, lst[:n // 2]), _tree_reduce(f, lst[n // 2:]))


class SRAMRedundancyMixin:

    def __init__(
        self,
        addr_width: int,
        data_width: int,
        has_byte_enable: bool = False,
        col_width: int = 4,
        num_r_cols: int = 1,
        debug: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(addr_width, data_width, has_byte_enable, col_width,
                         num_r_cols, debug, *args, **kwargs)

    def _init_attrs(self, addr_width: int, data_width: int,
                    has_byte_enable: bool, col_width: int, num_r_cols: int,
                    debug: bool, *args, **kwargs):
        super()._init_attrs(addr_width, data_width, has_byte_enable, debug,
                            *args, **kwargs)

        if col_width <= 0:
            raise ValueError()

        if data_width % col_width != 0:
            raise ValueError()

        if num_r_cols != 1:
            raise NotImplementedError()

        self.col_width = col_width
        self.num_r_cols = num_r_cols
        self.debug = debug

    @property
    def num_v_cols(self):
        return self.data_width // self.col_width

    @property
    def num_p_cols(self):
        return self.num_v_cols + self.num_r_cols

    def _init_io(self):
        super()._init_io()
        self.io += m.IO(RCE=m.In(m.Bits[self.num_r_cols]),
                        **{
                            f'RCF{i}A':
                            m.In(m.Bits[m.bitutils.clog2safe(self.num_v_cols)])
                            for i in range(self.num_r_cols)})

    def _instance_subcomponents(self):
        self.cols = [
            m.Memory(
                1 << self.addr_width,
                m.Bits[self.col_width],
                read_latency=READ_LATENCY,
                has_read_enable=False,
            )() for _ in range(self.num_p_cols)
        ]

        mask_t = m.Bits[self.num_v_cols]
        zero = mask_t(0)
        RCFs = [
            self.io.RCE[i].ite(_binary_to_unary(getattr(self.io, f'RCF{i}A')),
                               zero) for i in range(self.num_r_cols)
        ]

        self.mask = _tree_reduce(mask_t.bvor, RCFs)

    def _read(self, addr):
        outputs = []
        # wire up all the read addresses and collect the outputs
        for mem in self.cols:
            mem.RADDR @= addr
            outputs.append(mem.RDATA)

        shift = None
        rdata = None

        for i in range(self.num_v_cols):
            if shift is None:
                shift = self.mask[i]
            else:
                shift |= self.mask[i]

            data = shift.ite(outputs[i + 1], outputs[i])

            if rdata is None:
                rdata = data
            else:
                rdata = rdata.concat(data)

        assert isinstance(rdata, m.Bits[self.data_width])
        return rdata

    def _write(self, addr, data):
        inputs = [
            data[i * self.col_width:(i + 1) * self.col_width]
            for i in range(self.num_v_cols)
        ]

        assert all(isinstance(x, m.Bits[self.col_width]) for x in inputs)

        # wire up the WE / addr
        for mem in self.cols:
            mem.WADDR @= addr
            mem.WE @= self.we

        shift = None
        for i, mem in enumerate(self.cols):
            if shift is None:
                shift = self.mask[i]
            elif i < self.num_v_cols:
                shift |= self.mask[i]

            # this logic isn't strictly necessary
            if i < self.num_v_cols:
                mem.WE @= self.we & ~self.mask[i]
            else:
                mem.WE @= self.we & shift

            # each input is either fed to the current column or the next
            # so each column gets its input either from current input or
            # the previous
            if i == 0:
                # there is no "previous"
                mem.WDATA @= inputs[i]
            elif i < self.num_v_cols:
                mem.WDATA @= shift.ite(inputs[i - 1], inputs[i])
            else:
                # there is no "current"
                mem.WDATA @= inputs[i - 1]


class SRAMModalMixin:

    class State(m.Enum):
        Normal = 0
        Retention = 1
        TotalRetention = 2
        DeepSleep = 3

    def _init_attrs(self, addr_width: int, data_width: int,
                    has_byte_enable: bool, debug: bool, *args, **kwargs):
        super()._init_attrs(addr_width, data_width, has_byte_enable, debug,
                            *args, **kwargs)

        self.debug = debug

    def _init_io(self):
        super()._init_io()
        self.io += m.IO(
            deep_sleep=m.In(m.Bit),
            power_gate=m.In(m.Bit),
            wake_ack=m.Out(m.Bit),
        )
        if self.debug:
            self.io += m.IO(current_state=m.Out(type(self).State), )

    @property
    def _current_state(self):
        return type(self).State([self.io.deep_sleep, self.io.power_gate])

    @property
    def _in_normal(self):
        return self._current_state == type(self).State.Normal

    @property
    def ce(self):
        return super().ce & self._in_normal & self.boot_reg.O

    def _instance_subcomponents(self):
        super()._instance_subcomponents()
        self.Q_reg = m.Register(
            T=m.Bits[self.data_width],
            has_enable=True,
        )()
        self.boot_reg = m.Register(init=m.Bit(0), )()

    def _connect(self):
        super()._connect()
        # Not sure if this correct
        # boot reg blocks enable for a cycle after we enter normal mode
        self.io.wake_ack @= self._in_normal
        self.boot_reg.I @= self._in_normal

        if self.debug:
            self.io.current_state @= self._current_state

    def _read(self, addr):
        self.Q_reg.I @= super()._read(addr)
        self.Q_reg.CE @= self.re
        return self.Q_reg.O


class SRAMDM(SRAMModalMixin, SRAMDouble):
    pass


class SRAMSM(SRAMModalMixin, SRAMSingle):
    pass


class SRAMDR(SRAMRedundancyMixin, SRAMDouble):
    pass


class SRAMSR(SRAMRedundancyMixin, SRAMSingle):
    pass


class SRAMSMR(SRAMModalMixin, SRAMRedundancyMixin, SRAMSingle):
    pass


class SRAMDMR(SRAMModalMixin, SRAMRedundancyMixin, SRAMDouble):
    pass


# Base -> Features -> Class
SRAM_FEATURE_TABLE = {
    SRAMSingle: {
        frozenset(): SRAMSingle,
        frozenset((SRAMModalMixin, )): SRAMSM,
        frozenset((SRAMRedundancyMixin, )): SRAMSR,
        frozenset((
            SRAMModalMixin,
            SRAMRedundancyMixin,
        )): SRAMSMR,
    },
    SRAMDouble: {
        frozenset(): SRAMDouble,
        frozenset((SRAMModalMixin, )): SRAMDM,
        frozenset((SRAMRedundancyMixin, )): SRAMDR,
        frozenset((
            SRAMModalMixin,
            SRAMRedundancyMixin,
        )): SRAMDMR,
    },
}


class SRAMStateful(SRAMDouble):

    class CMD(m.Enum):
        NOP = 0  # have a nop so that CMD actually has more than 1 cmd
        INIT = 1

    class State(m.Enum):
        SLEEP = 0
        BOOT = 1
        READY = 2

    def __init__(self,
                 addr_width: int,
                 data_width: int,
                 has_byte_enable: bool = False,
                 col_width: int = 4,
                 debug: bool = False,
                 *args,
                 **kwargs):

        super().__init__(addr_width, data_width, has_byte_enable, col_width,
                         debug, *args, **kwargs)

    def _init_attrs(self, addr_width: int, data_width: int,
                    has_byte_enable: bool, col_width: int, debug: bool, *args,
                    **kwargs):
        super()._init_attrs(addr_width, data_width, has_byte_enable, *args,
                            **kwargs)

        if col_width <= 0:
            raise ValueError()

        if data_width % col_width != 0:
            raise ValueError()

        self.col_width = col_width
        self.debug = debug

    def _init_io(self):
        super()._init_io()
        self.io += m.IO(cmd=m.In(type(self).CMD))
        if self.debug:
            self.io += m.IO(
                current_state=m.Out(type(self).State),
                mask=m.Out(m.Bits[self.num_cols]),
            )

    @property
    def ce(self):
        return super().ce & (self.state.O == type(self).State.READY)

    @property
    def num_cols(self):
        return self.data_width // self.col_width

    def _instance_subcomponents(self):
        self.cols = [
            m.Memory(1 << self.addr_width,
                     m.Bits[self.col_width],
                     read_latency=READ_LATENCY,
                     has_read_enable=False)()
            for _ in range(self.num_cols + 1)  # + 1 for redundancy
        ]
        self.state = m.Register(init=type(self).State.SLEEP)()
        self.mask_reg = m.Register(T=m.Bits[self.num_cols], has_enable=True)()

    def _connect(self):
        super()._connect()
        # set up some aliases
        State = type(self).State
        CMD = type(self).CMD
        state = self.state
        current_state = state.O

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
                    mask_en = m.Bit(1)
                else:
                    # cmd == CMD.NOP
                    next_state = State.BOOT
            else:
                # current_state == READY
                next_state = State.READY
            state.I @= next_state
            self.mask_reg.I @= mask_in
            self.mask_reg.CE @= mask_en

        if self.debug:
            self.io.current_state @= current_state
            self.io.mask @= self.mask_reg.O

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
                # mem.RE @= self.re & ~self.mask_reg.O[i]
            else:
                pass
                # redundancy column
                # mem.RE @= self.re & shift

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
                rdata = shift.ite(outputs[i + 1], outputs[i])
            else:
                rdata = rdata.concat(shift.ite(outputs[i + 1], outputs[i]))

        assert isinstance(rdata, m.Bits[self.data_width])

        return rdata

    def _write(self, addr, data):
        inputs = [
            data[i * self.col_width:(i + 1) * self.col_width]
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
                mem.WDATA @= shift.ite(inputs[i - 1], inputs[i])
            else:
                # there is no "current"
                mem.WDATA @= inputs[i - 1]
