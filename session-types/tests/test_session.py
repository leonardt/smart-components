import pytest

from magma_session import (Send, Receive, Choose, Offer, Dual, Epsilon, Rec,
                           Channel)


def test_dual():
    x = Send[int, Epsilon]
    assert repr(x) == "Send[<class 'int'>, Epsilon]"
    y = Receive[int, Epsilon]
    assert Dual(x) == y
    assert Dual(y) == x

    a = Choose[
        ("c", x),
        ("d", y)
    ]
    assert repr(a) == """\
Choose[
    ('c', Send[<class 'int'>, Epsilon])
    ('d', Receive[<class 'int'>, Epsilon])
]\
"""

    b = Offer[
        ("c", y),
        ("d", x)
    ]
    assert Dual(a) == b
    assert Dual(b) == a
    assert x != b

    m = Rec['foo', Send[int, "foo"]]
    assert m != b
    assert repr(m) == "Rec[\"foo\", Send[<class 'int'>, 'foo']]"
    assert Dual(m) == Rec['foo', Receive[int, "foo"]]

    chan = Channel[a]
    assert chan == Channel[Dual(b)]
    assert chan != a

    with pytest.raises(TypeError):
        Dual(int)
