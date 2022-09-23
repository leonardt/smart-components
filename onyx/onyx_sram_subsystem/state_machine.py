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

# ORIGINAL
#                 ready_for_dfc = m.Bits[1](1)
#                 if self.DataFromClient.valid == m.Bits[1](1):
#                     redundancy_data = self.DataFromClient.data
#                     ready_for_dfc = m.Bits[1](0)
#                     next_state = State.MemOff

# PROTOTYPE
# @m.combinational2()
# def add(x: m.UInt[16], y: m.UInt[16]) -> m.UInt[16]:
#         return x + y

# WANT?
# (ready_for_dfc, redundancy_data, next_state) \
#     = rvget_and_go(self.DataFromClient, State.MemOff)

# @m.combinational2()
# def rvget_and_go(
#         q : RcvQueue,
#         goto_state : m.Bits[State.nbits],
# ) -> (
#     m.Bits[1],           # ready_out
#     m.Bits[16],          # data_out
#     m.Bits[State.nbits], # state_out
# ):
#     ready_for_dfc = m.Bits[1](1)
#     if q.valid == m.Bits[1](1):
#         data = q.data
#         ready_for_dfc = m.Bits[1](0)
#         next_state = State.MemOff
# 
#     return (ready_for_dfc, data, next_state)


#         ##############################################################################
#         @m.inline_combinational()
#         def rvget_and_go(
#                 q : RcvQueue,
#                 goto_state : m.Bits[State.nbits],
#         ) -> (
#             m.Bits[1],           # ready_out
#             m.Bits[16],          # data_out
#             m.Bits[State.nbits], # state_out
#         ):
#             ready_for_dfc = m.Bits[1](1)
#             if q.valid == m.Bits[1](1):
#                 data = q.data
#                 ready_for_dfc = m.Bits[1](0)
#                 next_state = State.MemOff
#                 
#             return (ready_for_dfc, data, next_state)

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

    # Convenience function; given a 'cur_state' wire and some states
    # (constants), enable the register ONLY when in those states
    # This probably builds terrible RTL, but with any luck the
    # downstream tools will optimize easily...
    def enable(self, cur_state, state, *more_states):
        cond = (cur_state == state)
        for s in more_states: cond = cond | (cur_state == s)
        self.Reg.CE @= cond

    def is_valid(self): return (self.valid == m.Bits[1](1))

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
    def __init__(self, name, nbits, data_out=None, valid_out=None, ready_in=None):
        Queue.__init__(self, name, nbits)

        # "They" control ready signal
        self.ready = self.ReadyReg.O

        # "We" control valid signal and data
        # (valid and data got to queue in-port)
        self.valid = self.ValidReg.I
        self.data  = self.Reg.O=I      # ??? was is loss '=I'

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

        # dfcq = "data-from-client queue" (i.e. receive)
        # dtcq = "data-to-client queue" (i.e. send)
        self.io += m.IO(
            receive=m.In(m.Bits[16]),
            receive_valid = m.In(m.Bits[1]),
            receive_ready = m.Out(m.Bits[1]),

            offer=m.In(m.Bits[4]),
            offer_valid = m.In(m.Bits[1]),
            offer_ready = m.Out(m.Bits[1]),

            send=m.Out(m.Bits[16]),
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
            ready_out = self.io.receive_ready
        );

        # OLD style comm (FIXME)
        # self.DataToClient = MessageQueue("DataToClient", nbits=16);
        self.DataToClient = Queue("DataToClient", nbits=16, readyvalid=False);

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
        self.io.send             @= self.DataToClient.O
        
        # Enable registers *only* in states where regs are used (why?)
        cur_state = self.state_reg.O
        self.redundancy_reg.CE @= (cur_state == State.MemInit)
        self.mem_addr_reg.CE   @= (cur_state == State.ReadAddr)


        # Enable queues *only* in states where queues are used (why?)
        # FIXME isn't DFC also used in MemWrite and MemRead states? For address?
        # Also DTC? FIXME Why is this working???
        cur_state = self.state_reg.O
        self.DataFromClient.enable(   cur_state, State.MemInit)
        self.DataToClient.enable(     cur_state, State.Send)
        self.CommandFromClient.enable(cur_state, State.MemOff, State.MemOn)

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

                if cfc.is_valid() & (cfc.data == Command.Read):

                    ready_for_cmd = ~READY                  # Got data, not yet ready for next command
                    next_state = State.ReadAddr

                    # These now belong to state Read Addr etc. (right???)
                    # addr_to_mem = dfc.data                  # Receive(Addr) [from client requesting read]
                    # data_to_client = data_from_mem          # Send(Data)    [to requesting client]



                # MemOn & Read => writemem & goto MemOff




                # WRITE: get address and data from client, send to memory
                # messages from client arrive via r_reg (receive reg)
                # Assumes DataFromClient magically chenges when read I guess...?
                elif cfc.data == Command.Write:
                    addr_to_mem = self.DataFromClient.get() # Receive(Addr) [from client requesting mem write]
                    data        = self.DataFromClient.get() # Receive(Data) [from client requesting mem write]
                    next_state = State.MemOn


            # State ReadAddr
            elif cur_state == State.ReadAddr:

                # Get read-address info from client/testbench
                # If successful, go to state ReadData

                ready_for_dfc = READY        # Ready for new data
                if dfc.is_valid():
                    addr_to_mem = dfc.data                  # Receive(Addr) [from client requesting read]
                    ready_for_dfc = ~READY   # Got data, not yet ready for next data
                    next_state = State.ReadData





            # Wire up our shortcuts
            self.state_reg.I      @= next_state
            self.redundancy_reg.I @= redundancy_data

            self.mem_addr_reg.I @= addr_to_mem


            # "to" MessageQueue inputs
            self.DataToClient.Reg.I @= data_to_client

            self.CommandFromClient.ready @= ready_for_cmd

            self.DataFromClient.ready @= ready_for_dfc






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

    def send_and_check_data(dval, reg_name, reg):
        
        # Send dval to MC receive-queue as redundancy data
        tester.circuit.receive = m.Bits[16](dval)

        # Mark receive-queue (dfc/DataFromQueue) data "valid"
        tester.print("beep boop ...sending valid signal\n")
        valid=1
        tester.circuit.receive_valid = m.Bits[1](valid)

        # FIXME should check "ready" signal before sending data

        # Wait one cycle for data-valid signal to propagate
        # After which valid signal and valid data should be avail on MC input regs
        tester.print("beep boop ...after one cy valid sig should be avail internally\n")
        cycle()
        tester.circuit.DataFromClient_valid.O.expect(valid)

        tester.print("beep boop ...one more cy to latch data and move to new state\n")
        # Wait one cycle MC to both 1) clock data into its internal reg
        # and 2) go to new state
        cycle()

        tester.print(f"beep boop received {reg_name} data '%d' == {dval} == 0x{dval:x}\n", reg.O)
        reg.O.expect(dval)
        tester.print(f"beep boop ...passed initial {reg_name} data check\n")

        tester.print("beep boop ...reset valid signal\n")
        valid=0
        tester.circuit.receive_valid = m.Bits[1](valid)


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

    # Send redundancy data, after which state should proceed to MemOff
    # Send "17" to MC receive-queue as redundancy data
    tester.circuit.receive = m.Bits[16](17)

    # Mark receive-queue (dfcq) data "valid"
    valid=1
    tester.circuit.receive_valid = m.Bits[1](valid)

    # FIXME should check "ready" signal before sending data

    # Wait one cycle for recundancy valid signal to propagate
    # After which valid signal and valid data should be avail on MC input regs
    tester.print("beep boop after one cy valid sig should be avail internally\n")
    cycle()
    tester.circuit.DataFromClient_valid.O.expect(valid)


    tester.circuit.receive = m.Bits[16](6)



    
    # Wait one cycle MC to both 1) clock data into its internal reg
    # and 2) go to new state (MemOff)
    cycle()


    tester.print("beep boop and now we should be in state Memoff\n")
    tester.circuit.current_state.expect(State.MemOff)
    tester.print("beep boop received redundancy data '%d' == 17 == 0x11\n", 
                 tester.circuit.redundancy_reg.O)
    tester.circuit.redundancy_reg.O.expect(17)
    tester.print("beep boop passed initial redundancy data check\n")


    valid=0
    tester.circuit.receive_valid = m.Bits[1](valid)



    ########################################################################
    cycle()
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
    tester.print("beep boop -----------------------------------------------\n")
    tester.print("beep boop Check receive mem addr '6'\n")

    # Send mem_addr data, after which state should proceed to MemOff
    send_and_check_data(6, "mem_addr", tester.circuit.mem_addr_reg)

    ########################################################################
    tester.print("beep boop -----------------------------------------------\n")
    tester.print("beep boop Verify arrival in state ReadData\n")
    tester.circuit.current_state.expect(State.ReadData)
    tester.print("beep boop ...CORRECT!\n")










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

