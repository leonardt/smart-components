import functools as ft
import typing as tp

import magma as m
import hwtypes as ht

from mock_mem import SRAMDMR
from session import Offer, Choose, Send, Recieve, Sequence
from session import SessionTypeVisitor, SessionT, LabelT
from util import inverse_look_up
from visitors import MaxRecieveBitVisitor, MaxSendBitVisitor
from visitors import MaxOfferVisitor, MaxChooseVisitor
from visitors import LongestPathVisitor


AddrT = m.Bits[8]
DataT = m.Bits[16]

MemT = SRAMDMR(AddrT.size, DataT.size, num_r_cols=1)
RedundancyT = MemT.redundancy_addr_t

WakeAckT = m.Bit

CmdT = ht.BitVector


# because of issues with forward decls I declare all the type and their
# commands as enums. Maybe there is a better way to do this.
# Note: strings are NOT better imo.
class MemStates(m.Enum):
    MemInit = 0
    MemOff = 1
    MemOn = 2


class MemOffCmds(m.Enum):
    POWER_OFF = 0
    POWER_ON = 1


class MemOnCmds(m.Enum):
    POWER_OFF = 0
    IDLE = 1
    READ = 2
    WRITE = 3


MemInitT = Sequence(
    Recieve(RedundancyT),
    MemStates.MemOff,
)



MemOffT = Sequence(Offer({
    MemOffCmds.POWER_OFF : Sequence(MemStates.MemOff,),
    MemOffCmds.POWER_ON : Sequence(
        Send(WakeAckT),
        MemStates.MemOn,
    ),
}))


MemOnT = Sequence(Offer({
    MemOnCmds.POWER_OFF: Sequence(MemStates.MemOff,),
    MemOnCmds.IDLE : Sequence(MemStates.MemOn,),
    MemOnCmds.READ : Sequence(
        Recieve(AddrT),
        Send(DataT),
        MemStates.MemOn,
    ),
    MemOnCmds.WRITE : Sequence(
        Recieve(m.Tuple[AddrT, DataT]),
        MemStates.MemOn,
    ),
}))


# Mapping state enums members to their actual type
LABEL_TO_T = {
    MemStates.MemInit : MemInitT,
    MemStates.MemOff : MemOffT,
    MemStates.MemOn : MemOnT,
}


# similar
LABEL_TO_CMDS = {
    MemStates.MemInit : None,
    MemStates.MemOff : MemOffCmds,
    MemStates.MemOn : MemOnCmds,
}




'''
For right now I am going to assume that session types
come from the following grammar:
    session_t := Sequence( sequence_args )
    sequence_args := send , sequence_args
                   | receive , sequence_args
                   | offer
                   | choose
                   | label
    send := Send( DATA_T )
    receive := Receive( DATA_T )
    offer := Offer({ branch_args })
    choose := Choose({ branch_args })
    branch_args := branch_arg
                 | branch_arg , branch_args
    branch_arg := CMD : ( branch_seq ) ,
    branch_seq := send , branch_seq
                | receive ,  branch_seq
                | label
    label := LabelValue

Basically I expect every type to be a sequence of send / receives
terminated by an Offer, Choose, or Label
Further every option in a Offer / Choose shoud be a sequence of send or
receive terminated by a label
Note that this requires the type be non terminating.
Aditionally note that any non terminating type can be
transformed into this form.
First consider a type:
    S = Sequence(head, Offer({..., cmd_label: Sequence(cmd_body)}), tail)
Assume head and cmd_body contain only send / recieves and no transition.
This would violate the above grammar in two ways.  cmd_body isn't terminated by
a transition and S is not terminated by its offer.
we can rewrite this as:
    S = Sequence(..., Offer({..., cmd: Sequence(cmd_body, S')}))
    S' = Sequence(tail)
This normal form makes tracking state simpler
would be even simpler if each branch could only contain a label
'''
class SessionTypeGenerator:
    def __init__(self, label_to_type, initial_state, **types):
        self._label_to_type = label_to_type
        self._elaborated_types = {
            type_name: self._elaborate_top(type_name, t)
            for type_name, t in types.items()
        }
        # state variables:
        #   current_type :: macro level state
        #   sequence_index :: position top level sequence
        #   choice_index :: which choice we are currently taking
        #   in_branch :: bool (note each type has at most one branch)

    def offer(self,
            cmd_to_function: tp.Mapping[LabelT, tp.Callable],
            ):
        self._log(Offer, cmd_to_function)
        # if current_type and sequence index equal current elaborated state:
        #     sequence_index = 0
        #     in_branch = True
        # Note by construction we know that:
        #   in_branch = False and choice_index = 0
        # offerings = {cmd: f() for cmd, f in cmd_to_function.items()}

    def choose(self, choice, cmd_to_function):
        self._log(Choose, cmd_to_function)
        # if current_type and sequence index equal current elaborated state:
        #     sequence_index = 0
        #     in_branch = True
        #     choice_index = choice


    def send(self, data):
        self._log(Send(type(data)))
        # extends the send mux
        # if all state variable are in current elaborate state:
        #     send mux should select data padded to correct size
        #     if other side is ready:
        #         sequence_index += 1

    def recieve(self, data_t):
        self._log(Recieve(data_t))
        # slice the receive port for the correct data type
        # if all state variable are in current elaborate state:
        #     if data is valid:
        #         sequence_index += 1
        return # sliced data_t

    def transition(self, label):
        self._log(label)
        # extend the next_state mux
        # if all state variable are in current elaborate state then
        #     current_type = label
        #     sequence_index = 0
        #     choice_index = 0
        #     in_branch = False


    def _log(self, T, cmd_to_function=None):
        if cmd_to_function is None:
            assert isinstance(T, (Send, Recieve, LabelT)), T
            self._current_type.append(T)
            self._elaborated_i += 1
        elif issubclass(T, Offer):
            d = {}
            for cmd, function in cmd_to_function.items():
                d[cmd] = self._elaborate_branch(cmd, function)
            self._current_type.append(Offer(d))
        else:
            assert issubclass(T, Choose)
            d = {}
            for cmd, function in cmd_to_function.items():
                d[cmd] = self._elaborate_branch(cmd, function)
            self._current_type.append(Choose(d))
            self._elaborated_i += 1


    def _elaborate_top(self, type_name: str, t: SessionT) -> SessionT:
        # elaborated state
        self._current_type = []
        self._elaborated_t = inverse_look_up(self._label_to_type, t)
        self._elaborated_i = 0
        self._elaborated_c = 0
        self._elaborated_b = False
        method = getattr(self, type_name)
        method()
        return Sequence(*self._current_type)


    def _elaborate_branch(self, cmd, function) -> SessionT:
        self._elaborated_i = 0
        self._elaborated_c = cmd
        self._elaborated_b = True
        state = self._current_type
        self._current_type = []
        function()
        rval = self._current_type
        self._current_type = state
        return Sequence(*rval)



