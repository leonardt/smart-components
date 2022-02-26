from onyx_sram_subsystem.mock_mem import SRAMSingle
from onyx_sram_subsystem.mock_mem import SRAMDouble

def test_mock():
    single = SRAMSingle(32, 8, False)
    double = SRAMDouble(32, 8, False)