#                 queue = self.DataFromClient
#                 ready = ready_for_dfc
#                 valid = queue.valid
#                 data = queue.data
#                 move_on = State.MemOff
# 
#                 ready = m.Bits[1](1)
#                 if valid == m.Bits[1](1):
#                     redundancy_data = data
#                     ready = m.Bits[1](0)
#                     next_state = move_on
# 

#         @m.circuit.combinational
#         def basic_if(I: m.Bits[2], S:m.Bit) -> m.Bit:
#             if S:
#                 return I[0]
#             else:
#                 return I[1]


#         @m.circuit.combinational
#         def rvget_and_go(
#                 valid : m.Bits[1],
#                 # ----------------------------------------
#                 cur_data  : m.Bits[16],
#                 cur_state : m.Bits[State.nbits],
#                 # ----------------------------------------
#                 data       : m.Bits[16],
#                 goto_state : m.Bits[State.nbits],
#                 # ----------------------------------------
#         ) -> (
#             m.Bits[16],                 # data_out
#             m.Bits[State.nbits],        # next_state
#             m.Bits[1]                   # ready_out
#         ):
#             ready = m.Bits[1](1)
#             if valid:
#                 return (data, goto_state, ~ready)
#             else:
#                 return (cur_data, cur_state, ready)

#         def foo():
#             ready_for_dfc = m.Bits[1](1)
# 
#         def bar():
#                 # ValueError: Converting non-constant magma bit to bool not supported
#                 # if self.DataFromClient.valid == m.Bits[1](1):
# 
#                     # Then grab it and move on (else will remain in same state)
#                     ready_for_dfc = m.Bits[1](0)
#                     return (self.DataFromClient.data,State.MemOff)
# 

                # (redundancy_data, next_state, ready_for_dfc)=rvget_and_go(
                #     dfc.valid,
                #     cur_data, cur_state,
                #     dfc.data, goto_state,
                # )



