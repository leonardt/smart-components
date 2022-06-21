import typing as tp

import magma as m

from session import Offer, Choose, Send, Recieve, Sequence
from session import SessionTypeVisitor, SessionT, LabelT

# could push all of these into one visitor but
# it gets a bit convoluted
class MaxBitVisitor(SessionTypeVisitor):
    def __init__(self):
        self.max_bits: int = 0

    def visit_leaf(self, T: m.Kind) ->  None:
        if isinstance(T, m.Bit):
            self.max_bits = max(self.max_bits, 1)
        elif isinstance(T, m.Bits):
            self.max_bits = max(self.max_bits, T.size)
        else:
            self.max_bits = max(self.max_bits, T.flat_length())


class MaxLabelVisitor(SessionTypeVisitor):
    def __init__(self):
        self.max_bits: int = 0

    def visit_label(self, label: LabelT) ->  None:
        self.max_bits = max(self.max_bits, label.size)


class MaxRecieveBitVisitor(MaxBitVisitor):
    def visit_Send(self, T: Send) ->  None:
        # prevent recursion
        pass


class MaxSendBitVisitor(MaxBitVisitor):
    def visit_Recieve(self, T: Send) ->  None:
        pass


class MaxOfferVisitor(MaxLabelVisitor):
    def visit_Choose_label(self, k: LabelT) ->  None:
        pass


class MaxChooseVisitor(MaxLabelVisitor):
    def visit_Offer_label(self, k: LabelT) ->  None:
        pass


class AlwaysTransitionsVisitor(SessionTypeVisitor):
    def __init__(self):
        self.always_transitions = False

    def visit_Sequence(self, T: Sequence):
        self.always_transitions = False
        # if any element in a sequence always transitions then we do
        for t in T:
            v = type(self)()
            v.visit(t)
            self.always_transitions |= v.always_transitions

    def _visit_branch(self, T: tp.Union[Offer, Choose]):
        # if all branches of an offer transition then we do
        at = None
        for k, t in T:
            if at is None:
                # the type is not empty 
                at = True

            v = type(self)()
            v.visit(t)
            at &= v.always_transitions

        if at is None:
            # the type is empty we do not transition
            at = False

        self.always_transitions = at


    def visit_Offer(self, T: Offer) ->  None:
        self._visit_branch(T)

    def visit_Choose(self, T: Choose) ->  None:
        self._visit_branch(T)

    def visit_leaf(self, T: m.Kind) ->  None:
        self.always_transitions = False

    def visit_label(self, k: LabelT) ->  None:
        self.always_transitions = True



class LongestPathVisitor(SessionTypeVisitor):
    ''' Finds the longest path in a type '''
    def __init__(self):
        self.len: int = 0

    def visit_leaf(self, T: m.Kind):
        self.len += 1


    def _visit_d(self, T: tp.Union[Offer, Choose]) -> None:
        max_len = 0
        for k, v in T:
            visitor = type(self)()
            visitor.visit(v)
            max_len = max(max_len, visitor.len)
        self.len += max_len


    def visit_Offer(self, T: Offer) ->  None:
        self._visit_d(T)


    def visit_Choose(self, T: Choose) -> None:
        self._visit_d(T)
