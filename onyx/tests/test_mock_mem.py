import itertools as it

import pytest
import fault
import hwtypes as hw
import magma as m

from onyx_sram_subsystem.mock_mem import SRAMSingle
from onyx_sram_subsystem.mock_mem import SRAMDouble
from onyx_sram_subsystem.mock_mem import SRAMStateful
from onyx_sram_subsystem.mock_mem import SRAMRedundancyMixin
from onyx_sram_subsystem.mock_mem import SRAMModalMixin
from onyx_sram_subsystem.mock_mem import SRAM_FEATURE_TABLE

ADDR_WIDTH = 8
DATA_WIDTH = 8


@pytest.mark.parametrize('base', [SRAMSingle, SRAMDouble])
@pytest.mark.parametrize(
    'mixins, params', [
        ((), {}),
        ((SRAMModalMixin, ), {}),
        ((SRAMRedundancyMixin, ), {
            'num_r_cols': 1
        }),
        ((SRAMRedundancyMixin, ), {
            'num_r_cols': 2
        }),
        ((
            SRAMModalMixin,
            SRAMRedundancyMixin,
        ), {
            'num_r_cols': 1
        }),
        ((
            SRAMModalMixin,
            SRAMRedundancyMixin,
        ), {
            'num_r_cols': 2
        }),
    ]
)
def test_sram(base, mixins, params):
    generator = SRAM_FEATURE_TABLE[base][frozenset(mixins)]
    Definition = generator(ADDR_WIDTH, DATA_WIDTH, debug=True, **params)
    tester = fault.Tester(Definition, Definition.CLK)

    if SRAMModalMixin in mixins:
        State = Definition.State
        tester.circuit.deep_sleep = hw.Bit(1)
        tester.circuit.power_gate = hw.Bit(1)
        tester.eval()
        tester.circuit.current_state.expect(State.DeepSleep)
        tester.circuit.wake_ack.expect(hw.Bit(0))

        tester.circuit.deep_sleep = hw.Bit(0)
        tester.circuit.power_gate = hw.Bit(1)
        tester.eval()
        tester.circuit.current_state.expect(State.TotalRetention)
        tester.circuit.wake_ack.expect(hw.Bit(0))

        tester.circuit.deep_sleep = hw.Bit(1)
        tester.circuit.power_gate = hw.Bit(0)
        tester.eval()
        tester.circuit.current_state.expect(State.Retention)
        tester.circuit.wake_ack.expect(hw.Bit(0))

        tester.circuit.deep_sleep = hw.Bit(0)
        tester.circuit.power_gate = hw.Bit(0)
        tester.eval()
        tester.circuit.current_state.expect(State.Normal)
        tester.circuit.wake_ack.expect(hw.Bit(1))
        tester.step(2)
        tester.circuit.wake_ack.expect(hw.Bit(1))

    if SRAMRedundancyMixin in mixins:
        tester.circuit.RCE = hw.BitVector[params['num_r_cols']](-1)
        for i in range(params['num_r_cols']):
            setattr(
                tester.circuit, f'RCF{i}A',
                hw.BitVector[m.bitutils.clog2safe(Definition.num_v_cols)](i)
            )

    for i in range(1 << ADDR_WIDTH):
        tester.circuit.CEn = hw.Bit(0)
        tester.circuit.REn = hw.Bit(0)
        tester.circuit.WEn = hw.Bit(1)
        if base is SRAMSingle:
            tester.circuit.ADDR = hw.BitVector[ADDR_WIDTH](i)
        else:
            tester.circuit.RADDR = hw.BitVector[ADDR_WIDTH](0)
            tester.circuit.WADDR = hw.BitVector[ADDR_WIDTH](i)

        tester.circuit.WDATA = hw.BitVector[DATA_WIDTH](i)
        tester.step(2)

    for i in range(1 << ADDR_WIDTH):
        tester.circuit.CEn = hw.Bit(0)
        tester.circuit.REn = hw.Bit(1)
        tester.circuit.WEn = hw.Bit(0)
        if base is SRAMSingle:
            tester.circuit.ADDR = hw.BitVector[ADDR_WIDTH](i)
        else:
            tester.circuit.RADDR = hw.BitVector[ADDR_WIDTH](i)
            tester.circuit.WADDR = hw.BitVector[ADDR_WIDTH](0)
        tester.circuit.WDATA = hw.BitVector[DATA_WIDTH](0)
        tester.step(2)
        tester.circuit.RDATA.expect(hw.BitVector[DATA_WIDTH](i))

    tester.compile_and_run("verilator", flags=["-Wno-fatal"])