#                                 # Cut'n'paste
# 
#                 # if valid, redundancy_datay = new data from dfc queue
#                 redundancy_data = rvgetd(v, cur_data, self.DataFromClient.data)
# 
#                 # if valid, next_state = goto_state
#                 next_state      = rvgets(v, cur_state, goto_state)
# 
#                 # if valid, reset ready=0, else set ready=1
#                 ready_for_dfc   = rvgetr(v)
# 



#         ########################################################################
#         # Utilities for dealing with ready-valid protocol
# 
#         # If data valid and command correct, fetch 
# 
# 
#         # If data valid, fetch new data
#         dataT = m.Bits[16]
#         @m.circuit.combinational
#         def rvgetd(
#                 valid     : m.Bits[1],
#                 cur_data  : dataT,
#                 new_data  : dataT) -> m.Bits[16]:
#             #------------------------
#             if valid: return new_data
#             else:     return cur_data
# 
# 
#         # If data valid, go to new state
#         stateT = m.Bits[State.nbits]
#         @m.circuit.combinational
#         def rvgets(
#                 valid      : m.Bits[1],
#                 cur_state  : stateT,
#                 goto_state : stateT,
#         ) -> m.Bits[State.nbits]:
#             #--------------------------
#             if valid: return goto_state
#             else:     return cur_state
# 
#         # If data valid, reset ready signal
#         @m.circuit.combinational
#         def rvgetr(valid : m.Bits[1]) -> m.Bits[1]:
#             ready = m.Bits[1](1)
#             if valid: return ~ready  # Got data, not yet ready for new data
#             else:     return  ready  # Want data but not got data yet, keep signaling "ready"
# 
#         ########################################################################