class Controller(SessionTypeGenerator):
    def __init__(self):
        super().__init__(
                LABEL_TO_T,
                MemStates.MemInit,
                MemInitT=MemInitT,
                MemOffT=MemOffT,
                MemOnT=MemOnT,
            )

    def MemInitT(self):
        self.redundancy = self.recieve(RedundancyT)
        self.transition(MemStates.MemOff)

    def MemOffT(self):
        def power_off():
            self.transition(MemStates.MemOff)

        def power_on():
            self.send(WakeAckT(1))
            self.transition(MemStates.MemOn)

        self.offer({
            MemOffCmds.POWER_OFF: power_off,
            MemOffCmds.POWER_ON: power_on,
        })

    def MemOnT(self):
        def power_off():
            self.transition(MemStates.MemOff)

        def idle():
            self.transition(MemStates.MemOn)

        def read():
            addr = self.recieve(AddrT)
            # wire up addr and read data
            data = DataT(0)
            self.send(data)
            self.transition(MemStates.MemOn)

        def write():
            addr_data = self.recieve(m.Tuple[AddrT, DataT])
            # wire up addr / data
            self.transition(MemStates.MemOn)

        self.offer({
            MemOnCmds.POWER_OFF: power_off,
            MemOnCmds.IDLE : idle,
            MemOnCmds.READ : read,
            MemOnCmds.WRITE : write,
        })


#class Controller(m.Generator2):
#    def __init__(self, label_to_type, label_to_cmds, **kwargs):
#        super().__init__(label_to_type, label_to_cmds, **kwargs)
#
#
#    def _decl_attrs(self,
#            label_to_type,
#            label_to_cmds,
#            ):
#        v = MaxRecieveBitVisitor()
#        # put in a Sequence to visit all in one shot
#        v.visit(Sequence(*STATE_TO_T.values()))
#        r_bits = v.max_bits
#
#        assert r_bits == AddrT.size + DataT.size
#        assert r_bits == m.Tuple[AddrT, DataT].flat_length()
#
#        v = MaxSendBitVisitor()
#        v.visit(Sequence(*STATE_TO_T.values()))
#        s_bits = v.max_bits
#
#
#        v = MaxOfferVisitor()
#        v.visit(Sequence(*STATE_TO_T.values()))
#        o_bits = v.max_bits
#
#        v = MaxChooseVisitor()
#        v.visit(Sequence(*STATE_TO_T.values()))
#        c_bits = v.max_bits
#
#        # All this should probably be ready valid or something
#        if r_bits > 0:
#            io += m.IO(
#                recieve=m.In(m.Bits[r_bits])
#            )
#        if s_bits > 0:
#            io += m.IO(
#                send=m.Out(m.Bits[s_bits])
#            )
#        if o_bits > 0:
#            io += m.IO(
#                offer=m.In(m.Bits[o_bits])
#            )
#        if c_bits > 0:
#            io += m.IO(
#                choose=m.Out(m.Bits[c_bits])
#            )
#
#    
