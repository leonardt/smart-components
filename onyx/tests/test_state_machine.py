##############################################################################
# Importing things

# import itertools as it
# FIXME don't need hwtypes, can use m.Bits instead I think
import hwtypes as hw

import pytest
import fault
import magma as m

# SRAM setup (mock_mem)
from onyx_sram_subsystem.mock_mem import SRAMSingle
from onyx_sram_subsystem.mock_mem import SRAMDouble
from onyx_sram_subsystem.mock_mem import SRAMRedundancyMixin
from onyx_sram_subsystem.mock_mem import SRAMModalMixin
from onyx_sram_subsystem.mock_mem import SRAM_FEATURE_TABLE

# state_machine setup
from onyx_sram_subsystem.state_machine import StateMachine
from onyx_sram_subsystem.state_machine import StateMachineGraph

# state_machine constants
# TODO/FIXME could wrap all these into e.g. "Enums" or "Constants"
# Or i dunno "import Enums as e" then can use e.g. e.State, e.Command ?
from onyx_sram_subsystem.state_machine import State
from onyx_sram_subsystem.state_machine import Command
from onyx_sram_subsystem.state_machine import Action

# To test/break, can replace right state w wrong in an edge e.g.
# < (State.MemOff,    Command.PowerOn,    Action.GetCommand,    State.SetMode),
# > (State.MemOff,    Command.PowerOn,    Action.GetCommand,    State.MemOff),


# SRAM setup

# SRAM = 2K 16-bit words, just like garnet :)
# SRAM_ADDR_WIDTH = 11
# SRAM_DATA_WIDTH = 16

# Change to match test_mock_mem
SRAM_ADDR_WIDTH = 8
SRAM_DATA_WIDTH = 8


##############################################################################
# Example build and show verilog functions

def build_verilog(smg):
    FSM = StateMachine(MemDefinition, smg)
    m.compile("steveri/tmpdir/fsm", FSM, output="mlir-verilog")

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
DBG9 = True
DBG9 = False
if DBG:
    def debug(m): print(m, flush=True)
else:
    def debug(m): pass

##############################################################################
# Each SRAM variant needs a different state machine to test it

# Convenient abbrev
ANY = Command.NoCommand

# Basic state machine common to all SRAM configurations
# Covers MemOn state and its children (read and write)
sm_read_and_write = (
    (State.MemOn,     Command.PowerOff,       State.MemOff),

    (State.MemOn,     Command.Read,           State.ReadAddr),
    (State.ReadAddr,  ANY,                    State.ReadData),
    (State.ReadData,  ANY,                    State.MemOn),

    (State.MemOn,     Command.Write,          State.WriteAddr),
    (State.WriteAddr, ANY,                    State.WriteData),
    (State.WriteData, ANY,                    State.MemOn),
)

# Init, no redundancy
sm_init = (
    (State.MemInit,   ANY,                    State.MemOff),
)

# Init for SRAMs with redundancy
sm_init_red = (
    (State.MemInit,   ANY,                    State.MemOff),
    (State.MemOn,     Command.RedOn,          State.MemOn),
    (State.MemOn,     Command.RedOff,         State.MemOn),
)

# MemOn for plain SRAMs
sm_memoff = (
    (State.MemOff,    Command.PowerOn,        State.MemOn),
)

# MemOn for SRAMs with multiple modes
sm_memoff_ack = (
    (State.MemOff,    Command.PowerOn,        State.SetMode),
    (State.SetMode,   Command.PowerOn,        State.MemOn),

    (State.MemOff,    Command.DeepSleep,      State.SetMode),
    (State.SetMode,   Command.DeepSleep,      State.MemOff),

    (State.MemOff,    Command.TotalRetention,   State.SetMode),
    (State.SetMode,   Command.TotalRetention,   State.MemOff),
)

# Prep a state machine for each different SRAM variety
graph_plain   = sm_init     + sm_read_and_write + sm_memoff
graph_red     = sm_init_red + sm_read_and_write + sm_memoff
graph_ack     = sm_init     + sm_read_and_write + sm_memoff_ack
graph_ack_red = sm_init_red + sm_read_and_write + sm_memoff_ack

# makedot("build/SMM", sm_init + sm_read_and_write)
def makedot(filename, graph):

    # from onyx_sram_subsystem.state_machine import build_dot_graph
    import sys
    import subprocess

    orig_stdout = sys.stdout

    filename_dot = filename + ".dot"
    filename_pdf = filename + ".pdf"


    # f = open('build/deleteme.txt', 'w')
    f = open(filename_dot, 'w')

    sys.stdout = f
    StateMachineGraph.build_dot_graph(graph)
    sys.stdout = orig_stdout
    f.close()

    # FIXME need a catch here or something because in general this will not work!!!
    subprocess.run(f'dot {filename_dot} -Tpdf > {filename_pdf}', shell=True)

