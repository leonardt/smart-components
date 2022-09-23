# TODO NEXT
# - continue scrubbing the state machine i guess


##############################################################################
README='''

# Also see README.txt

# To see state machine diagram:
    display state_machine3.png

# To automatically run, see output, and compare to prev
    ./test_state_machine.sh

# To run state machine
    python state_machine.py

# To see output from state machine run
    cat tmpdir/obj_dir/StateMachine.log | sed 's/beep/\
beep/g'

# To compare state machine verilog vs. prev successful run(s)
    diff ref/StateMachine.v tmpdir/StateMachine.v && echo PASS || echo FAIL
'''
##############################################################################

DBG=True
if DBG:
    import sys
    def debug(m):
        print(m); sys.stdout.flush()
else:
    def debug(m): pass

#------------------------------------------------------------------------
debug("Begin importing python packages...")
import sys
import magma as m
import hwtypes as ht
from mock_mem import SRAMDMR
from session import Offer, Choose, Send, Recieve, Sequence
from session import SessionTypeVisitor, SessionT, LabelT
from util import inverse_look_up, BiMap
debug("* Done importing python packages...")

#------------------------------------------------------------------------
# 2K SRAM where e.g. SRAM[13] = 10013; SRAM[2047] = 12047;
SRAM=[]
for i in range(2048): SRAM.append(i+10000)
assert SRAM[2047] == 12047

#------------------------------------------------------------------------
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
    num_states = 7; i=0
    nbits = (num_states-1).bit_length()
    #----------------------------------
    MemInit  = m.Bits[nbits](i); i=i+1
    MemOff   = m.Bits[nbits](i); i=i+1
    Send     = m.Bits[nbits](i); i=i+1 # currently unused maybe
    MemOn    = m.Bits[nbits](i); i=i+1
    ReadAddr = m.Bits[nbits](i); i=i+1 # currently unused maybe
    ReadData = m.Bits[nbits](i); i=i+1 # currently unused maybe
    Write    = m.Bits[nbits](i); i=i+1 # currently unused maybe



class Queue():
    '''A way to pass messages between ourself and others. Depending on
    which way you want to go, you'll use one of the subclasses
    'RcvQueue' or 'XmtQueue', see below for details.
    '''

    # def __init__(self, name, nbits, port=None):
    def __init__(self, name, nbits, readyvalid=True):
        self.Reg = m.Register(T=m.Bits[nbits], has_enable=True)()
        self.Reg.name = name    ; # E.g. "DataFromClient"

        if readyvalid:
            # Initialize to not ready, not valid
            self.ReadyReg = m.Register(T=m.Bits[1], has_enable=False, init=m.Bits[1](0))()
            self.ReadyReg.name = name+"_ready" ; # E.g. "DataFromClient_ready"
            
            
            self.ValidReg = m.Register(T=m.Bits[1], has_enable=False, init=m.Bits[1](0))()
            self.ValidReg.name = name+"_valid" ; # E.g. "DataFromClient_valid"

        self.I = self.Reg.I
        self.O = self.Reg.O

        # if port != None: self.Reg.I @= port

    # Convenience function; given a 'state_reg' wire and some states
    # (constants), enable the register ONLY when in those states
    # This probably builds terrible RTL, but with any luck the
    # downstream tools will optimize easily...
    def enable(self, state_reg, state, *more_states):
        cond = (state_reg == state)
        for s in more_states: cond = cond | (state_reg == s)
        self.Reg.CE @= cond

    def is_valid(self): return (self.valid == m.Bits[1](1))
    def is_ready(self): return (self.ready == m.Bits[1](1))

    # Backward compatibility (TEMPORARY)
    # Until everyone is on board with R/V, use this for backward compatibility
    def get(self): return self.Reg.O


