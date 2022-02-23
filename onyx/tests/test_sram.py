import magma as m
from onyx_sram_subsystem.sram import SRAM


def test_sram():
    m.compile("build/SRAM", SRAM(32, m.Bits[8]))
