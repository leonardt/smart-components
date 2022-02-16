import functools as ft

import magma as m



class InitMem(m.Generator2):
    def __init__(self,
            height,
            T,
            read_latency,
            init_sequence,
            debug=False,
            ):

        addr_width = m.bitutils.clog2(height)
        self.io = m.IO(
            RADDR=m.In(m.Bits[addr_width]),
            RDATA=m.Out(T),
            WADDR=m.In(m.Bits[addr_width]),
            WDATA=m.In(T),
            WE=m.In(m.Enable),
            RE=m.In(m.Enable),
        ) + m.ClockIO()

        if not init_sequence:
            raise ValueError('init_sequence must not be empty')

        N = len(init_sequence)

        class State(m.Enum):
            SLEEP = 0
            for i in range(1, N):
                exec(f'BOOT_{i} = {i}')
                del i
            READY = N

        state_reg = m.Register(init=State.SLEEP)()

        if debug:
            self.io += m.IO(current_state=m.Out(State))
            self.io += m.IO(next_state=m.Out(State))
            self.io.current_state @= state_reg.O


        memory = m.Memory(height, T,
                read_latency=read_latency,
                has_read_enable=True)()

        is_ready = state_reg.O == State.READY

        re = m.bit(self.io.RE) & is_ready
        we = m.bit(self.io.WE) & is_ready

        memory.RE @= m.enable(re)
        memory.WE @= m.enable(we)

        memory.RADDR @= self.io.RADDR
        memory.WADDR @= self.io.WADDR
        memory.WDATA @= self.io.WDATA
        self.io.RDATA @= memory.RDATA

        def _test_state(idx):
            tests = []

            for port, value in init_sequence[idx].items():
                tests.append(getattr(self.io, port) == value)

            return ft.reduce(m.Bit.__and__, tests, m.Bit(1))

        def _build_state_mux(idx):
            if idx == N:
                # Once ready always ready
                return State.READY

            return (state_reg.O == idx).ite(
                _test_state(idx).ite(
                    State(idx+1), # Advance to next state
                    State.SLEEP # init sequence failed go back to SLEEP
                ),
                _build_state_mux(idx+1)
            )

        next_state = _build_state_mux(0)

        state_reg.I @= next_state

        if debug:
            self.io.next_state @= next_state
