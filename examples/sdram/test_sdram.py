import pytest
import fault
import magma as m
import hwtypes as hw
from main import InitMem

@pytest.mark.parametrize('init_sequece',
        [
            (
                m.generator.ParamDict(WE=hw.Bit(0), RE=hw.Bit(0)),
            ),
            (
                m.generator.ParamDict(WE=hw.Bit(1), RE=hw.Bit(1)),
            ),
            (
                m.generator.ParamDict(WE=hw.Bit(0), RE=hw.Bit(0)),
                m.generator.ParamDict(WE=hw.Bit(1), RE=hw.Bit(1)),
                m.generator.ParamDict(WE=hw.Bit(0), RE=hw.Bit(0)),
            ),
       ]
    )
def test_mem(init_sequece):
    TestMem = InitMem(
        16,
        m.Bits[32],
        1,
        init_sequece,
        True
    )

    State = TestMem.io.current_state

    assert hasattr(State, 'SLEEP')
    assert hasattr(State, 'READY')

    N = len(init_sequece)

    for i in range(1, N):
        assert hasattr(State, f'BOOT_{i}')

    tester = fault.Tester(TestMem, TestMem.CLK)

    tester.circuit.current_state.expect(State.SLEEP)
    tester.circuit.next_state.expect(State.SLEEP)


    def _set_signals(idx):
        for port, value in init_sequece[idx].items():
            setattr(tester.circuit, port, value)

    _set_signals(0)
    for i in range(1, N):
        tester.eval()
        expected = getattr(State, f'BOOT_{i}')
        tester.circuit.next_state.expect(
            expected,
            msg=(
                f'current_state: %x, next_state: %x, expected next_state {expected}',
                tester.circuit.current_state,
                tester.circuit.next_state,
            ),
        )
        tester.step(2)
        tester.circuit.current_state.expect(
            expected,
            msg=(
                f'current_state: %x, next_state: %x, expected current_state {expected}',
                tester.circuit.current_state,
                tester.circuit.next_state,
            ),
        )
        _set_signals(i)

    tester.print("Expecting ready... \n")
    expected = State.READY
    tester.eval()
    tester.circuit.next_state.expect(
        expected,
        msg=(
            f'current_state: %x, next_state: %x, expected next_state {expected}',
            tester.circuit.current_state,
            tester.circuit.next_state,
        ),
    )
    tester.step(2)
    tester.circuit.current_state.expect(
        expected,
        msg=(
            f'current_state: %x, next_state: %x, expected current_state {expected}',
            tester.circuit.current_state,
            tester.circuit.next_state,
        ),
    )
    tester.compile_and_run("verilator", flags=["-Wno-fatal"])

