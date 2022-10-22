import itertools as it

import pytest
import fault
import hwtypes as hw
import magma as m

# SRAM setup

from onyx_sram_subsystem.mock_mem import SRAMSingle
from onyx_sram_subsystem.mock_mem import SRAMDouble
from onyx_sram_subsystem.mock_mem import SRAMRedundancyMixin
from onyx_sram_subsystem.mock_mem import SRAMModalMixin
from onyx_sram_subsystem.mock_mem import SRAM_FEATURE_TABLE

from onyx_sram_subsystem.state_machine import StateMachine
from onyx_sram_subsystem.state_machine import StateMachineGraph

# TODO/FIXME could wrap all these into e.g. "Enums" or "Constants"
# Or i dunno "import Enums as e" then can use e.g. e.State, e.Command ?
from onyx_sram_subsystem.state_machine import State
from onyx_sram_subsystem.state_machine import Command
from onyx_sram_subsystem.state_machine import Action


ANY = Command.NoCommand

# State Machine Graph, MemInit => MemOn paths

mygraph_nul_on = (
    (State.MemInit,   ANY,                Action.NoAction,      State.MemOff),
    (State.MemOff,    Command.PowerOn,    Action.GetCommand,    State.MemOn),
)
mygraph_nul_ack = (
    (State.MemInit,   ANY,                Action.NoAction,      State.MemOff),
    (State.MemOff,    Command.PowerOn,    Action.GetCommand,    State.SendAck),
    (State.SendAck,   ANY,                Action.SendAck,       State.MemOn),
)
mygraph_red_on = (
    (State.MemInit,   ANY,                Action.GetRedundancy, State.MemOff),
    (State.MemOff,    Command.PowerOn,    Action.GetCommand,    State.MemOn),
)
mygraph_red_ack = (
    (State.MemInit,   ANY,                Action.GetRedundancy, State.MemOff),
    (State.MemOff,    Command.PowerOn,    Action.GetCommand,    State.SendAck),
    (State.SendAck,   ANY,                Action.SendAck,       State.MemOn),
)

# State Machine Graph, MemOn => (read, write, off)

mygraph_read_and_write = (
    (State.MemOn,     Command.PowerOff,   Action.GetCommand,    State.MemOff),
    (State.MemOn,     Command.Read,       Action.GetCommand,    State.ReadAddr),
    (State.MemOn,     Command.Write,      Action.GetCommand,    State.WriteAddr),
    (State.ReadAddr,  ANY,                Action.GetAddr,       State.ReadData),
    (State.WriteAddr, ANY,                Action.GetAddr,       State.WriteData),
    (State.WriteData, ANY,                Action.WriteData,     State.MemOn),
    (State.ReadData,  ANY,                Action.ReadData,      State.MemOn),
)


# FIXME/TODO these can all share the basic machine i.e. apply a hierarchy or some such
mygraph_plain   = mygraph_nul_on  + mygraph_read_and_write
mygraph_SMM     = mygraph_nul_ack + mygraph_read_and_write
mygraph_SRM     = mygraph_red_on  + mygraph_read_and_write
mygraph_SMM_SMR = mygraph_red_ack + mygraph_read_and_write


# To test/break, can replace right state w wrong in an edge e.g.
# < (State.MemOff,    Command.PowerOn,    Action.GetCommand,    State.SendAck),
# > (State.MemOff,    Command.PowerOn,    Action.GetCommand,    State.MemOff),

########################################################################
# SRAM setup

# Maybe we'll come back to this, but probabl;y not...
# # Choose a base
# SRAM_base = SRAMDouble
# SRAM_base = SRAMSingle
# 
# # Choose a "mixin"
# SRAM_mixins = (SRAMModalMixin, )
# SRAM_mixins = (SRAMRedundancyMixin, )
# SRAM_mixins = (SRAMModalMixin,SRAMRedundancyMixin, )
# 
# # If mode includes redundancy, will need to choose one of these two parameters
# if SRAMRedundancyMixin in SRAM_mixins:
#     # Choose one
#     SRAM_params = { 'num_r_cols': 1 }
#     SRAM_params = { 'num_r_cols': 2 }
# else:
#     SRAM_params = {}

SMM=SRAMModalMixin
SRM=SRAMRedundancyMixin

