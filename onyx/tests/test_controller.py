import fault as f
from onyx_sram_subsystem.controller import Controller


def test_controller():
    controller = Controller()
    tester = f.SynchronousTester(controller)
    tester.circuit.ASYNCRESETN = 1
    for addr, name in [
        (0, 'deep_sleep'),
        (1, 'power_gate'),
        (2, 'col_cfg')
    ]:
        tester.circuit.PADDR = addr << 2
        tester.circuit.PSEL = 1
        tester.circuit.PENABLE = 0
        tester.circuit.PWRITE = 1
        tester.circuit.PWDATA = 1
        tester.advance_cycle()
        tester.circuit.PENABLE = 1
        tester.advance_cycle()
        tester.circuit.PENABLE = 0
        tester.circuit.PSEL = 0
        getattr(tester.circuit, name).expect(1)
    tester.circuit.wake_ack = 1
    tester.advance_cycle()
    tester.circuit.wake_ack = 0
    for addr, expected in [
        (3, 1),
        (4, 0x5A5A5A5A),
    ]:
        tester.circuit.PADDR = addr << 2
        tester.circuit.PSEL = 1
        tester.circuit.PENABLE = 0
        tester.circuit.PWRITE = 0
        tester.advance_cycle()
        tester.circuit.PENABLE = 1
        tester.advance_cycle()
        tester.circuit.PENABLE = 0
        tester.circuit.PSEL = 0
        tester.circuit.PRDATA.expect(expected)
    tester.compile_and_run('verilator', flags=['--trace'])
