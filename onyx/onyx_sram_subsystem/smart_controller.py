from collections import defaultdict
import itertools as it
import functools as ft
import typing as tp

import magma as m
import hwtypes as ht

from mock_mem import SRAMDMR
from session import Offer, Choose, Send, Recieve, Sequence
from session import SessionTypeVisitor, SessionT, LabelT
from util import inverse_look_up, BiMap
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


class SessionTypeGenerator:
    def __init__(self,
            initial_label: LabelT,
            declared_types: tp.Mapping[LabelT, SessionT]):
        self._labels: tp.Mapping[LabelT, tp.Callable[[], None]] = {}
        # because I cant do all in one line with annotated assignment
        labels = self._labels
        for cls in type(self).mro():
            for name, attr in cls.__dict__.items():
                l = getattr(attr, '_marked_', None)
                if l is not None:
                    assert l not in labels
                    labels[l] = getattr(self, name)

        assert initial_label in labels, (initial_label, labels)
        assert labels.keys() == declared_types.keys()
        self._next_idx = it.count()
        # after a branch we are in many possible states
        self._curr_state = set()
        self._curr_cmd = None
        self._label_to_state = {
                l : i for l,i in zip(labels, self._next_idx)
        }
        self._next_states = defaultdict(set)

        self._declared_types: tp.Mapping[LabelT, SessionT] = declared_types

        self._inferred_types: tp.Mapping[LabelT, SessionT] = {
            l : self._elaborate_label(l) for l in labels
        }
        if self._inferred_types.keys() != declared_types.keys():
            raise TypeError()

        for l, t in self._inferred_types.items():
            if t != declared_types[l]:
                raise TypeError(f'Declared type for {l} ({t}) does not match inferred type {declared_types[l]}')

    def offer(self,
            cmd_to_function: tp.Mapping[LabelT, tp.Callable],
            ):
        idx = self._add_state(Offer, cmd_to_function)

    def choose(self, choice, cmd_to_function):
        idx = self._add_state(Choose, cmd_to_function)
        print(idx, self._next_states[idx])

    def send(self, data):
        idx = self._add_state(Send(type(data)))
        print('s', idx, self._next_states[idx])

    def recieve(self, data_t):
        idx = self._add_state(Recieve(data_t))
        print('r', idx, self._next_states[idx])
        return # sliced data_t

    def transition(self, label):
        self._add_state(label)


    def _set_next_state(self, next_state):
        for s in self._curr_state:
            self._next_states[s].add((next_state, self._curr_cmd))

    def _add_state(self, T, cmd_to_function=None):
        state = self._curr_state
        if cmd_to_function is None:
            assert isinstance(T, (Send, Recieve, LabelT)), T
            if isinstance(T, LabelT):
                self._set_next_state(self._label_to_state[T])
                self._curr_state = set()
                idx = None
            else:
                idx = next(self._next_idx)
                self._set_next_state(idx)
                self._curr_state = {idx}
            self._current_type.append(T)
            self._curr_cmd = None # we dont need a command to transition
        elif issubclass(T, Offer):
            d = {}
            idx = next(self._next_idx)
            self._set_next_state(idx)
            end_states = set()
            for cmd, function in cmd_to_function.items():
                self._curr_state = {idx}
                d[cmd] = self._elaborate_branch(cmd, function)
                end_states |= self._curr_state
            self._curr_state = end_states
            self._current_type.append(Offer(d))
        else:
            assert issubclass(T, Choose)
            d = {}
            idx = next(self._next_idx)
            self._set_next_state(idx)
            end_states = set()
            for cmd, function in cmd_to_function.items():
                self._curr_state = {idx}
                d[cmd] = self._elaborate_branch(cmd, function)
                end_states |= self._curr_state
            self._curr_state = end_states
            self._current_type.append(Choose(d))
        return idx

    def _elaborate_label(self, l: LabelT) -> SessionT:
        self._curr_state = {self._label_to_state[l]}
        self._current_type = []
        method = self._labels[l]
        method()
        return Sequence(*self._current_type)

    def _elaborate_branch(self, cmd, function) -> SessionT:
        # I dont know if saving this is needed
        old_cmd = self._curr_cmd
        # this one definitely needs to be saved
        old_t = self._current_type

        self._curr_cmd = cmd
        self._current_type = []
        function()
        branch_t = Sequence(*self._current_type)

        self._curr_cmd = old_cmd
        self._current_type = old_t

        return branch_t

def mark(t):
    def add_mark(fn):
        setattr(fn, '_marked_', t)
        return fn
    return add_mark

class Controller(SessionTypeGenerator):
    def __init__(self):
        super().__init__(
                MemStates.MemInit,
                LABEL_TO_T,
            )

    @mark(MemStates.MemInit)
    def MemInitT(self):
        self.redundancy = self.recieve(RedundancyT)
        self.transition(MemStates.MemOff)

    @mark(MemStates.MemOff)
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

    @mark(MemStates.MemOn)
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