base=SRAMDouble; mixins=(SMM,);     params={                 }
base=SRAMDouble; mixins=(SRM,);     params={ 'num_r_cols': 1 }
base=SRAMDouble; mixins=(SRM,);     params={ 'num_r_cols': 2 }
base=SRAMDouble; mixins=(SMM,SRM,); params={ 'num_r_cols': 1 }
base=SRAMDouble; mixins=(SMM,SRM,); params={ 'num_r_cols': 2 }


# DONE/working plain GOOD!!
mygraph = mygraph_plain
base=SRAMDouble; mixins=();         params={                 } # 1020.0700
base=SRAMSingle; mixins=();         params={                 } # 1020.0720

# DONE/working SMM GOOD!!
mygraph = mygraph_SMM
base=SRAMSingle; mixins=(SMM,);     params={                 } # 1022.0700

# DONE/working SRM GOOD
mygraph = mygraph_SRM
base=SRAMSingle; mixins=(SRM,);     params={ 'num_r_cols': 1 } # 1022.0700
base=SRAMSingle; mixins=(SRM,);     params={ 'num_r_cols': 2 } # 1022.0720

# DONE/working SMM_SRM GOOD
mygraph = mygraph_SMM_SMR
base=SRAMSingle; mixins=(SMM,SRM,); params={ 'num_r_cols': 1 } # 1022.0700
base=SRAMSingle; mixins=(SMM,SRM,); params={ 'num_r_cols': 2 } # 1020.0720




########################################################################
smg = StateMachineGraph(mygraph)
SRAM_base = base; SRAM_mixins = mixins; SRAM_params = params


# SRAM = 2K 16-bit words, just like garnet :)
SRAM_ADDR_WIDTH = 11
SRAM_DATA_WIDTH = 16

# Instantiate SRAM
generator = SRAM_FEATURE_TABLE[SRAM_base][frozenset(SRAM_mixins)]
MemDefinition = generator(
    SRAM_ADDR_WIDTH, SRAM_DATA_WIDTH, debug=True, **SRAM_params
)

has_redundancy = (SRAMRedundancyMixin in SRAM_mixins)
needs_wake_ack = (SMM in SRAM_mixins)



# end SRAM setup
########################################################################


def build_verilog():
    FSM = StateMachine(MemDefinition, smg)
    m.compile("steveri/tmpdir/fsm", FSM, output="coreir-verilog")

def show_verilog():
    with open('steveri/tmpdir/fsm.v', 'r') as f: print(f.read())

# ------------------------------------------------------------------------
# build_verilog()
# show_verilog()
# print("==============================================================================")
# print("okay so that was the verilog")
# print("==============================================================================")
# print("TO TEST: cd blahblah; python test_state_machine.py or whatever
# ------------------------------------------------------------------------

#==============================================================================
# TESTBENCH
#==============================================================================

import fault

########################################################################
# FIXME can use logger
DBG  = True
DBG9 = False
if DBG:
    def debug(m): print(m, flush=True)
else:
    def debug(m): pass


