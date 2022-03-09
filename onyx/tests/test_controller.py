from hwtypes import BitVector
import magma as m
import fault as f
from onyx_sram_subsystem.controller import Controller


def expect_write(tester, addr, output_name, data):
    tester.circuit.PADDR = addr
    tester.circuit.PSEL = 1
    tester.circuit.PENABLE = 0
    tester.circuit.PWRITE = 1
    tester.circuit.PWDATA = data
    tester.advance_cycle()
    tester.circuit.PSLVERR.expect(0)
    tester.circuit.PENABLE = 1
    tester.advance_cycle()
    tester.circuit.PENABLE = 0
    tester.circuit.PSEL = 0
    getattr(tester.circuit, output_name).expect(data)
    expect_read(tester, addr, data)


def expect_read(tester, addr, data):
    tester.circuit.PADDR = addr
    tester.circuit.PSEL = 1
    tester.circuit.PENABLE = 0
    tester.circuit.PWRITE = 0
    tester.advance_cycle()
    tester.circuit.PSLVERR.expect(0)
    tester.circuit.PENABLE = 1
    tester.advance_cycle()
    tester.circuit.PENABLE = 0
    tester.circuit.PSEL = 0
    tester.circuit.PRDATA.expect(data)


def test_controller():
    num_r_cols = 2
    num_v_cols = 4
    controller = Controller(num_r_cols, num_v_cols)
    tester = f.SynchronousTester(controller)
    tester.circuit.ASYNCRESETN = 1
    for addr, name in [
        (0, 'deep_sleep'),
        (1, 'power_gate'),
    ]:
        expect_write(tester, addr << 2, name, 1)

    for addr, name, data in [
        (2, 'RCE', BitVector.random(num_r_cols)),
    ] + [
        (3 + i, f'RCF{i}A',
         BitVector.random(m.bitutils.clog2safe(num_v_cols)))
        for i in range(num_r_cols)
    ]:
        expect_write(tester, addr << 2, name, data)

    tester.circuit.wake_ack = 1
    tester.advance_cycle()
    tester.circuit.wake_ack = 0

    offset = 2 + num_r_cols + 1
    for addr, expected in [
        (offset, 1),
        (offset + 1, 0x5A5A5A5A),
    ]:
        expect_read(tester, addr << 2, expected)
    tester.compile_and_run('verilator', flags=['--trace'])