@pytest.mark.parametrize('base', [SRAMSingle, SRAMDouble])
@pytest.mark.parametrize(
    'mixins, params', [
        ((SRAMRedundancyMixin, ), {
            'num_r_cols': 1
        }), ((
            SRAMModalMixin,
            SRAMRedundancyMixin,
        ), {
            'num_r_cols': 1
        }), ((
            SRAMModalMixin,
            SRAMRedundancyMixin,
        ), {
            'num_r_cols': 2
        })
    ]
)
def test_redundancy(base, mixins, params):
    generator = SRAM_FEATURE_TABLE[base][frozenset(mixins)]
    Definition = generator(ADDR_WIDTH, DATA_WIDTH, debug=True, **params)
    tester = fault.Tester(Definition, Definition.CLK)
    if SRAMModalMixin in mixins:
        State = Definition.State
        tester.circuit.deep_sleep = hw.Bit(1)
        tester.circuit.power_gate = hw.Bit(1)
        tester.eval()
        tester.circuit.current_state.expect(State.DeepSleep)
        tester.circuit.wake_ack.expect(hw.Bit(0))

        tester.circuit.deep_sleep = hw.Bit(0)
        tester.circuit.power_gate = hw.Bit(1)
        tester.eval()
        tester.circuit.current_state.expect(State.TotalRetention)
        tester.circuit.wake_ack.expect(hw.Bit(0))

        tester.circuit.deep_sleep = hw.Bit(1)
        tester.circuit.power_gate = hw.Bit(0)
        tester.eval()
        tester.circuit.current_state.expect(State.Retention)
        tester.circuit.wake_ack.expect(hw.Bit(0))

        tester.circuit.deep_sleep = hw.Bit(0)
        tester.circuit.power_gate = hw.Bit(0)
        tester.eval()
        tester.circuit.current_state.expect(State.Normal)
        tester.circuit.wake_ack.expect(hw.Bit(1))
        tester.step(2)
        tester.circuit.wake_ack.expect(hw.Bit(1))

    # enable redudancy on the all columns
    tester.circuit.RCE = hw.BitVector[params['num_r_cols']](-1)

    for i in range(params['num_r_cols']):
        setattr(
            tester.circuit, f'RCF{i}A',
            hw.BitVector[m.bitutils.clog2safe(Definition.num_v_cols)](i)
        )

    # Write 0 everywhere
    for i in range(1 << ADDR_WIDTH):
        tester.circuit.CEn = hw.Bit(0)
        tester.circuit.REn = hw.Bit(0)
        tester.circuit.WEn = hw.Bit(1)
        if base is SRAMSingle:
            tester.circuit.ADDR = hw.BitVector[ADDR_WIDTH](i)
        else:
            tester.circuit.RADDR = hw.BitVector[ADDR_WIDTH](0)
            tester.circuit.WADDR = hw.BitVector[ADDR_WIDTH](i)

        tester.circuit.WDATA = hw.BitVector[DATA_WIDTH](0)
        tester.step(2)

    # disable redudancy
    tester.circuit.RCE = hw.BitVector[params['num_r_cols']](0)

    # Write i everywhere
    for i in range(1 << ADDR_WIDTH):
        tester.circuit.CEn = hw.Bit(0)
        tester.circuit.REn = hw.Bit(0)
        tester.circuit.WEn = hw.Bit(1)
        if base is SRAMSingle:
            tester.circuit.ADDR = hw.BitVector[ADDR_WIDTH](i)
        else:
            tester.circuit.RADDR = hw.BitVector[ADDR_WIDTH](0)
            tester.circuit.WADDR = hw.BitVector[ADDR_WIDTH](i)

        tester.circuit.WDATA = hw.BitVector[DATA_WIDTH](i)
        tester.step(2)

    # enable redudancy
    tester.circuit.RCE = hw.BitVector[params['num_r_cols']](-1)

    # read everything back
    # the top bits should be 0,
    # and the bottom bits should be the top bits
    for i in range(1 << ADDR_WIDTH):
        tester.circuit.CEn = hw.Bit(0)
        tester.circuit.REn = hw.Bit(1)
        tester.circuit.WEn = hw.Bit(0)
        if base is SRAMSingle:
            tester.circuit.ADDR = hw.BitVector[ADDR_WIDTH](i)
        else:
            tester.circuit.RADDR = hw.BitVector[ADDR_WIDTH](i)
            tester.circuit.WADDR = hw.BitVector[ADDR_WIDTH](0)
        tester.circuit.WDATA = hw.BitVector[DATA_WIDTH](0)
        tester.step(2)
        tester.circuit.RDATA.expect(
            hw.BitVector[DATA_WIDTH](i) >> Definition.col_width *
            Definition.num_r_cols
        )

    tester.compile_and_run("verilator", flags=["-Wno-fatal"])