def test_state_machine_fault():
    
    debug("Build and test state machine")

    def prlog0(msg, *args):
        '''print to log'''
        tester.print("beep boop " + msg, *args)

    def prlog9(msg, *args):
        '''print to log iff extra debug requested'''
        if DBG9: tester.print("beep boop " + msg, *args)

    # ready and valid are active high
    READY=1; VALID=1

    # Convenient little shortcut
    # - tester.step(1) is one clock edge
    # - cycle(1) = one complete clock cycle = two clock edges (one pos, one neg)
    def cycle(n=1): tester.step(2*n)

    def check_transition(cmd, state):
        ' Send "cmd" to controller, verify that it arrives in state "state" '

        # FIXME should check "ready" signal before sending data
        # something like...? 'while tester.circuit.offer_ready != 1: cycle()'

        # successfully fails when/if valid=0
        valid=1
        tester.circuit.offer = cmd
        tester.circuit.offer_valid = m.Bits[1](valid)

        # Because "offer" is registered, it takes two cycles to transition
        # Cy 1: offer => offer_reg, next_state reg changes, current_state stays the same
        # Cy 2: 'next_state' wire clocks into 'current_state' reg
        # One cycle = two tester steps
        # FIXME how would we do this in ONE cycle instead of two??
        cycle(2)

        # Verify arrival at desired state
        tester.circuit.current_state.expect(state)

        # WITHDRAW THE OFFER!!!
        tester.circuit.offer_valid = m.Bits[1](0)


    def send_and_check_dfc_data(dval, reg_name, reg):
        '''
        Send data to controller's DataFromClient (dfc) reg
        and verify that controller stored it in its reg 'reg_name'
        '''

        # Send dval to MC receive-queue as "DataFromClient" data
        prlog9("...sending data to controller L203\n")
        tester.circuit.receive = m.Bits[16](dval)
        # prlog0("initreg is now %d (1)\n", tester.circuit.initreg.O)

        # Mark receive-queue (dfc/DataFromQueue) data "valid"
        prlog9("...sending valid signal\n")
        tester.circuit.receive_valid = VALID

        # FIXME should check "ready" signal before sending data

        # Wait one cycle for valid signal to propagate
        # After which valid signal and valid data should be avail on MC input regs
        prlog9("...after one cy valid sig should be avail internally\n")
        cycle()
        tester.circuit.DataFromClient_valid.O.expect(VALID)

        # prlog9("  BEFORE: mem_addr_reg is %d\n", tester.circuit.mem_addr_reg.O)
        prlog9(f"  BEFORE: {reg_name}_reg is %d\n", reg.O)

        # Sanity check of reg-enable signal
        prlog9("...CE better be active for dfc (CE=1)\n")
        tester.circuit.DataFromClient.CE.expect(1)
        prlog9("...CE better be active for internal reg too (CE=1)\n")
        reg.CE.expect(1)

        # Reset valid signal
        prlog9("...reset valid signal\n")
        tester.circuit.receive_valid = ~VALID

        # Wait one cycle MC to clock data in, and goto new state
        prlog9("...one more cy to latch data and move to new state\n")
        cycle()

        # prlog9("  AFTER: mem_addr_reg is %d (762)\n", tester.circuit.mem_addr_reg.O)
        prlog9(f"  AFTER: {reg_name}_reg is %d (762)\n", reg.O)

        # Check latched data for correctness
        msg = f"MC received {reg_name} data '%d' ==? {dval} (0x{dval:x})"
        prlog9(f"{msg}\n", reg.O)
        reg.O.expect(dval)
        prlog9(f"...yes! passed initial {reg_name} data check\n")


    def get_and_check_dtc_data(dval):
        "Get data from controller's DataToClient (dtc) interface"

        # We expect that sender has valid data
        # tester.print("beep boop ...expect send_valid TRUE...\n")
        # tester.circuit.send_valid.expect(VALID)
 
        # Tell MC that we are ready to read the data
        prlog9("...sending ready signal\n")
        tester.circuit.send_ready = READY

        # Wait one cycle for ready signal to propagate
        # After which ready signal and valid data should be avail on MC input regs
        prlog9("...after one cy ready sig should be avail internally\n")
        cycle()
        tester.circuit.DataToClient_ready.O.expect(READY)

        # Wait one complete clock cycle for...what...?
        cycle()

        # See what we got / check latched data for correctness
        reg = tester.circuit.DataToClient
        msg = f"MC sent us data '%x' ==? {dval} (0x{dval:x})"
        prlog9(f"{msg}\n",  reg.O)
        reg.O.expect(dval)
        prlog9(f"...yes! passed data check\n")

        prlog9(f"still expect ready=1\n")
        tester.circuit.DataToClient_ready.O.expect(READY)

        # reset ready signal i guess
        tester.circuit.send_ready = ~READY

    def write_sram(addr, data):
        ''' Assuming MC is in state MemOn, write "data" to "addr" '''

        prlog9("-----------------------------------------------\n")
        prlog0(f"WRITE address '0x{addr:x}' with data '0x{data:x}'")

        prlog9(f"-----------------------------------------------\n")
        prlog9("Check transition MemOn => WriteAddr on command Write\n")
        check_transition(Command.Write, State.WriteAddr)
        prlog9("successfully arrived in state WriteAddr\n")

        ########################################################################
        # addr = 0x88     # Set this to e.g. 87 to make it break below...
        prlog9(f"-----------------------------------------------\n")
        prlog9(f"Check that MC received mem addr '0x{addr:x}'\n")
        send_and_check_dfc_data(addr, "mem_addr", tester.circuit.mem_addr_reg)

        ########################################################################
        prlog9("-----------------------------------------------\n")
        prlog9("Verify arrival in state WriteData\n")
        tester.circuit.current_state.expect(State.WriteData)
        prlog9("...CORRECT!\n")

        ########################################################################
        # data = 0x1088
        prlog9(f"-----------------------------------------------\n")
        prlog9(f"Send data '0x{data:x}' to MC and verify receipt\n")
        send_and_check_dfc_data(data, "mem_data_reg", tester.circuit.mem_data_reg)

        ########################################################################
        prlog9("-----------------------------------------------\n")
        prlog9("Verify arrival in state MemOn\n")
        tester.circuit.current_state.expect(State.MemOn)
        prlog9("...CORRECT!\n")


    def read_sram(addr, expect_data):
        ' Read SRAM address "addr", verify that we got "expect_data" '

        prlog9("-----------------------------------------------\n")
        prlog0(f"READ  address '0x{addr:x}', verify = '0x{expect_data:x}'")

        ########################################################################
        prlog9("-----------------------------------------------\n")
        prlog9("Check transition MemOn => ReadAddr on command Read\n")
        check_transition(Command.Read, State.ReadAddr)
        prlog9("successfully arrived in state ReadAddr\n")

        prlog9("-----------------------------------------------\n")
        prlog9(f"Send addr '0x{addr:x}' to MC and check receipt\n")
        send_and_check_dfc_data(addr, "mem_addr", tester.circuit.mem_addr_reg)

        ########################################################################
        prlog9("-----------------------------------------------\n")
        prlog9("Verify arrival in state ReadData\n")
        tester.circuit.current_state.expect(State.ReadData)
        prlog9("...CORRECT!\n")

        ########################################################################
        # wantdata = 0x1066
        prlog9("-----------------------------------------------\n")
        prlog9(f"Check that MC sent data '0x{expect_data:x}'\n")
        get_and_check_dtc_data(expect_data)
        cycle()

        ########################################################################
        prlog9("-----------------------------------------------\n")
        prlog9("Verify arrival in state MemOn\n")
        tester.circuit.current_state.expect(State.MemOn)
        prlog9("...CORRECT!\n")
        cycle()


    ########################################################################
    # BEGIN TEST
    ########################################################################

    ########################################################################
    # Tester setup
    Definition = StateMachine(MemDefinition, smg)
    tester = fault.Tester(Definition, Definition.CLK)
    prlog0("TESTING STATE_MACHINE CIRCUIT\n")

    prlog0("(tester data not valid yet so setting dfc valid=0)\n");
    tester.circuit.receive_valid  = m.Bits[1](0)

    prlog0("(offer not valid yet so setting offer_valid=0)\n");
    tester.circuit.offer_valid = m.Bits[1](0)

    ########################################################################
    # Expect to start in state MemInit
    tester.circuit.current_state.expect(State.MemInit)
    prlog0("-----------------------------------------------\n")
    prlog0("Successfully booted in state MemInit maybe\n")
    prlog0("  - sending redundancy data to MC\n")


    if has_redundancy:
        ########################################################################
        # rdata = 17
        # rdata -1 "enables redundancy to all columns" according to e.g. test_mock_mem.py
        rdata = -1

        prlog9("-----------------------------------------------\n")
        prlog0(f"  - check that MC received redundancy data '{rdata}'\n")
        send_and_check_dfc_data(rdata, "redundancy", tester.circuit.redundancy_reg)

    else:
        cycle()

    ########################################################################
    prlog9("-----------------------------------------------\n")
    prlog0("  - and now we should be in state Memoff\n")
    tester.circuit.current_state.expect(State.MemOff)

    ########################################################################
    prlog0("-----------------------------------------------\n")
    prlog0("Check transition MemOff => MemOff on command PowerOff\n")
    check_transition(Command.PowerOff, State.MemOff)
    prlog9("successfully arrived in state MemOff\n")


    if needs_wake_ack:

        # memoff => sendack => memon has to happen all together
        ########################################################################
        prlog0("-----------------------------------------------\n")
        prlog0("Check transition MemOff => SendAck => MemOn on command PowerOn 752\n")
        check_transition(Command.PowerOn, State.SendAck)
        prlog9("successfully arrived in state SendAck\n")
        ########################################################################
        WAKE_ACK_TRUE = 1

        wantdata = WAKE_ACK_TRUE
        prlog9("-----------------------------------------------\n")
        prlog0(f"  - check that MC sent WakeAck data '{wantdata}'\n")
        get_and_check_dtc_data(wantdata)
        cycle()
        ########################################################################
        prlog9("-----------------------------------------------\n")
        prlog0(f"  - and now we should be in state MemOn (0x{int(State.MemOn)})\n")
        tester.circuit.current_state.expect(State.MemOn)
        prlog9("  CORRECT!\n")
        ########################################################################

    else:
        prlog0("-----------------------------------------------\n")
        prlog0("Check transition MemOff => MemOn on command PowerOn 752\n")
        check_transition(Command.PowerOn, State.MemOn)
        prlog9("successfully arrived in state MemOn\n")
        


    ########################################################################
    prlog0("-----------------------------------------------\n")
    prlog0("Check transition MemOn => MemOn on command Idle\n")
    check_transition(Command.Idle, State.MemOn)
    prlog9("successfully arrived in state MemOn\n")

    ########################################################################
    prlog9("-----------------------------------------------\n")
    prlog0("Check transition MemOn => MemOff on command PowerOff\n")
    check_transition(Command.PowerOff, State.MemOff)
    prlog9("successfully arrived in state MemOff\n")


    # TODO/FIXME here and above, replace with def power_on() or something
    if needs_wake_ack:

        # memoff => sendack => memon has to happen all together
        # FIXME consider making this a method/function/subroutine or whatever tf
        ########################################################################
        prlog0("-----------------------------------------------\n")
        prlog0("Check transition MemOff => SendAck => MemOn on command PowerOn 944\n")
        check_transition(Command.PowerOn, State.SendAck)
        prlog9("successfully arrived in state SendAck\n")
        ########################################################################
        wantdata = int(WAKE_ACK_TRUE)
        prlog9("-----------------------------------------------\n")
        prlog0(f"  - check that MC sent WakeAck data '{wantdata}'\n")
        get_and_check_dtc_data(wantdata)
        cycle()
        ########################################################################
        prlog9("-----------------------------------------------\n")
        prlog0(f"  - and now we should be in state MemOn (0x{int(State.MemOn)})\n")
        tester.circuit.current_state.expect(State.MemOn)
        prlog9(f"  - CORRECT!\n")
        ########################################################################
    else:
        prlog0("-----------------------------------------------\n")
        prlog0("Check transition MemOff => MemOn on command PowerOn 752\n")
        check_transition(Command.PowerOn, State.MemOn)
        prlog9("successfully arrived in state MemOn\n")




