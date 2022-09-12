# TODO NEXT
# - continue scrubbing the state machine i guess


##############################################################################
README='''

# Also see README.txt

# To see state machine diagram:
    display state_machine2.png

# To run state machine
    python state_machine.py

# To see output from state machine run
    cat tmpdir/obj_dir/StateMachine.log | sed 's/beep/\
beep/g'

# To compare state machine verilog vs. prev successful run(s)
    diff ref/StateMachine.v tmpdir/StateMachine.v && echo PASS || echo FAIL

# To automatically run, see output, and compare to prev
    ./test_state_machine.sh

'''
##############################################################################

DBG=True
if DBG:
    import sys
    def debug(m):
        print(m); sys.stdout.flush()
else:
    def debug(m): pass

import sys
debug("Begin importing python packages...")
import magma as m
import hwtypes as ht
from mock_mem import SRAMDMR
from session import Offer, Choose, Send, Recieve, Sequence
from session import SessionTypeVisitor, SessionT, LabelT
from util import inverse_look_up, BiMap
debug("* Done importing python packages...")

class CoopGenerator(m.Generator2):
    def __init__(self, **kwargs):
        self._decl_attrs(**kwargs)
        self._decl_io(**kwargs)
        self._decl_components(**kwargs)
        self._connect(**kwargs)

    def _decl_attrs(self, **kwargs): pass

    def _decl_io(self, **kwargs):
        self.io = m.IO()

    def _decl_components(self, **kwargs): pass
    def _connect(self, **kwargs): pass

class Command():
    #----------------------------------
    num_commands = 5; i=0
    nbits = (num_commands-1).bit_length()

    # For compatibility w/ prev version
    nbits = 4  # Good for up to 16 commands
    #----------------------------------
    PowerOff = m.Bits[nbits](i); i=i+1
    PowerOn  = m.Bits[nbits](i); i=i+1 # not used
    Read     = m.Bits[nbits](i); i=i+1
    Write    = m.Bits[nbits](i); i=i+1
    Idle     = m.Bits[nbits](i); i=i+1

class State():
    #----------------------------------
    num_states = 4; i=0
    nbits = (num_states-1).bit_length()
    #----------------------------------
    MemInit = m.Bits[nbits](i); i=i+1
    MemOff  = m.Bits[nbits](i); i=i+1
    Send    = m.Bits[nbits](i); i=i+1 # currently unused maybe
    MemOn   = m.Bits[nbits](i); i=i+1

class MessageQueue():
    '''
    Examples:
      OLD: o_reg = m.Register(T=m.Bits[nbits], has_enable=True)(); o_reg.name = "o_reg"
      NEW: self.CommandFromClient = MessageQueue("o_reg", nbits=4)
    
      OLD: cmd = self.o_reg.O
      NEW: cmd = self.CommandFromClient.O

      OLD: self.o_reg.I             @= self.io.offer
      NEW: self.CommandFromClient.I @= self.io.offer

      OLD: self.o_reg.CE @= ((cur_state == State.MemOff) | (cur_state == State.MemOn))
      NEW: self.CommandFromClient.enable(cur_state, State.MemOff, State.MemOn)

    '''

    def __init__(self, name, nbits):
        self.Reg = m.Register(T=m.Bits[nbits], has_enable=True)()
        self.Reg.name = name

        self.I = self.Reg.I
        self.O = self.Reg.O

    def enable(self, cur_state, state, *more_states):
        cond = (cur_state == state)
        for s in more_states: cond = cond | (cur_state == s)
        # self.Reg.CE @= cond
        # q.enable(cond)
        self.Reg.CE @= cond

    def get(self): return self.Reg.O