class RcvQueue(Queue):
    '''
    Supplies the basic signals for receiving data from a ready-valid port:
        RcvQueue.data  = RcvQueue.Reg.O = data from the queue
        RcvQueue.ready = RcvQueue.ReadyReg.I = tells the queue we are ready for data
        RcvQueue.valid = RcvQueue.ValidReg.O = queue tells us when data is available

    Sample usage:

       # Instantiate a transmit queue and tell it what signals
       # client will use for communication
       
       DataFromClient = RcvQueue("DataFromClient", nbits=16,
           data_in   = self.io.receive,
           valid_in  = self.io.receive_valid,
           ready_out = self.io.receive_ready
           );

       # To read data from queue:
       
       # 1. Set ready bit for queue to show that we are ready for data.
       DataFromClient.ready @= ready_for_dfc
       ready_for_dfc = m.Bits[1](1)

       # 2. Check the valid bit. Grab data iff valid is true.
       if DataFromClient.valid == m.Bits[1](1): data = DataFromClient.data

    '''
    # set ReadyValid TRUE to use readyvalid protocol, otherwise it's just a register
    def __init__(self, name, nbits, readyvalid=False, data_in=None, valid_in=None, ready_out=None):
        Queue.__init__(self, name, nbits, readyvalid)

        # "We" control ready signal
        if readyvalid: self.ready = self.ReadyReg.I

        # "They" control valid signal and data
        # (valid and data come from queue out-port)
        if readyvalid: self.valid = self.ValidReg.O
        self.data  = self.Reg.O

        # Connect the ports for data, ready, valid to/from client
        if data_in:   self.Reg.I      @= data_in
        if valid_in:  self.ValidReg.I @= valid_in
        if ready_out: ready_out       @= self.ReadyReg.O




# TODO Not plugged in yet
class XmtQueue(Queue):
    '''
    Supplies the basic signals for sending data to a ready-valid port:
        XmtQueue.data  = XmtQueue.Reg.O = data from the queue
        XmtQueue.ready = XmtQueue.ReadyReg.I = tells the queue we are ready for data
        XmtQueue.valid = XmtQueue.ValidReg.O = queue tells us when data is available

    Sample usage:

       # Instantiate a transmit queue and tell it what signals
       # client will use for communication
       
       DataToClient = XmtQueue("DataToClient", nbits=16,
           data_out  = self.io.send,
           valid_out = self.io.dtcq_valid,
           ready_in  = self.io.dtcq_ready
           );

       # To send data to queue:
       
       # 1. Set the valid bit and write the data to the queue
       dtcq_valid = m.Bits[1](1)
       DataToClient.data = m.Bits[16](0x1234)

       # 2. Wait for ready bit to show that data has been collected
       while DataFromClient.ready != m.Bits[1](1): wait()

    '''
    # set ReadyValid TRUE to use readyvalid protocol, otherwise it's just a register
    def __init__(self, name, nbits, readyvalid=False, data_out=None, valid_out=None, ready_in=None):
        Queue.__init__(self, name, nbits, readyvalid)

        # "They" control ready signal
        if readyvalid: self.ready = self.ReadyReg.O

        # "We" control valid signal and data
        # (valid and data got to queue in-port)
        if readyvalid: self.valid = self.ValidReg.I
        self.data  = self.Reg.I

        # Connect the ports for data, ready, valid to/from client
        if data_out: data_out        @= self.Reg.O
        if valid_out: valid_out      @= self.ValidReg.O
        if ready_in: self.ReadyReg.I @= ready_in

        # self.Reg.I      @= data_in
        # self.ValidReg.I @= valid_in
        # ready_out       @= self.ReadyReg.O

    # Backward compatibility for now, will delete soon
    def get(self): return self.Reg.O


