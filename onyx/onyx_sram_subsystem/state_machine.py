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
            recieve=m.In(m.Bits[16]),
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
        
        # State 0 (MemInit) => enable receive register r_reg and transition to
        # state 1 (MemOff)

        # State 1 (MemOff)
        # Enable cmd reg (offer) (o_reg)
        # If cmd == poweroff stay in memoff;
        # if cmd == poweron => state 2 (send)

        # State 2 (Send)
        # send wakeAckT == enable s_reg (send register)
        # transition to state 3 (memOn)

        # State 3 (MemOn)
        # Enable o_reg (offer/cmd)
        # if cmd == poweroff => goto memoff
        # if cmd == poweron => stay in state 3 (memon)

        # Enable function for the o_reg
        # if state==1 or state==3 then enable cmd reg
        curstate = self.state_reg.O
        self.o_reg.CE @= ((curstate == 1) | (curstate == 3))

        # Enable function for the r_reg
        # if state==0 then enable r_reg
        self.r_reg.CE @= (curstate == 0)

        # Enable function for the s_reg
        # if state==2 then enable s_reg
        self.s_reg.CE @= (curstate == 2)
        
        # state update functions
        # if state == MemInit: state = MemOff
        # if curstate == MemInit: curstate = MemOff
        if curstate == 0: curstate = 1

        
