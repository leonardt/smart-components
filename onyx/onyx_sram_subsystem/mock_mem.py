import operator as op

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
        self._init_attrs(
            addr_width, data_width, has_byte_enable, *args, **kwargs
        )
        self._init_io()
        self._instance_subcomponents()
        self._connect()

    def _init_attrs(
        self, addr_width: int, data_width: int, has_byte_enable: bool, *args,
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
            CEn=m.In(m.Enable),
            WDATA=m.In(T),
            WEn=m.In(m.Enable),
            RDATA=m.Out(T),
            REn=m.In(m.Enable),
        ) + m.ClockIO()

        if self.has_byte_enable:
            self.io += m.IO(WBEn=m.Bits[data_width / 8])

    def _instance_subcomponents(self):
        self.memory = m.Memory(
            1 << self.addr_width,
            m.Bits[self.data_width],
            read_latency=READ_LATENCY,
            has_read_enable=False
        )()

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


def _build_mux_tree(lst):
    # Takes a list of (predicate, data)
    # returns a mux tree equivelent to:
    #   if predicate[0]:
    #       return data[0]
    #   elif prdicate[1]:
    #       return data[1]
    #   ...
    #   else:
    #       return data[-1]
    n = len(lst)
    if n == 1:
        return lst[0][1]
    else:
        assert n >= 2
        top = lst[:n // 2]
        bot = lst[n // 2:]
        cond = _tree_reduce(op.or_, [pred for pred, _ in top])
        return cond.ite(_build_mux_tree(top), _build_mux_tree(bot))


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
        # All widths are number of bits
        # num_r_cols is number of redundancy columns
        super().__init__(
            addr_width, data_width, has_byte_enable, col_width, num_r_cols,
            debug, *args, **kwargs
        )

    def _init_attrs(
        self, addr_width: int, data_width: int, has_byte_enable: bool,
        col_width: int, num_r_cols: int, debug: bool, *args, **kwargs
    ):
        super()._init_attrs(
            addr_width, data_width, has_byte_enable, debug, *args, **kwargs
        )

        if col_width <= 0:
            raise ValueError()

        if data_width % col_width != 0:
            raise ValueError()

        if num_r_cols > data_width // col_width:
            raise ValueError("More redundancy than virtual columns")

        self.col_width = col_width
        self.num_r_cols = num_r_cols
        self.debug = debug
        self.redundancy_addr_t = m.Bits[m.bitutils.clog2safe(self.num_v_cols)]

    @property
    def num_v_cols(self):
        # Number of virtual columns
        return self.data_width // self.col_width

    @property
    def num_p_cols(self):
        # Number of physical columns
        return self.num_v_cols + self.num_r_cols

    def _init_io(self):
        super()._init_io()
        self.io += m.IO(
            RCE=m.In(m.Bits[self.num_r_cols]),
            **{
                f'RCF{i}A':
                m.In(self.redundancy_addr_t)
                for i in range(self.num_r_cols)
            }
        )

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
            self.io.RCE[i].ite(
                _binary_to_unary(getattr(self.io, f'RCF{i}A')), zero
            ) for i in range(self.num_r_cols)
        ]

        self.mask = _tree_reduce(mask_t.bvor, RCFs)

    def _read(self, addr):
        outputs = []
        # wire up all the read addresses and collect the outputs
        for mem in self.cols:
            mem.RADDR @= addr
            outputs.append(mem.RDATA)

        # The following function is meant to build this pattern:
        #   shifts[k].ite(
        #       outputs[i+k+1],
        #       shifts[k-1].ite(
        #           outputs[i+k],
        #           shifts[k-2].ite(
        #               ...,
        #               shifts[0].ite(
        #                   outputs[i+1],
        #                   outputs[i]
        #               )
        #           )
        #       )
        #   )
        def build_ite(shifts, outputs, i):
            lst = [(True, outputs[i])]
            for idx, shift in enumerate(shifts):
                lst.append((shift, outputs[i + idx + 1]))
            lst.reverse()
            return _build_mux_tree(lst)

        shifts = [m.Bit(0) for _ in range(self.num_r_cols)]
        rdata = None

        for i in range(self.num_v_cols):
            prev = m.Bit(1)
            for idx in range(self.num_r_cols):
                shifts[idx] |= prev & self.mask[i]
                prev = shifts[idx]

            data = build_ite(shifts, outputs, i)

            if rdata is None:
                rdata = data
            else:
                rdata = rdata.concat(data)

        assert isinstance(rdata, m.Bits[self.data_width])
        return rdata

    def _write(self, addr, data):
        # break the inputs in chuncks
        inputs = [
            data[i * self.col_width:(i + 1) * self.col_width]
            for i in range(self.num_v_cols)
        ]

        assert all(isinstance(x, m.Bits[self.col_width]) for x in inputs)

        # The following function is meant to build this pattern:
        #   if i == 0:
        #       retun inputs[i]
        #   elif i == 1:
        #       return shifts[0].ite(inputs[i-1], inputs[i])
        #   elif i < self.num_v_cols:
        #       return shifts[1].ite(
        #           inputs[i-2],
        #           shifts[0].ite(inputs[i-1], inputs[i])
        #       )
        #   elif i == self.num_v_cols:
        #       return shifts[1].ite(inputs[i-2], inputs[i-1])
        #   else:
        #       return inputs[i-2]
        #
        # Not sure how to generalize it with ... above is for num_r_cols = 2
        # But basically there are 3 cases,
        #   i < num_r_cols:
        #       we select from the first i chuncks. Use first shift bits.
        #   i < num_v_cols:
        #       The "normal" case where the ith column consumes one preceding
        #       num_r_col+1 chunks. Use all the shift bits.
        #   i >= num_v_cols:
        #       The redundancy columns which must have a shift enabled to be
        #       relevant hence we use last shift bits.
        def build_ite(shits, inputs, i):
            max_inputs = len(shifts) + 1
            if i < self.num_r_cols:
                offsets = [k for k in range(i + 1)]
                assert len(offsets) < max_inputs
                shift_offset = 0
            elif i < self.num_v_cols:
                offsets = [k for k in range(self.num_r_cols + 1)]
                assert len(offsets) == max_inputs
                shift_offset = 0
            else:
                offsets = [
                    k for k in
                    range(i - self.num_v_cols + 1, self.num_r_cols + 1)
                ]
                assert len(offsets) < max_inputs
                shift_offset = max_inputs - len(offsets)

            lst = [(True, inputs[i - offsets[0]])]
            for idx, offset in enumerate(offsets[1:]):
                lst.append((shifts[idx + shift_offset], inputs[i - offset]))

            lst.reverse()
            return _build_mux_tree(lst)

        shifts = [m.Bit(0) for _ in range(self.num_r_cols)]
        for i, mem in enumerate(self.cols):
            # broadcast the addr
            mem.WADDR @= addr
            if i < self.num_v_cols:
                prev = m.Bit(1)
                for idx in range(self.num_r_cols):
                    shifts[idx] |= prev & self.mask[i]
                    prev = shifts[idx]

            # this logic isn't strictly necessary
            if i < self.num_v_cols:
                # only enable normal cols if they aren't masked
                mem.WE @= self.we & ~self.mask[i]
            else:
                # only enable redundancy cols if they are used
                mem.WE @= self.we & shifts[i - self.num_v_cols]

            mem.WDATA @= build_ite(shifts, inputs, i)


class SRAMModalMixin:
    class State(m.Enum):
        Normal = 0
        Retention = 1
        TotalRetention = 2
        DeepSleep = 3

    def _init_attrs(
        self, addr_width: int, data_width: int, has_byte_enable: bool,
        debug: bool, *args, **kwargs
    ):
        super()._init_attrs(
            addr_width, data_width, has_byte_enable, debug, *args, **kwargs
        )

        self.debug = debug

    def _init_io(self):
        super()._init_io()
        self.io += m.IO(
            deep_sleep=m.In(m.Bit),
            power_gate=m.In(m.Bit),
            wake_ack=m.Out(m.Bit),
        )
        if self.debug:
            self.io += m.IO(current_state=m.Out(type(self).State))

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