#     ########################################################################
#     read_sram(addr=0x66, expect_data=0x1066)
# 
# 
#     ########################################################################
#     prlog9("-----------------------------------------------\n")
#     prlog0("Verify *still* in state MemOn\n")
#     tester.circuit.current_state.expect(State.MemOn)
#     prlog9("...CORRECT!\n")
# 
# 
#     ########################################################################
#     write_sram(addr=0x88, data=0x1088)



    prlog0("-----------------------------------------------\n")
    write_sram(addr=0x33, data=       0x1033)
    read_sram( addr=0x33, expect_data=0x1033)

    prlog0("-----------------------------------------------\n")
    write_sram(addr=0x88, data=       0x1088)
    read_sram( addr=0x88, expect_data=0x1088)

    prlog0("-----------------------------------------------\n")
    prlog0("PASSED ALL TESTS\n")


    ########################################################################
    # Note the newlines do not print to the log file so you have to do
    # something like
    #    % python state_machine.py | sed 's/beep/\
    #    beep/g'
    #
    # or maybe
    #    % python state_machine.py && cat tmpdir/obj_dir/StateMachine.log | sed 's/beep/\
    #    beep/g'
    #
    # BEFORE: beep boop testing state_machine circuitbeep boop successfully booted in state
    # AFTER:
    #    beep boop testing state_machine circuit
    #    beep boop successfully booted in state

    ################################################################
    # Fault supports peeking, expecting, and printing internal signals.
    # For the verilator target, you should use the keyword argument
    # magma_opts with "verilator_debug" set to true. This will cause
    # coreir to compile the verilog with the required debug comments.
    #
    #    tester.compile_and_run("verilator", flags=["-Wno-fatal"], 
    #        magma_opts={"verilator_debug": True}, directory="build")

    debug("* Begin verilator compile-and-run")
    tester.compile_and_run(
        "verilator",
        flags=["-Wno-fatal"],
        magma_opts={"verilator_debug": True},
        directory="tmpdir",
    )
    # Note - If test succeeds, log (stdout) is not displayed :(
    print("""To read fault-test log:
    cat tmpdir/obj_dir/StateMachine.log | sed 's/beep/\\
beep/g'    """)
