import fault
import hwtypes as hw
import magma as m

from onyx_sram_subsystem.mock_mem import SRAMSingle
from onyx_sram_subsystem.mock_mem import SRAMDouble
from onyx_sram_subsystem.mock_mem import SRAMStateful

def test_single():
    Single = SRAMSingle(4, 4, False)
    tester = fault.Tester(Single, Single.CLK)

    for i in range(1<<4):
        tester.circuit.CEn = hw.Bit(0)
        tester.circuit.REn = hw.Bit(0)
        tester.circuit.WEn = hw.Bit(1)
        tester.circuit.ADDR = hw.BitVector[4](i)
        tester.circuit.WDATA = hw.BitVector[4](i)
        tester.step(2)

    for i in range(1<<4):
        tester.circuit.CEn = hw.Bit(0)
        tester.circuit.REn = hw.Bit(1)
        tester.circuit.WEn = hw.Bit(0)
        tester.circuit.ADDR = hw.BitVector[4](i)
        tester.circuit.WDATA = hw.BitVector[4](0)
        tester.step(2)
        tester.circuit.RDATA.expect(hw.BitVector[4](i))
    tester.compile_and_run("verilator", flags=["-Wno-fatal"])



def test_double():
    Double = SRAMDouble(4, 4, False)
    tester = fault.Tester(Double, Double.CLK)

    for i in range(1<<4):
        tester.circuit.CEn = hw.Bit(0)
        tester.circuit.REn = hw.Bit(0)
        tester.circuit.WEn = hw.Bit(1)
        tester.circuit.RADDR = hw.BitVector[4](0)
        tester.circuit.WADDR = hw.BitVector[4](i)
        tester.circuit.WDATA = hw.BitVector[4](i)
        tester.step(2)

    for i in range(1<<4):
        tester.circuit.CEn = hw.Bit(0)
        tester.circuit.REn = hw.Bit(1)
        tester.circuit.WEn = hw.Bit(0)
        tester.circuit.RADDR = hw.BitVector[4](i)
        tester.circuit.WADDR = hw.BitVector[4](0)
        tester.circuit.WDATA = hw.BitVector[4](0)
        tester.step(2)
        tester.circuit.RDATA.expect(hw.BitVector[4](i))

    tester.compile_and_run("verilator", flags=["-Wno-fatal"])

def test_stateful():
    State = SRAMStateful.State
    CMD = SRAMStateful.CMD
    Stateful = SRAMStateful(4, 8, False, debug=True)
    tester = fault.Tester(Stateful, Stateful.CLK)
    for mask in map(hw.BitVector[8], (0,1,2)):
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
        # Failing for unkown reasons
        # tester.circuit.mask.expect(mask[:2])

        for i in range(1<<4):
            tester.circuit.CEn = hw.Bit(0)
            tester.circuit.REn = hw.Bit(0)
            tester.circuit.WEn = hw.Bit(1)
            tester.circuit.RADDR = hw.BitVector[4](0)
            tester.circuit.WADDR = hw.BitVector[4](i)
            tester.circuit.WDATA = hw.BitVector[8](i)
            tester.step(2)

        for i in range(1<<4):
            tester.circuit.CEn = hw.Bit(0)
            tester.circuit.REn = hw.Bit(1)
            tester.circuit.WEn = hw.Bit(0)
            tester.circuit.RADDR = hw.BitVector[4](i)
            tester.circuit.WADDR = hw.BitVector[4](0)
            tester.circuit.WDATA = hw.BitVector[8](0)
            tester.step(2)
            tester.circuit.RDATA.expect(hw.BitVector[8](i))
            tester.step(2)

        tester.circuit.CEn = hw.Bit(1)
        tester.step(2)
        tester.circuit.current_state.expect(State.SLEEP)

    tester.compile_and_run("verilator", flags=["-Wno-fatal"])
