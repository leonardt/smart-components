import magma as m
import fault as f
from hwtypes import BitVector
from onyx_sram_subsystem.sram import SRAM


def test_sram():
    tester = f.SynchronousTester(SRAM(32, m.Bits[8]))
    tester.circuit.command = 1
    tester.advance_cycle()
    tester.circuit.command = 0
    for i in range(4):
        # TODO: Add num_cycles param to fault
        tester.advance_cycle()
    tester.circuit.WE = 1
    tester.circuit.RE = 1
    tester.circuit.ADDR = addr = BitVector.random(5)
    tester.circuit.WDATA = data = BitVector.random(8)
    tester.advance_cycle()
    tester.circuit.WE = 0
    tester.advance_cycle()
    tester.circuit.RDATA.expect(data)
    tester.compile_and_run("verilator", flags=["--trace"])