def test_stateful():
    State = SRAMStateful.State
    CMD = SRAMStateful.CMD
    Stateful = SRAMStateful(ADDR_WIDTH, DATA_WIDTH, False, debug=True)
    tester = fault.Tester(Stateful, Stateful.CLK)
    for mask in map(hw.BitVector[DATA_WIDTH], (0, 1, 2)):
        tester.circuit.CEn = hw.Bit(1)
        tester.step(2)
        tester.circuit.current_state.expect(State.SLEEP)

        tester.circuit.CEn = hw.Bit(0)
        tester.step(2)
        tester.circuit.current_state.expect(State.BOOT)

        tester.circuit.cmd = CMD.NOP
        tester.step(2)
        tester.circuit.current_state.expect(State.BOOT)
        tester.circuit.cmd = CMD.INIT
        tester.circuit.WDATA = mask
        tester.step(2)
        tester.circuit.current_state.expect(State.READY)
        tester.circuit.mask.expect(mask[:2])

        for i in range(1 << ADDR_WIDTH):
            tester.circuit.CEn = hw.Bit(0)
            tester.circuit.REn = hw.Bit(0)
            tester.circuit.WEn = hw.Bit(1)
            tester.circuit.RADDR = hw.BitVector[ADDR_WIDTH](0)
            tester.circuit.WADDR = hw.BitVector[ADDR_WIDTH](i)
            tester.circuit.WDATA = hw.BitVector[DATA_WIDTH](i)
            tester.step(2)

        for i in range(1 << ADDR_WIDTH):
            tester.circuit.CEn = hw.Bit(0)
            tester.circuit.REn = hw.Bit(1)
            tester.circuit.WEn = hw.Bit(0)
            tester.circuit.RADDR = hw.BitVector[ADDR_WIDTH](i)
            tester.circuit.WADDR = hw.BitVector[ADDR_WIDTH](0)
            tester.circuit.WDATA = hw.BitVector[DATA_WIDTH](0)
            tester.step(2)
            tester.circuit.RDATA.expect(hw.BitVector[DATA_WIDTH](i))
            tester.step(2)

        tester.circuit.CEn = hw.Bit(1)
        tester.step(2)
        tester.circuit.current_state.expect(State.SLEEP)

    tester.compile_and_run("verilator", flags=["-Wno-fatal"])
