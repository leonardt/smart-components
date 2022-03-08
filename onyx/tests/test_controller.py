import fault as f
import magma as m
from onyx_sram_subsystem.controller import Controller


def test_controller():
    controller = Controller()
    tester = f.Tester(controller)
    m.compile("build/Controller", controller)
