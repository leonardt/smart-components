import magma as m
import hwtypes as ht
from mock_mem import SRAMDMR
from session import Offer, Choose, Send, Recieve, Sequence
from session import SessionTypeVisitor, SessionT, LabelT
from util import inverse_look_up, BiMap

class CoopGenerator(m.Generator2):
    def __init__(self, **kwargs):
        self._decl_attrs(**kwargs)
        self._decl_io(**kwargs)
        self._decl_components(**kwargs)
        self._connect(**kwargs)

    def _decl_attrs(self, **kwargs): pass

    def _decl_io(self, **kwargs):
        self.io = m.IO()

    def _decl_components(self, **kwargs): pass
    def _connect(self, **kwargs): pass

class StateMachine(CoopGenerator):
    def _decl_attrs(self, **kwargs):
        super()._decl_attrs(**kwargs)
        self.num_states = 4

    def _decl_io(self, **kwargs):
        super()._decl_io(**kwargs)
        self.io += m.IO(
            receive=m.In(m.Bits[16]),
            offer=m.In(m.Bits[4]),
            send=m.Out(m.Bits[16]),
            current_state=m.Out(m.Bits[2]),
        )

    def _decl_components(self, **kwargs):
        super()._decl_components(**kwargs)
        self.state_reg = m.Register(
            init=m.Bits[2](0),
            has_enable=False,
        )()

        self.s_reg = m.Register(
            T=m.Bits[16],
            has_enable=True,
        )()

        self.r_reg = m.Register(
            T=m.Bits[16],
            has_enable=True,
        )()

        self.o_reg = m.Register(
            T=m.Bits[4],
            has_enable=True,
        )()

    def _connect(self, **kwargs):
        super()._connect(**kwargs)
        self.io.current_state @= self.state_reg.O
        self.r_reg.I @= self.io.receive
        self.o_reg.I @= self.io.offer
        self.io.send @= self.s_reg.O
        
        MemInit = 0
        MemOff = 1
        MemOn = 3
        Send = 2

        # State MemInit
        # Enable receive register 'r_reg'
        # GOTO MemOff

        # State MemOff
        # Enable offer/cmd reg 'o_reg'
        # If cmd == poweroff => GOTO MemOff
        # if cmd == poweron  => GOTO Send

        # State Send
        # Enable send reg 's_reg'
        # send wakeAckT
        # GOTO MemOn

        # State MemOn
        # Enable offer/cmd reg 'o_reg'
        # if cmd == poweroff => goto memoff
        # if cmd == poweron => stay in state 2 (memon)

        # Enable registers only where needed

        # Enable r_reg for state MemInit
        self.r_reg.CE @= (cur_state == MemInit)

        # Enable s_reg for state Send
        self.s_reg.CE @= (cur_state == Send)

        # Enable o_reg for states MemOff, MemOn
        self.o_reg.CE @= ((cur_state == MemOff) | (cur_state == MemOn))

        # state update functions
        # if state == MemInit: state = MemOff
        # if cur_state == MemInit: cur_state = MemOff
        # if cur_state == 0: cur_state = 1

        cur_state = self.state_reg.O
        cmd = self.o_reg.O
        rcv = self.r_reg.O

        @m.inline_combinational()
        def controller():
            if cur_state == MemInit:
                # FIXME
                if receive_redundancy: next_state = MemOff

            elif cur_state == MemOff:
                if   cmd == PowerOff:  next_state = MemOff
                elif cmd == PowerOn:   next_state = Send

            elif cur_state == Send:
                send_WakeAckT;         next_state = MemOn

            elif cur_state == MemOn:
                if   cmd == PowerOff:  next_state = MemOff
                elif cmd == PowerOn:   next_state = MemOn

            self.state_reg.I @= next_state

        def receive_redundancy():
            # WRITEME
            # ?? return (rcv == RedundancyT)
            return True

        def send_wakeAckT():
            # WRITEME
            return True


##############################################################################
        def controller_alt():
            next_state = state_machine([
                MemInit, receive_redundancy,  MemOff,

                MemOff, cmd == PowerOff,      MemOff,
                MemOff, cmd == PowerOn,       Send  ,

                Send,   cmd == send_wakeAckT, MemOn ,

                MemOn,  cmd == PowerOff,      MemOff,
                MemOn,  cmd == PowerOn,       MemOn ,
            ])
            self.state_reg.I @= next_state



        def state_machine (smlist):
            # assert n_elements%3 == 0?
            while smlist:
                state1 = smlist.pop(0); # assert type int?
                action = smlist.pop(0); # assert type bool or func?
                state2 = smlist.pop(0); # assert type int?
                if cur_state == state1:
                    # DO NOT eval action unless we are in appropriate state!
                    if type(action) != bool: action = action()
                    if action:
                        return state2

            # ERROR? ASSERT?
            return state1
##############################################################################


def test():
    sm = StateMachine()
    print("foo ehlloo foozzz")
    print(sm.num_states)
    print("bar byebye baxzzzz")

test()