# Deprecated simple register interface w/o ready/valid
# to be deleted after code has been updated
class MessageQueue():
    '''
    Examples:
      OLD: o_reg = m.Register(T=m.Bits[nbits], has_enable=True)(); o_reg.name = "o_reg"
      NEW: self.CommandFromClient = MessageQueue("o_reg", nbits=4)
    
      OLD: cmd = self.o_reg.O
      NEW: cmd = self.CommandFromClient.O

      OLD: self.o_reg.I             @= self.io.offer
      NEW: self.CommandFromClient.I @= self.io.offer

      OLD: self.o_reg.CE @= ((state_reg == State.MemOff) | (state_reg == State.MemOn))
      NEW: self.CommandFromClient.enable(state_reg, State.MemOff, State.MemOn)

    '''

    def __init__(self, name, nbits):
        self.Reg = m.Register(T=m.Bits[nbits], has_enable=True)()
        self.Reg.name = name

        self.I = self.Reg.I
        self.O = self.Reg.O

    def enable(self, state_reg, state, *more_states):
        cond = (state_reg == state)
        for s in more_states: cond = cond | (state_reg == s)
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

        # dfcq = "data-from-client queue" (i.e. receive)
        # dtcq = "data-to-client queue" (i.e. send)
        self.io += m.IO(
            receive       = m.In(m.Bits[16]),
            receive_valid = m.In(m.Bits[ 1]),
            receive_ready = m.Out(m.Bits[1]),

            offer       = m.In(m.Bits[4]),
            offer_valid = m.In(m.Bits[1]),
            offer_ready = m.Out(m.Bits[1]),

            send       = m.Out(m.Bits[16]),
            send_ready = m.In(m.Bits[1]),
            send_valid = m.Out(m.Bits[1]),
            # dtcq_valid = m.In(m.Bits[1]),  TBD
            # dtcq_ready = m.Out(m.Bits[1]), TBD

            current_state=m.Out(m.Bits[State.nbits]),
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


        # mem_addr reg holds mem_addr data from ?client? for future ref
        # self.mem_addr_reg = reg("mem_addr_reg", nbits=16); # "mem_addr" reg
        self.mem_addr_reg = m.Register(
            T=m.Bits[16],
            has_enable=True,
        )()
        self.mem_addr_reg.name = "mem_addr_reg"




        # Instead of registers to transfer info, now have message queues.
        # Coming soon: ready-valid protocol
        # 
        # Formerly registers o_reg, r_reg, and s_reg
        # Now ready/valid queues CommandFromClient, DataFromClient, DataToClient

        # Note: Redundancy info and address info both come in via DFC queue

        # MessageQueue == register DEPRECATED, instead want
        # RcvQueue = "receive" queue w/ ready-valid protocol
        # XmtQueue = "send" queue w/ ready-valid protocol

        # OLD style MessageQueue comm (FIXME)
        # self.CommandFromClient = MessageQueue("CommandFromClient", nbits= 4);
        self.CommandFromClient = RcvQueue(
            "CommandFromClient", nbits=4, readyvalid=True,
            data_in   = self.io.offer,
            valid_in  = self.io.offer_valid,
            ready_out = self.io.offer_ready
        );

        # NEW style comm
        self.DataFromClient = RcvQueue(
            "DataFromClient", nbits=16, readyvalid=True,
            data_in   = self.io.receive,
            valid_in  = self.io.receive_valid,
            ready_out = self.io.receive_ready,
        );

        # OLD style comm (FIXME)
        # self.DataToClient = MessageQueue("DataToClient", nbits=16);
        # self.DataToClient = Queue("DataToClient", nbits=16, readyvalid=False);

        self.DataToClient = XmtQueue(
            "DataToClient", nbits=16, readyvalid=True,
            ready_in  = self.io.send_ready,
            valid_out = self.io.send_valid,
            data_out  = self.io.send,
        );



    def _connect(self, **kwargs):
        super()._connect(**kwargs)
        self.io.current_state @= self.state_reg.O

        # Inputs (old style)
        # self.CommandFromClient.I @= self.io.offer

        # Inputs (not needed w/ new style)
        # self.DataFromClient.I           @= self.io.receive
        # self.DataFromClient.ValidReg.I  @= self.io.receive_valid
        # self.io.receive_ready              @= self.DataFromClient.ReadyReg.O

        # Outputs (old style)
        # self.io.send             @= self.DataToClient.O
        
        # Enable registers *only* in states where regs are used (why?)
        state_reg = self.state_reg.O
        self.redundancy_reg.CE @= (state_reg == State.MemInit)
        self.mem_addr_reg.CE   @= (state_reg == State.ReadAddr)


        # Enable queues *only* in states where queues are used (why?)
        # FIXME isn't DFC also used in MemWrite and MemRead states? For address?
        # Also DTC? FIXME Why is this working???
        self.DataFromClient.enable(state_reg, 
            State.MemInit, State.ReadAddr, State.Write
        )
        self.DataToClient.enable(     state_reg, State.Send, State.ReadData)
        self.CommandFromClient.enable(state_reg, State.MemOff, State.MemOn)

        # ==============================================================================
        # Note inline_combinational() is not very robust i.e. very particular
        # about indentation even on comments, also should avoid e.g. one-line
        # if-then ('if a: b=1'), multiple statements on one line separated by semicolon etc.

        @m.inline_combinational()
        def controller():

            addr_to_mem     = m.Bits[16](13) # changes on read, write request
            data_from_mem   = m.Bits[16](13) # magically changes when addr_to_mem changes
            data_to_client  = m.Bits[16](13)
            redundancy_data = m.Bits[16](13) # changes when we enter meminit state

            # Convenient shortcuts
            cur_state = self.state_reg.O

            # Dummy value for now
            WakeAcktT       = m.Bits[16](1)

            # Default is to stay in the same state as before
            next_state = cur_state
                
            # FIXME make sure all ready/valids initialize to ZERO (init= in Queue)

            ##############################################################################
            # NOT HERE
            # # Reset all ready-valid signals that we control.
            # # self.DataFromClient.ready = m.Bits[1](0); # Not ready for input from client
            # # self.DataFromClient.ReadyReg.I = m.Bits[1](0); # Not ready for input from client

            # FIXME need a dfcq_ready but not here
            # FIXME dfc_ready => dfcq_ready or maybe vice-versa? 'ready' implies 'q'?
            # ready_for_dfc = m.Bits[1](0)
            ##############################################################################


            READY = m.Bits[1](1)
            ready_for_dfc = ~READY
            ready_for_cmd = ~READY

            cfc = self.CommandFromClient
            dfc = self.DataFromClient

            # State 'MemInit'
            if cur_state == State.MemInit:

                # Get redundancy info from client/testbench
                # If successful, go to goto_state

                # Setup
                goto_state = State.MemOff    # Go to this state when/if successful
                ready_for_dfc = READY        # Ready for new data

                if dfc.is_valid():
                    redundancy_data = dfc.data
                    ready_for_dfc = ~READY   # Got data, not yet ready for next data
                    next_state = goto_state


            # State MemOff
            elif cur_state == State.MemOff:

                # MemOff * PowerOn => goto MemOn

                ready_for_cmd = READY
                if cfc.is_valid() & (cfc.data == Command.PowerOn):
                    data_to_client = WakeAcktT
                    ready_for_cmd = ~READY     # Got data, not yet ready for next command
                    next_state = State.MemOn

                # State diagram says MemOff => MemOff on command PowerOff
                # But. Why? By default we will stay in MemOff anyway...?
                # elif (c == Command.PowerOff): next_state = State.MemOff
                # FIXME will client freak out if no ack from PowerOff command? grumble grumble


            # State MemOn
            elif cur_state == State.MemOn:

                ready_for_cmd = READY

                # MemOn & PowerOff => goto MemOff

                if cfc.is_valid() & (cfc.data == Command.PowerOff):
                    ready_for_cmd = ~READY     # Got data, not yet ready for next command
                    next_state = State.MemOff




                # TODO oops time for new state diagram innit

                # MemOn & Read => readmem & goto ReadAddr
                # 
                # READ: get address from client, send back data from mem
                # Assumes data_from_mem magically appears when addr changes (I guess)

                elif cfc.is_valid() & (cfc.data == Command.Read):

                    ready_for_cmd = ~READY                  # Got data, not yet ready for next command
                    next_state = State.ReadAddr


                # MemOn & Read => writemem & goto MemOff

                # # WRITE: get address and data from client, send to memory
                # # messages from client arrive via r_reg (receive reg)
                # # Assumes DataFromClient magically chenges when read I guess...?
                # elif cfc.data == Command.Write:
                #     addr_to_mem = self.DataFromClient.get() # Receive(Addr) [from client requesting mem write]
                #     data        = self.DataFromClient.get() # Receive(Data) [from client requesting mem write]
                #     next_state = State.MemOn


                elif cfc.is_valid() & (cfc.data == Command.Write):
                    ready_for_cmd = ~READY                  # Got data, not yet ready for next command
                    next_state = State.Write




            # State ReadAddr
            elif cur_state == State.ReadAddr:

                # Get read-address info from client/testbench
                # If successful, go to state ReadData

                ready_for_dfc = READY        # Ready for new data
                if dfc.is_valid():
                    addr_to_mem = dfc.data                  # Receive(Addr) [from client requesting read]
                    ready_for_dfc = ~READY   # Got data, not yet ready for next data
                    next_state = State.ReadData


            # bookmark working on readdata
            # State ReadData
            elif cur_state == State.ReadData:
                dtc_data_valid = m.Bits[1](1)

                # post valid data
                VALID = m.Bits[1](1)
                data_to_client = m.Bits[16](10066)
                dtc_data_valid = VALID

                # dtc READY means they got the data and we can all move on
                if self.DataToClient.is_ready():
                    dtc_dta_valid = ~VALID
                    next_state = State.MemOn



            # State Write



            # Wire up our shortcuts
            self.state_reg.I      @= next_state
            self.redundancy_reg.I @= redundancy_data

            self.mem_addr_reg.I @= addr_to_mem


            # "to" MessageQueue inputs
            self.DataToClient.Reg.I @= data_to_client

            self.CommandFromClient.ready @= ready_for_cmd

            self.DataFromClient.ready @= ready_for_dfc

            self.DataToClient.valid @= dtc_data_valid





def build_verilog():
    FSM = StateMachine()
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
def test_state_machine_fault():
    
    debug("Build and test state machine")

    # Convenient little shortcut
    # - tester.step(1) is one clock edge
    # - cycle(1) = one complete clock cycle = two clock edges (one pos, one neg)
    def cycle(n=1): tester.step(2*n)

    def check_transition(cmd, state):

        # FIXME should check "ready" signal before sending data
        # something like...? 'while tester.circuit.offer_ready != 1: cycle()'

        # successfully fails when/if valid=0
        valid=1
        tester.circuit.offer = cmd
        tester.circuit.offer_valid = m.Bits[1](valid)

        # Because "offer" is registered, it takes two cycles to transition
        # Cy 1: offer => reg, next_state changes (current_state stays the same)
        # Cy 2: 'next_state' wire clocks into 'current_state' reg
        # One cycle = two tester steps
        cycle(2)

        # Verify arrival at desired state
        tester.circuit.current_state.expect(state)

    def send_and_check_dfc_data(dval, reg_name, reg):

        # Send dval to MC receive-queue as "DataFromClient" data
        tester.print("beep boop ...sending data to controller\n")
        tester.circuit.receive = m.Bits[16](dval)

        # Mark receive-queue (dfc/DataFromQueue) data "valid"
        tester.print("beep boop ...sending valid signal\n")
        VALID = 1
        tester.circuit.receive_valid = VALID

        # FIXME should check "ready" signal before sending data

        # Wait one cycle for valid signal to propagate
        # After which valid signal and valid data should be avail on MC input regs
        tester.print("beep boop ...after one cy valid sig should be avail internally\n")
        cycle()
        tester.circuit.DataFromClient_valid.O.expect(VALID)

        # Sanity check of reg-enable signal
        tester.print("beep boop ...CE better be active (CE=1)\n")
        tester.circuit.DataFromClient.CE.expect(1)

        # Reset valid signal
        tester.print("beep boop ...reset valid signal\n")
        tester.circuit.receive_valid = ~VALID

        # Wait one cycle MC to clock data in, and goto new state
        tester.print("beep boop ...one more cy to latch data and move to new state\n")
        cycle()

        # Check latched data for correctness
        msg = f"MC received {reg_name} data '%d' ==? {dval} (0x{dval:x})"
        tester.print(f"beep boop {msg}\n", reg.O)
        reg.O.expect(dval)
        tester.print(f"beep boop ...yes! passed initial {reg_name} data check\n")


    def get_and_check_dtc_data(dval):
        READY=1; VALID=1

        # Tell MC that we are ready to read the data
        tester.print("beep boop ...sending ready signal\n")
        tester.circuit.send_ready = READY

        # Wait one cycle for ready signal to propagate
        # After which ready signal and valid data should be avail on MC input regs
        tester.print("beep boop ...after one cy ready sig should be avail internally\n")
        cycle()
        tester.circuit.DataToClient_ready.O.expect(READY)

        # Wait for MC to signal valid data
        tester.circuit.send_valid.expect(READY)
        tester.print("beep boop ...found send_valid TRUE...\n")


        # See what we got
        tester.print("beep boop ...expecting to get 10066\n")
        tester.circuit.DataToClient.O.expect(10066)
        

        # Check latched data for correctness
        reg = tester.circuit.DataToClient
        msg = f"MC sent us data '%d' ==? {dval} (0x{dval:x})"
        tester.print(f"beep boop {msg}\n",  reg.O)
        reg.O.expect(dval)
        tester.print(f"beep boop ...yes! passed data check\n")


    ########################################################################
    # Tester setup
    Definition = StateMachine()
    tester = fault.Tester(Definition, Definition.CLK)
    tester.print("beep boop testing state_machine circuit\n")

    tester.print("beep boop tester data not valid yet so setting dfc valid=0\n");
    tester.circuit.receive_valid  = m.Bits[1](0)

    tester.print("beep boop offer not valid yet so setting offer_valid=0\n");
    tester.circuit.offer_valid = m.Bits[1](0)

    ########################################################################
    # Expect to start in state MemInit
    tester.circuit.current_state.expect(State.MemInit)
    tester.print("beep boop -----------------------------------------------\n")
    tester.print("beep boop 0 successfully booted in state MemInit maybe\n")
    tester.print("beep boop sending redundancy data to MC\n")

    ########################################################################
    rdata = 17
    tester.print("beep boop -----------------------------------------------\n")
    tester.print(f"beep boop Check that MC received redundancy data '{rdata}'\n")
    send_and_check_dfc_data(17, "redundancy", tester.circuit.redundancy_reg)

    ########################################################################
    tester.print("beep boop -----------------------------------------------\n")
    tester.print("beep boop and now we should be in state Memoff\n")
    tester.circuit.current_state.expect(State.MemOff)

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
    check_transition(Command.PowerOn, State.MemOn)
    tester.print("beep boop successfully arrived in state MemOn\n")

    ########################################################################
    tester.print("beep boop -----------------------------------------------\n")
    tester.print("beep boop Check transition MemOn => MemOn on command Idle\n")
    check_transition(Command.Idle, State.MemOn)
    tester.print("beep boop successfully arrived in state MemOn\n")


    ########################################################################
    tester.print("beep boop -----------------------------------------------\n")
    tester.print("beep boop Check transition MemOn => MemOff on command PowerOff\n")
    check_transition(Command.PowerOff, State.MemOff)
    tester.print("beep boop successfully arrived in state MemOff\n")

    ########################################################################
    tester.print("beep boop -----------------------------------------------\n")
    tester.print("beep boop Check transition MemOff => MemOn on command PowerOn\n")
    check_transition(Command.PowerOn, State.MemOn)
    tester.print("beep boop successfully arrived in state MemOn\n")

    ########################################################################
    tester.print("beep boop -----------------------------------------------\n")
    tester.print("beep boop Check transition MemOn => ReadAddr on command Read\n")
    check_transition(Command.Read, State.ReadAddr)
    tester.print("beep boop successfully arrived in state ReadAddr\n")

    ########################################################################
    maddr = 66
    tester.print("beep boop -----------------------------------------------\n")
    tester.print(f"beep boop Check that MC received mem addr '{maddr}'\n")

    # Send mem_addr data, after which state should proceed to MemOff
    send_and_check_dfc_data(maddr, "mem_addr", tester.circuit.mem_addr_reg)
        
    ########################################################################
    tester.print("beep boop -----------------------------------------------\n")
    tester.print("beep boop Verify arrival in state ReadData\n")
    tester.circuit.current_state.expect(State.ReadData)
    tester.print("beep boop ...CORRECT!\n")

    ########################################################################
    wantdata = 10066
    tester.print("beep boop -----------------------------------------------\n")
    tester.print(f"beep boop Check that MC sent data '{wantdata}'\n")

    get_and_check_dtc_data(10066)



# bookmark
##############################################################################
##############################################################################
##############################################################################


#     ########################################################################
#     tester.print("beep boop -----------------------------------------------\n")
#     tester.print("beep boop Check transition ReadAddr => ReadData\n")
#     check_transition(Command.Read, State.ReadAddr)
#     tester.print("beep boop successfully arrived in state ReadAddr\n")

    # ########################################################################
    # tester.print("beep boop -----------------------------------------------\n")
    # tester.print("beep boop Check transition MemOn => MemOn on command Write\n")
    # check_transition(Command.Write, State.MemOn)
    # tester.print("beep boop successfully arrived in state MemOn\n")



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

