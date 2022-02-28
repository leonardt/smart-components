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
    Stateful = SRAMStateful(4, 8, False, debug=True)