class StateMachine(CoopGenerator):

    def _decl_attrs(self, **kwargs):
        super()._decl_attrs(**kwargs)
        self.num_states = State.num_states

    def _decl_io(self, **kwargs):
        super()._decl_io(**kwargs)
        self.io += m.IO(
            receive=m.In(m.Bits[16]),
            offer=m.In(m.Bits[4]),
            send=m.Out(m.Bits[16]),
            current_state=m.Out(m.Bits[2]),
        )

    def _decl_components(self, **kwargs):
        super()._decl_components(**kwargs)

        # state reg holds current state number
        self.state_reg = m.Register(
            init=m.Bits[State.nbits](0),
            has_enable=False,
        )()
        self.state_reg.name = "state_reg"

        # redundancy reg holds redundancy data from ?client? for future ref
        # self.redundancy_reg = reg("redundancy_reg", nbits=16); # "redundancy" reg
        self.redundancy_reg = m.Register(
            T=m.Bits[16],
            has_enable=True,
        )()
        self.redundancy_reg.name = "redundancy_reg"

        # Instead of registers to transfer info, now have message queues.
        # Coming soon: ready-valid protocol
        # 
        # Formerly o_reg, r_reg, and s_reg
        # Note: Redundancy info and address info both come in via DataFrom queue
        self.CommandFromClient = MessageQueue("CommandFromClient", nbits= 4);
        self.DataFromClient    = MessageQueue("DataFromClient",    nbits=16);
        self.DataToClient      = MessageQueue("DataToClient",      nbits=16);


    def _connect(self, **kwargs):
        super()._connect(**kwargs)
        self.io.current_state @= self.state_reg.O

        # Inputs
        self.DataFromClient.I    @= self.io.receive
        self.CommandFromClient.I @= self.io.offer

        # Outputs
        self.io.send             @= self.DataToClient.O
        
        # Enable registers *only* in states where regs are used (why?)
        cur_state = self.state_reg.O
        self.redundancy_reg.CE @= (cur_state == State.MemInit)

        # Enable queues *only* in states where queues are used (why?)
        # FIXME isn't r_reg also used in MemWrite and MemRead states? For address?
        cur_state = self.state_reg.O
        self.DataFromClient.enable(cur_state, State.MemInit)
        self.DataToClient.enable(cur_state, State.Send)
        self.CommandFromClient.enable(cur_state, State.MemOff, State.MemOn)

        # ==============================================================================
        # Note inline_combinational() is not very robust i.e. very particular
        # about indentation even on comments, also should avoid e.g. one-line
        # if-then ('if a: b=1'), multiple statements on one line separated by semicolon etc.

        @m.inline_combinational()
        def controller():

            addr_to_mem     = m.Bits[16](0) # changes on read, write request
            data_from_mem   = m.Bits[16](0) # magically changes when addr_to_mem changes
            data_to_client  = m.Bits[16](0)
            redundancy_data = m.Bits[16](0) # changes when we enter meminit state

            # Convenient shortcuts
            cur_state = self.state_reg.O
            cmd       = self.CommandFromClient.O

            # Dummy value for now
            WakeAcktT       = m.Bits[16](1)

            # Default is to stay in the same state as before
            next_state = cur_state

            # State MemInit
            if cur_state == State.MemInit:
                # Receive redundancy: output of receive reg => input of redundancy reg
                # redundancy_data = self.r_reg.O
                redundancy_data = self.DataFromClient.O
                next_state = State.MemOff

            # State MemOff
            elif cur_state == State.MemOff:
                c = self.CommandFromClient.get()

                # MemOff => MemOn on command PowerOn
                if (c == Command.PowerOn):
                    data_to_client = WakeAcktT
                    next_state = State.MemOn

                # MemOff => MemOff on command PowerOff
                # Why? By default we will stay in MemOff anyway...?
                # elif (c == Command.PowerOff): next_state = State.MemOff

            # State MemOn
            elif cur_state == State.MemOn:
                c = self.CommandFromClient.get()

                if c == Command.PowerOff:
                    next_state = State.MemOff

                # Why? By default we will stay in MemOn anyway...?
                # elif c == Command.Idle:
                #     next_state = State.MemOn

                # READ: get address from client, send back data from mem
                # Assumes data_from_mem magically appears when addr changes (I guess)
                elif c == Command.Read:

                    # addr_to_mem = self.r_reg.O     # Receive(Addr) [from client requesting read]
                    addr_to_mem = self.DataFromClient.O # Receive(Addr) [from client requesting read]

                    data_to_client = data_from_mem # Send(Data)    [to requesting client]
                    next_state = State.MemOn


                # WRITE: get address and data from client, send to memory
                # messages from client arrive via r_reg (receive reg)
                elif c == Command.Write:

                    # addr_to_mem = self.r_reg.O      # Receive(Addr) [from client requesting mem write]
                    addr_to_mem = self.DataFromClient.O # Receive(Addr) [from client requesting mem write]

                    # data = self.r_reg.O      # Receive(Data) [from client requesting mem write]
                    data = self.DataFromClient.O # Receive(Data) [from client requesting mem write]

                    next_state = State.MemOn

            # Wire up our shortcuts
            self.state_reg.I      @= next_state
            self.DataToClient.I   @= data_to_client
            self.redundancy_reg.I @= redundancy_data


def build_verilog():
    FSM = StateMachine()
    m.compile("steveri/tmpdir/fsm", FSM, output="coreir-verilog")

def show_verilog():
    with open('steveri/tmpdir/fsm.v', 'r') as f: print(f.read())