# Build all four dot-graphs
makedot("build/graph",         graph_plain)
makedot("build/graph_red",     graph_red)
makedot("build/graph_ack",     graph_ack)
makedot("build/graph_ack_red", graph_ack_red)

quicktest = True
quicktest = False

if quicktest: singledouble = [SRAMSingle]
else:         singledouble = [SRAMSingle, SRAMDouble]

@pytest.mark.parametrize('base', singledouble)


# Stacking decorators? What th'? How does this even work???
# Trailing commas in 'mixins' tuples are *required* or it breaks...
@pytest.mark.parametrize(
    'mixins,                                  graph,           params',
  [
    ((),                                      (graph_plain),   {},                  ),
    ((SRAMModalMixin, ),                      (graph_ack),     {},                  ),
    ((SRAMRedundancyMixin, ),                 (graph_red),     { 'num_r_cols': 1 }, ),
    ((SRAMRedundancyMixin, ),                 (graph_red),     { 'num_r_cols': 2 }, ),
    ((SRAMModalMixin, SRAMRedundancyMixin, ), (graph_ack_red), { 'num_r_cols': 1 }, ),
    ((SRAMModalMixin, SRAMRedundancyMixin, ), (graph_ack_red), { 'num_r_cols': 2 }, ),
  ]
)

