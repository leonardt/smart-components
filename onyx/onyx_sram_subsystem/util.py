import functools as ft
import typing as tp
import sys

# PEP 585
if sys.version_info < (3, 9):
    from typing import MutableMapping, Mapping, MutableSet, AbstractSet as Set, Iterator, Iterable
    from typing import MappingView, ItemsView, KeysView, ValuesView
else:
    from collections.abc import MutableMapping, Mapping, MutableSet, Set, Iterator, Iterable
    from collections.abc import MappingView, ItemsView, KeysView, ValuesView


T = tp.TypeVar('T')
S = tp.TypeVar('S')


def inverse_look_up(d: Mapping[T, S], v: S) -> T:
    for k_, v_ in d.items():
        if v_ == v:
            return k_
    raise KeyError()

# I really need a make a repo for this recipe I use it all the time.
# Because the setitem signature does not match mutable mapping 
# we inherit from mapping. We lose MutableMapping mixin methods
# for correct typing but we don't use them anyway 
class BiMap(Mapping[T, Set[S]]):
    _d: MutableMapping[T, MutableSet[S]]
    _r: MutableMapping[S, MutableSet[T]]

    def __init__(self, d: tp.Optional['BiMap[T, S]'] = None) -> None:
        self._d = {}
        self._r = {}
        if d is not None:
            for k, v in d.items():
                for vv in v:
                    self[k] = vv

    def __getitem__(self, idx: T) -> Set[S]:
        return frozenset(self._d[idx])

    def __setitem__(self, idx: T, val: S) -> None:
        self._d.setdefault(idx, set()).add(val)
        self._r.setdefault(val, set()).add(idx)

    def __delitem__(self, idx: T) -> None:
        for val in self._d[idx]:
            self._r[val].remove(idx)
            if not self._r[val]:
                del self._r[val]
        del self._d[idx]

    def __iter__(self) -> Iterator[T]:
        return iter(self._d)

    def __len__(self) -> int:
        return len(self._d)

    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return self._d == other._d
        else:
            return NotImplemented

    def __ne__(self, other) -> bool:
        return (eq := self == other) if eq is NotImplemented else not eq

    @property
    def i(self) -> 'BiMap[S, T]':
        i: BiMap[S, T] = BiMap()
        i._d = self._r
        i._r = self._d
        return i

    def __repr__(self) -> str:
        kv = map(': '.join, (map(repr, items) for items in self.items()))
        return f'{type(self).__name__}(' + ', '.join(kv) + ')'
