from abc import abstractmethod
from collections.abc import Iterable
import typing as tp

import hwtypes as ht
import magma as m

# Morally these should all be metaclasses maybe using getitem syntax e.g.
#  Offer[{x: T, y: S}]
# but for now they are objects for agility.

# Iterate for children
class SessionT(Iterable):
    def __eq__(self, other):
        if isinstance(other, type(self)):
            if len(self) == len(other):
                return all(s == o for s,o in zip(self, other))
            return False
        else:
            return NotImplemented

    def __hash__(self):
        return sum(map(hash, self))

    def __ne__(self, other):
        eq = self == other
        if eq is NotImplemented:
            return NotImplemented
        return not eq

    @abstractmethod
    def __len__(self): pass


# Because of how magma enum's work
LabelT = ht.BitVector


class _WrapperL(SessionT):
    _t: m.Kind
    def __init__(self, T: m.Kind):
        self._t = T

    def __iter__(self):
        yield self._t

    def __len__(self):
        return 1

    def __repr__(self):
        return f'{type(self).__qualname__}({self._t})'


class _WrapperM(SessionT):
    _d: tp.Mapping[LabelT, SessionT]
    def __init__(self, d: tp.Mapping[LabelT, SessionT]):
        self._d = d

    def __iter__(self):
        yield from self._d.items()

    def __len__(self):
        return len(self._d)

    def __repr__(self):
        return f'{type(self).__qualname__}({self._d})'


# Not really necessary as Sequence is the only one but maybe later
# we add concurrent or similar 
class _WrapperS(SessionT):
    _s: tp.Sequence[tp.Union[LabelT, SessionT]]
    def __init__(self, *s: tp.Union[LabelT, SessionT]):
        self._s = s

    def __iter__(self):
        yield from self._s

    def __len__(self):
        return len(self._s)

    def __repr__(self):
        return f'{type(self).__qualname__}({", ".join(map(repr, self._s))})'


class Send(_WrapperL): pass


class Recieve(_WrapperL): pass


class Offer(_WrapperM): pass


class Choose(_WrapperM): pass


class Sequence(_WrapperS): pass


class SessionTypeVisitor:
    def visit(self, T: tp.Union[LabelT, SessionT]):
        method_name = f'visit_{type(T).__name__}'
        method = getattr(self, method_name, self.visit_label)
        method(T)

    def visit_leaf(self, T: m.Kind) ->  None:
        '''
        Method for visiting leaf magma types
        '''
        pass

    def visit_Sequence(self, T: Sequence) ->  None:
        for t in T:
            self.visit(t)

    # This leads to a kinda convoluted design pattern when one wants to only
    # visit leaf from one of send/receive.  Maybe get rid of visit_Leaf. 
    def visit_Send(self, T: Send) ->  None:
        self.visit_leaf(*T)

    def visit_Recieve(self, T: Recieve) ->  None:
        self.visit_leaf(*T)

    def visit_Offer(self, T: Offer) ->  None:
        for k, v in T:
            self.visit_Offer_item(k, v)

    def visit_Choose(self, T: Choose) ->  None:
        for k, v in T:
            self.visit_Choose_item(k, v)

    # maybe I am being to granulated here but it doesn't hurt anything
    def visit_Offer_item(self, k: LabelT, v: SessionT) ->  None:
        self.visit_Offer_label(k)
        self.visit(v)

    def visit_Choose_item(self, k: LabelT, v: SessionT) ->  None:
        self.visit_Choose_label(k)
        self.visit(v)

    def visit_Offer_label(self, k: LabelT) ->  None:
        self.visit_label(k)

    def visit_Choose_label(self, k: LabelT) ->  None:
        self.visit_label(k)

    def visit_label(self, k: LabelT) ->  None:
        pass