# FIXME/TODO can break this up into multiple tests see e.g.
# test_mock_mem.py test_sram(), test_redundancy(),  etc.
def test_state_machine_fault(base, mixins, graph, params):

    ##############################################################################
    # Instantiate SRAM
    smg = StateMachineGraph(graph)
    generator = SRAM_FEATURE_TABLE[base][frozenset(mixins)]
    MemDefinition = generator(
        SRAM_ADDR_WIDTH, SRAM_DATA_WIDTH, debug=True, **params
    )

    # SRAM name, e.g. 'SRAMDM_inst0'. See mock_mem.py. E.g.
    # f=frozenset((SRAMModalMixin, ))
    # SRAM_FEATURE_TABLE[SRAMSingle][f].__name__ => 'SRAMSM'
    # => mock_name = 'SRAMSM_inst0'
    mock_name = generator.__name__ + '_inst0'

    # Convenient shortcuts for later
    has_redundancy = (SRAMRedundancyMixin in mixins)
    needs_wake_ack = (SRAMModalMixin      in mixins)

    if has_redundancy:
        RED_ON  = hw.BitVector[params['num_r_cols']](-1)
        RED_OFF = hw.BitVector[params['num_r_cols']]( 0)

    ##############################################################################
    # Old school debugging: tell verilator to print things to its log

    def prlog0(msg, *args):
        '''print to log'''
        tester.print("beep boop " + msg, *args)

    def prlog9(msg, *args):
        '''print to log iff extra debug requested'''
        if DBG9: tester.print("beep boop " + msg, *args)

    ##############################################################################
    debug("Build and test state machine")

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


    def send_and_check_dfc_data(dval, reg_name, reg, reg_CE):
        '''
        Send data to controller's DataFromClient (dfc) reg
        and verify that controller stored it in its reg 'reg_name'
        '''

        # Send dval to MC receive-queue as "DataFromClient" data
        prlog9("...sending data to controller L203\n")
        tester.circuit.receive = m.Bits[SRAM_DATA_WIDTH](dval)
        # prlog0("initreg is now %d (1)\n", tester.circuit.initreg.O)

        # Mark receive-queue (dfc/DataFromQueue) data "valid"
        prlog9("...sending valid signal\n")
        tester.circuit.receive_valid = VALID

        # FIXME should check "ready" signal before sending data

        # Wait one cycle for valid signal to propagate
        # After which valid signal and valid data should be avail on MC input regs
        prlog9("...after one cy valid sig should be avail internally\n")
        cycle()
        tester.circuit.dfcq_valid.expect(VALID)

        # prlog9("  BEFORE: mem_addr_reg is %d\n", tester.circuit.mem_addr_reg.O)
        prlog9(f"  BEFORE: {reg_name}_reg is %d\n", reg)

        # Sanity check of reg-enable signal
        prlog9("...CE better be active for dfc (CE=1)\n")
        tester.circuit.dfcq_enable.expect(1)
        prlog9("...CE better be active for internal reg too (CE=1)\n")
        reg_CE.expect(1)

        # Reset valid signal
        prlog9("...reset valid signal\n")
        tester.circuit.receive_valid = ~VALID

        # Wait one cycle MC to clock data in, and goto new state
        prlog9("...one more cy to latch data and move to new state\n")
        cycle()

        # prlog9("  AFTER: mem_addr_reg is %d (762)\n", tester.circuit.mem_addr_reg.O)
        prlog9(f"  AFTER: {reg_name}_reg is %d (762)\n", reg)

        # Check latched data for correctness
        msg = f"MC received {reg_name} data '%d' ==? {dval} (0x{dval:x})"
        prlog9(f"{msg}\n", reg)
        reg.expect(dval)
        prlog9(f"...yes! passed initial {reg_name} data check\n")


    def get_and_check_dtc_data(dval, check_data=True):
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
        tester.circuit.dtcq_ready.expect(READY)

        # Wait one complete clock cycle for...what...?
        cycle()

        # See what we got / check latched data for correctness
        send = tester.circuit.send
        msg = f"MC sent us data '%x'"
        prlog9(f"{msg}\n",  send)
        if check_data:
            send.expect(dval)
            prlog9(f"...yes! passed data check\n")

        prlog9(f"still expect ready=1\n")
        tester.circuit.dtcq_ready.expect(READY)

        # reset ready signal i guess
        tester.circuit.send_ready = ~READY


    def setmode(cname, cmd, mstate, want_ack):
        '''FIXME add descriptive comment here'''

        if want_ack == 0: (final_str, final) = ("MemOff", State.MemOff)
        else:             (final_str, final) = ("MemOn",  State.MemOn)

        prlog0("-----------------------------------------------\n")
        prlog0(f"Check transition MemOff => SetMode => {final_str} on command {cname} 465\n")
        check_transition(cmd, State.SetMode)

        prlog9("  - successfully arrived in state SetMode\n")
        tester.circuit.current_state.expect(State.SetMode)

        prlog0(f"  - verify SRAM state = {cname}\n")
        mock_ckt = getattr(tester.circuit, mock_name) # E.g. "tester.circuit.SRAMSM_inst0"
        mock_ckt.current_state.expect(mstate)

        prlog0(f"  - check that MC sent WakeAck data '{want_ack}'\n")
        get_and_check_dtc_data(want_ack)
        cycle()

        if want_ack == 0:
            prlog0(f"  - and now we should be in state MemOff (0x{int(State.MemOff)})\n")
            tester.circuit.current_state.expect(State.MemOff)
        else:
            prlog0(f"  - and now we should be in state MemOn (0x{int(State.MemOn)})\n")
            tester.circuit.current_state.expect(State.MemOn)

        prlog0(f"  - and now we should be in state {final_str} (0x{int(final)})\n")
        tester.circuit.current_state.expect(final)

        prlog9("  CORRECT!\n")


    def write_sram(addr, data, dbg=False):
        ''' Assuming MC is in state MemOn, write "data" to "addr" '''

        prlog9("-----------------------------------------------\n")
        if dbg: prlog0(f"WRITE address '0x{addr:x}' with data '0x{data:x}'\n")

        prlog9(f"-----------------------------------------------\n")
        prlog9("Check transition MemOn => WriteAddr on command Write\n")
        check_transition(Command.Write, State.WriteAddr)
        prlog9("successfully arrived in state WriteAddr\n")

        ########################################################################
        # addr = 0x88     # Set this to e.g. 87 to make it break below...
        prlog9(f"-----------------------------------------------\n")
        prlog9(f"Check that MC received mem addr '0x{addr:x}'\n")
        send_and_check_dfc_data(addr, "mem_addr", tester.circuit.mem_addr_reg_out, tester.circuit.mem_addr_reg_CE_out)

        ########################################################################
        prlog9("-----------------------------------------------\n")
        prlog9("Verify arrival in state WriteData\n")
        tester.circuit.current_state.expect(State.WriteData)
        prlog9("...CORRECT!\n")

        ########################################################################
        # data = 0x1088
        prlog9(f"-----------------------------------------------\n")
        prlog9(f"Send data '0x{data:x}' to MC and verify receipt\n")
        send_and_check_dfc_data(data, "mem_data_reg", tester.circuit.mem_data_reg_out, tester.circuit.mem_data_reg_CE_out)

        ########################################################################
        prlog9("-----------------------------------------------\n")
        prlog9("Verify arrival in state MemOn\n")
        tester.circuit.current_state.expect(State.MemOn)
        prlog9("...CORRECT!\n")


    def read_sram(addr, expect_data, dbg=False, check_data=False):
        ' Read SRAM address "addr", verify that we got "expect_data" '

        prlog9("-----------------------------------------------\n")
        if dbg: prlog0(f"READ  address '0x{addr:x}', verify = '0x{expect_data:x}'\n")

        ########################################################################
        prlog9("-----------------------------------------------\n")
        prlog9("Check transition MemOn => ReadAddr on command Read\n")
        check_transition(Command.Read, State.ReadAddr)
        prlog9("successfully arrived in state ReadAddr\n")

        prlog9("-----------------------------------------------\n")
        prlog9(f"Send addr '0x{addr:x}' to MC and check receipt\n")
        send_and_check_dfc_data(addr, "mem_addr", tester.circuit.mem_addr_reg_out, tester.circuit.mem_addr_reg_CE_out)

        ########################################################################
        prlog9("-----------------------------------------------\n")
        prlog9("Verify arrival in state ReadData\n")
        tester.circuit.current_state.expect(State.ReadData)
        prlog9("...CORRECT!\n")

        ########################################################################
        # wantdata = 0x1066
        prlog9("-----------------------------------------------\n")
        prlog9(f"Check that MC sent data '0x{expect_data:x}'\n")
        get_and_check_dtc_data(expect_data, check_data=check_data)
        cycle()


        ########################################################################
        prlog9("-----------------------------------------------\n")
        prlog9("Verify arrival in state MemOn\n")
        tester.circuit.current_state.expect(State.MemOn)
        prlog9("...CORRECT!\n")
        cycle()

    def initialize_memory():
        '''boot memory and move from state MemInit to MemOff'''

        prlog0("(tester data not valid yet so setting dfc valid=0)\n");
        tester.circuit.receive_valid  = m.Bits[1](0)

        prlog0("(offer not valid yet so setting offer_valid=0)\n");
        tester.circuit.offer_valid = m.Bits[1](0)

        ########################################################################
        # Expect to start in state MemInit
        tester.circuit.current_state.expect(State.MemInit)
        prlog0("-----------------------------------------------\n")
        prlog0("Successfully booted in state MemInit maybe\n")

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


    def check_memoff_modes(needs_wake_ack):
        '''Check all the MemOff modes, ending at MemOn'''
        if needs_wake_ack:

            # needs_wake_ack means we have an SRAM with multiple possible states
            # e.g. DeepSleep, Normal, etc.

            setmode(
                "DeepSleep",
                Command.DeepSleep,
                SRAMModalMixin.State.DeepSleep,
                want_ack=0,
            )
            setmode(
                "TotalRetention",
                Command.TotalRetention,
                SRAMModalMixin.State.TotalRetention,
                want_ack=0,
            )
            setmode(
                "PowerOn",
                Command.PowerOn,
                SRAMModalMixin.State.Normal,
                want_ack=1,
            )
            # FIXME should add final mode "Retention" someday haha

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


    def readwrite_check_two_locations():
        '''Write and read two random locations in the SRAM'''

        prlog0("-----------------------------------------------\n")
        write_sram(addr=0x33, data=       0x3)
        read_sram( addr=0x33, expect_data=0x3, check_data=True)

        prlog0("-----------------------------------------------\n")
        write_sram(addr=0x88, data=       0x8)
        read_sram( addr=0x88, expect_data=0x8, check_data=True)

    def readwrite_first_and_last():
        '''Write and read first and last n location of the SRAM'''

        # Takes way too long to do all 2K addresses...so...
        # ...just do first four and last four
        def print_region(i):
            MAX_ADDR = 1 << SRAM_ADDR_WIDTH
            return (i <= 0x3) or (i >= (MAX_ADDR-4))

        # Write
        prlog0("-----------------------------------------------\n")
        prlog0("# For i = 0 to MAX_ADDR, write i => SRAM[i] (first and last four only)\n")
        # For i = 0 to MAX_ADDR, write i => SRAM[i]
        for i in range( 1 << SRAM_ADDR_WIDTH ):
            if not print_region(i): continue
            write_sram(addr=i, data=i, dbg=print_region(i) )
            if i==0x3: prlog0("...\n")

        # Read
        prlog0("-----------------------------------------------\n")
        prlog0("# For i = 0 to MAX_ADDR, read SRAM[i] =? i (first and last four only)\n")
        # For i = 0 to MAX_ADDR, read SRAM[i] =? i
        for i in range( 1 << SRAM_ADDR_WIDTH ):
            if not print_region(i): continue
            read_sram(addr=i, expect_data=i, dbg=print_region(i), check_data=True )
            if i==0x3: prlog0("...\n")

    def set_redundancy(want_redundancy, dbg=False):
        prlog9("-----------------------------------------------\n")

        if want_redundancy:
            prlog0("Turn on redundancy, remain in state MemOn\n")
            check_transition(Command.RedOn, State.MemOn)

            if dbg: prlog0("  - verify redundancy is ON (111...)\n")
            mock_ckt.RCE.expect(RED_ON)

        else:
            prlog0("Turn off redundancy, remain in state MemOn\n")
            check_transition(Command.RedOff, State.MemOn)

            if dbg: prlog0("  - verify redundancy is OFF (0)\n")
            mock_ckt.RCE.expect(RED_OFF)

        if dbg: prlog0("  - and now we should be in state Mem0n\n")
        tester.circuit.current_state.expect(State.MemOn)


    ########################################################################
    # BEGIN TEST
    ########################################################################

    # Tester setup
    Definition = StateMachine(MemDefinition, smg)
    tester = fault.Tester(Definition, Definition.CLK)
    prlog0("TESTING STATE_MACHINE CIRCUIT\n")

    # Initialize tester; boot memory and move from state MemInit to MemOff
    initialize_memory()

    # Check all the MemOff modes, ending at MemOn
    check_memoff_modes(needs_wake_ack)

    # Write and read two random locations in the SRAM
    readwrite_check_two_locations()

    # Write and read first and last n location of the SRAM
    readwrite_first_and_last()


    ########################################################################
    # Redundancy checks

    if has_redundancy:
        N_SRAM_WORDS = 1 << SRAM_ADDR_WIDTH

        prlog0("-----------------------------------------------\n")
        prlog0("REDUNDANCY CHECKS\n")

        mock_ckt = getattr(tester.circuit, mock_name) # E.g. "tester.circuit.SRAMSM_inst0"

        prlog9("Expect RCF0A == 0\n")
        mock_ckt.RCF0A.expect(0)

        ####################################################################
        # enable redundancy on all columns, write zeroes everywhere
        set_redundancy(True)

        prlog9("-----------------------------------------------\n")
        prlog0("  - write 0 everywhere\n")
        for i in range(N_SRAM_WORDS): write_sram(addr=i, data=0, dbg=DBG9)

        prlog9("  - verify redundancy still ON (111...)\n")
        mock_ckt.RCE.expect(RED_ON)


        ####################################################################
        # disable redundancy, write i everywhere
        set_redundancy(False, dbg=DBG9)

        prlog9("-----------------------------------------------\n")
        prlog0("  - write i everywhere\n")
        for i in range(N_SRAM_WORDS): write_sram(addr=i, data=i, dbg=DBG9)

        prlog9("  - verify redundancy still OFF (0)\n")
        mock_ckt.RCE.expect(RED_OFF)


        ####################################################################
        # enable redundancy, read everything back
        set_redundancy(True)

        prlog0("  - read everything back: 16 each 0,0,0... 1,1,1... f,f,f\n")
        # read everything back
        # "the top bits should be 0, and the bottom bits should be the top bits"
        # I.e. for 8-bit data with 1 redundant column, should see
        #     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        #     1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        #     2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        #     ...
        #     f, f, f, f, f, f, f, f, f, f, f, f, f, f, f, f
        #
        # SRAM is three 4-bit columns, 3rd column is redundant (with...?)
        for i in range(N_SRAM_WORDS):
            # expect = hw.BitVector[8](i) >> 4
            expect = i >> 4
            prlog9(f"mem[{i:d}] == {expect} ?\n")
            read_sram(addr=i, expect_data=expect, dbg=DBG9)


        prlog0("REDUNDANCY CHECKS SUCCESSED\n")
        prlog0("-----------------------------------------------\n")


    ########################################################################
    # Turn it off
    ########################################################################
    prlog9("-----------------------------------------------\n")
    prlog0("Check transition MemOn => MemOff on command PowerOff\n")
    check_transition(Command.PowerOff, State.MemOff)
    prlog9("successfully arrived in state MemOff\n")


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

    # For waveforms/gtkw turn on '--trace'
    debug("* Begin verilator compile-and-run")
    tester.compile_and_run(
        "verilator",
        flags=["-Wno-fatal"],
        # flags=["-Wno-fatal", "--trace"],
        magma_output="mlir-verilog",
        magma_opts={"verilator_debug": True},
        directory="build",
    )
    # Note - If test succeeds, log (stdout) is not displayed :(
    print("""To read fault-test log:
    cat tmpdir/obj_dir/StateMachine.log | sed 's/beep/\\
beep/g'    """)
    pass