# build_verilog()

# show_verilog()
# print("==============================================================================")
# print("okay so that was the verilog")
# print("==============================================================================")

# print("TO TEST: cd blahblah; python test_state_machine.py or whatever


#==============================================================================
#==============================================================================
#==============================================================================
import fault
def test_state_machine_fault():
    
    debug("Build and test state machine")

    # Convenient little shortcut
    # - tester.step(1) is one clock edge
    # - mycycle() = one complete clock cycle = two clock edges (one pos, one neg)
    def cycle(): tester.step(2)

    def check_transition(cmd, state, ncycles=2):
        # Because "offer" is registered via "o_reg", takes two cycles to transition
        # Cy 1: offer => o_reg.O, next_state changes (current_state stays the same)
        # Cy 2: 'next_state' wire clocks into 'current_state' reg
        ncycles=2
        tester.circuit.offer = cmd

        # tester.print("beep boop begin: o_reg OUT = command %d\n",
        #              tester.circuit.o_reg.O)
        # tester.print("beep boop begin: current_state = state %d\n",
        #              tester.circuit.current_state)

        for i in range(ncycles):
            cycle()
            # cfmt=f"beep boop cy{i+1}: o_reg OUT = command %d\n"
            # tester.print(cfmt, tester.circuit.o_reg.O)
            # sfmt=f"beep boop cy{i+1}: current_state = state %d\n"
            # tester.print(sfmt, tester.circuit.current_state)

        tester.circuit.current_state.expect(state)


    # Tester setup
    Definition = StateMachine()
    tester = fault.Tester(Definition, Definition.CLK)
    tester.print("beep boop testing state_machine circuit\n")
    
    ########################################################################
    # Start in state MemInit
    tester.circuit.current_state.expect(State.MemInit)
    tester.print("beep boop -----------------------------------------------\n")
    tester.print("beep boop successfully booted in state MemInit maybe\n")
    tester.print("beep boop waiting for a single clock edge...\n")

    ########################################################################
    cycle()
    tester.print("beep boop -----------------------------------------------\n")
    tester.print("beep boop and now we should be in state Memoff\n")
    tester.circuit.current_state.expect(State.MemOff)

    # Check contents of redundancy_reg
    # For now, our circuit sets it to zero and we can check that
    # Later, it will be an unknown quantity supplied by the SRAM
    tester.print("beep boop received redundancy data '%d'\n", tester.circuit.redundancy_reg.O)
    tester.circuit.redundancy_reg.O.expect(0)
    tester.print("beep boop passed initial redundancy data check\n")

    ########################################################################
    tester.print("beep boop -----------------------------------------------\n")
    tester.print("beep boop Check transition MemOff => MemOff on command PowerOff\n")
    check_transition(Command.PowerOff, State.MemOff)
    tester.print("beep boop successfully arrived in state MemOff\n")

    ########################################################################
    tester.print("beep boop -----------------------------------------------\n")
    tester.print("beep boop Check transition MemOff => MemOn on command PowerOn\n")

    # FIXME why do we need two cycles (4 edges) for this transition?
    # I guess...one cycle for command to propagate from o_reg.I to o_reg.O
    # Plus one cycle for state to move from MemOff to MemOn...?
    check_transition(Command.PowerOn, State.MemOn, ncycles=2)
    tester.print("beep boop successfully arrived in state MemOn\n")

    ########################################################################
    tester.print("beep boop -----------------------------------------------\n")
    tester.print("beep boop Check transition MemOn => MemOn on command Idle\n")
    check_transition(Command.Idle, State.MemOn, ncycles=1)
    tester.print("beep boop successfully arrived in state MemOn\n")

    ########################################################################
    tester.print("beep boop -----------------------------------------------\n")
    tester.print("beep boop Check transition MemOn => MemOn on command Read\n")
    check_transition(Command.Read, State.MemOn, ncycles=1)
    tester.print("beep boop successfully arrived in state MemOn\n")

    ########################################################################
    tester.print("beep boop -----------------------------------------------\n")
    tester.print("beep boop Check transition MemOn => MemOn on command Write\n")
    check_transition(Command.Write, State.MemOn, ncycles=1)
    tester.print("beep boop successfully arrived in state MemOn\n")

    ########################################################################
    tester.print("beep boop -----------------------------------------------\n")
    tester.print("beep boop Check transition MemOn => MemOff on command PowerOff\n")
    check_transition(Command.PowerOff, State.MemOff, ncycles=2)
    tester.print("beep boop successfully arrived in state MemOff\n")


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

test_state_machine_fault()
