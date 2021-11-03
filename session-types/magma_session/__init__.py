class SessionTypeMeta(type):
    def __getitem__(cls, key):
        return cls(*key)

    def __repr__(cls):
        return cls.__name__


class SessionType(metaclass=SessionTypeMeta):
    pass


class Epsilon(SessionType):
    pass


class SessionTypeWithData(SessionType):
    def __init__(self, data_type, next):
        self.data_type = data_type
        self.next = next

    def __repr__(self):
        name_str = type(self).__name__
        return f"{name_str}[{repr(self.data_type)}, {repr(self.next)}]"

    def __eq__(self, other):
        if not isinstance(other, SessionTypeWithData):
            return NotImplemented
        return (type(self) == type(other) and self.data_type == other.data_type
                and self.next == other.next)


class Receive(SessionTypeWithData):
    pass


class Send(SessionTypeWithData):
    pass


class SessionTypeWithBranches(SessionType):
    def __init__(self, *branches):
        self.branches = branches

    def __repr__(self):
        branches = ["\n    ".join(x for x in repr(y).splitlines())
                    for y in self.branches]
        branches = "\n    ".join(branches)
        return f"{type(self).__name__}[\n    {branches}\n]"

    def __eq__(self, other):
        if not isinstance(other, SessionTypeWithBranches):
            return NotImplemented
        return (type(self) == type(other) and
                all(x == y for x, y in zip(self.branches, other.branches)))


class Offer(SessionTypeWithBranches):
    pass


class Choose(SessionTypeWithBranches):
    pass


# TODO: Should this be parametrized like types or a function
# i.e. we could do either
#   * Dual(T), or
#   * Dual[T]
def Dual(T):
    if isinstance(T, Offer):
        return Choose(*((x[0], Dual(x[1])) for x in T.branches))
    if isinstance(T, Choose):
        return Offer(*((x[0], Dual(x[1])) for x in T.branches))
    if isinstance(T, Send):
        return Receive(T.data_type, Dual(T.next))
    if isinstance(T, Receive):
        return Send(T.data_type, Dual(T.next))
    if T is Epsilon:
        return T
    if isinstance(T, Rec):
        return Rec(T.name, Dual(T.T))
    if isinstance(T, str):
        return T
    raise TypeError(f"Unsupport type {T}")


# TODO: Should this be parametrizxed like types or a function?
#   * Rec(name, T), or
#   * Rec[name, T]
# TODO: What's the most elegant syntax to forward declare the "name" for the
# recursion?
#   e.g. we could use a lambda based syntax:
#       lambda name: Send[UInt, Receive[UInt, name]]
#   but we'd probably want to normalize it into a more standard data structure
#   for inspecting the type (e.g. something like this object)
class Rec(SessionType):
    def __init__(self, name, T):
        self.name = name
        self.T = T

    def __repr__(self):
        return f"Rec[\"{self.name}\", {self.T}]"

    def __eq__(self, other):
        if not isinstance(other, Rec):
            return NotImplemented
        return self.name == other.name and self.T == other.T


class ChannelMeta(type):
    def __getitem__(cls, T):
        return cls(T)


class Channel(metaclass=ChannelMeta):
    def __init__(self, T):
        self.T = T

    def __eq__(self, other):
        if not isinstance(other, Channel):
            return NotImplemented
        return self.T == other.T
