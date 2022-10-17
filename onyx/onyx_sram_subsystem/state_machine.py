##############################################################################
README='''

# Also see README.txt

# To see state machine diagram:
    display state_machine.png

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
########################################################################
# FIXME can use logger
DBG=True
if DBG:
    def debug(m):
        print(m, flush=True)
else:
    def debug(m): pass

#------------------------------------------------------------------------
debug("Begin importing python packages...")
import sys
import magma as m
import hwtypes as hw
debug("* Done importing python packages...")





#------------------------------------------------------------------------
# State Machine generator setup

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

# FIXME can use enum

# >>> from enum import Enum
# >>> class foo(Enum):
# >>> class foo(Enum):
# ...   e1=m.Bits[1](1)
# ... 
# >>> foo.e1
# <foo.e1: Bits[1](1)>

class Command():
    #----------------------------------
    num_commands = 6; i=0
    nbits = (num_commands-1).bit_length()
    #----------------------------------
    NoCommand= m.Bits[nbits](i); i=i+1
    PowerOff = m.Bits[nbits](i); i=i+1
    PowerOn  = m.Bits[nbits](i); i=i+1 # not used
    Read     = m.Bits[nbits](i); i=i+1
    Write    = m.Bits[nbits](i); i=i+1
    Idle     = m.Bits[nbits](i); i=i+1

class Action():
    #----------------------------------
    num_actions = 7; i=0
    nbits = (num_actions-1).bit_length()
    #----------------------------------
    NoAction      = m.Bits[nbits](i); i=i+1
    GetCommand    = m.Bits[nbits](i); i=i+1
    GetRedundancy = m.Bits[nbits](i); i=i+1
    SendAck       = m.Bits[nbits](i); i=i+1
    GetAddr       = m.Bits[nbits](i); i=i+1
    ReadData      = m.Bits[nbits](i); i=i+1
    WriteData     = m.Bits[nbits](i); i=i+1

class State():
    #----------------------------------
    num_states = 7; i=0
    nbits = (num_states-1).bit_length()
    #----------------------------------
    MemInit   = m.Bits[nbits](i); i=i+1 # 0
    MemOff    = m.Bits[nbits](i); i=i+1 # 1
    SendAck   = m.Bits[nbits](i); i=i+1 # 2 UNUSED???
    MemOn     = m.Bits[nbits](i); i=i+1 # 3
    ReadAddr  = m.Bits[nbits](i); i=i+1 # 4
    ReadData  = m.Bits[nbits](i); i=i+1 # 5
    WriteAddr = m.Bits[nbits](i); i=i+1 # 6
    WriteData = m.Bits[nbits](i); i=i+1 # 7

##############################################################################
# begin side quest

# Example of input to build_dot_graph:
# mygraph_string = '''
#     (State.MemInit,  ACTION,  Action.GetRedundancy, State.MemOff),
#     (State.MemOff,   COMMAND, Command.PowerOn,      State.SendAck),
#     (State.MemOn,     COMMAND, Command.PowerOff,    State.MemOff),
#     (State.MemOn,     COMMAND, Command.Read,        State.ReadAddr),
#     (State.MemOn,     COMMAND, Command.Write,       State.WriteAddr),
#     (State.SendAck,   ACTION,  Action.SendAck,      State.MemOn),
#     (State.ReadAddr,  ACTION,  Action.GetAddr,      State.ReadData),
#     (State.WriteAddr, ACTION,  Action.GetAddr,      State.WriteData),
#     (State.WriteData, ACTION,  Action.WriteData,    State.MemOn),
#     (State.ReadData,  ACTION,  Action.ReadData,     State.MemOn),
# '''

def build_dot_graph(graph):
    '''
    # Example: build_dot_graph(mygraph_string) =>
    # 
    #     digraph Diagram { node [shape=box];
    #       "MemInit"   -> "MemOff"    [label="GetRedundancy()"];
    #       "MemOff"    -> "SendAck"   [label="PowerOn"];
    #       "MemOn"     -> "MemOff"    [label="PowerOff"];
    #       "MemOn"     -> "ReadAddr"  [label="Read"];
    #       "MemOn"     -> "WriteAddr" [label="Write"];
    #       "SendAck"   -> "MemOn"     [label="SendAck()"];
    #       "ReadAddr"  -> "ReadData"  [label="GetAddr()"];
    #       "WriteAddr" -> "WriteData" [label="GetAddr()"];
    #       "WriteData" -> "MemOn"     [label="WriteData()"];
    #       "ReadData"  -> "MemOn"     [label="ReadData()"];
    #     }
    '''
    def quote(word): return '"' + word + '"'
    print('digraph Diagram { node [shape=box];')
    for line in graph.split("\n"):
        words = line.split()
        if not words: continue
        from_state = words[0][7:-1]
        ac = words[1]
        if (ac == "ACTION,"): label = words[2][7:-1] + "()"
        else:                 label = words[2][8:-1]
        to_state = words[3][6:-2]
        print(f'  {quote(from_state):11} -> {quote(to_state):11} [label={quote(label)}];')
    print('}\n')

# end side quest
##############################################################################


# Example of input to StateMachineGraph():
# 
# mygraph = (
#     (State.MemInit,   ACTION,  Action.GetRedundancy, State.MemOff),
#     (State.MemOff,    COMMAND, Command.PowerOn,      State.SendAck),
#     (State.MemOn,     COMMAND, Command.PowerOff,     State.MemOff),
#     (State.MemOn,     COMMAND, Command.Read,         State.ReadAddr),
#     (State.MemOn,     COMMAND, Command.Write,        State.WriteAddr),
#     (State.SendAck,   ACTION,  Action.SendAck,       State.MemOn),
#     (State.ReadAddr,  ACTION,  Action.GetAddr,       State.ReadData),
#     (State.WriteAddr, ACTION,  Action.GetAddr,       State.WriteData),
#     (State.WriteData, ACTION,  Action.WriteData,     State.MemOn),
#     (State.ReadData,  ACTION,  Action.ReadData,      State.MemOn),
# )



# To test/break, can replace e.g.
# <   (State.MemOff,  COMMAND, Command.PowerOn,      State.SendAck),
# >   (State.MemOff,  COMMAND, Command.PowerOn,      State.MemOff),


ACTION  = m.Bits[1](0)
COMMAND = m.Bits[1](1)

class StateMachineGraph():

    def __init__(self, graph): self.graph = list(graph)

    # Low-tech labels for our "edge" data structure/list
    def curstate  (self, edge): return edge[0]
    def actype    (self, edge): return edge[1]
    def acdata    (self, edge): return edge[2]
    def nextstate (self, edge): return edge[3]

    def action(self, cur_state):
        '''If cur_state matches and no command needed, return target action'''
        action = Action.NoAction # default    
        for e in self.graph:
            action = (cur_state == self.curstate(e) ).ite(
                (self.actype(e) == COMMAND).ite(
                    Action.GetCommand,
                    self.acdata(e)),
                action)
        return action
            
    def state(self, cur_state, command=Command.NoCommand):
        '''If cur_state and command both match, return target state'''
        state = cur_state # default    
        for e in self.graph:
            state = (cur_state == self.curstate(e)).ite(
                # need_command.ite(
                (self.actype(e) == COMMAND).ite(
                    (self.acdata(e) == command).ite(
                        self.nextstate(e),
                        state,
                    ),
                    self.nextstate(e),
                ),
                state)
        return state

    # FIXME/TODO def dot() etc.

########################################################################
class Queue():
    '''A way to pass messages between ourself and others. Depending on
    which way you want to go, you'll use one of the subclasses
    'RcvQueue' or 'XmtQueue', see below for details.
    '''
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

    def is_valid(self): return (self.valid == m.Bits[1](1))
    def is_ready(self): return (self.ready == m.Bits[1](1))

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
    def __init__(self, name, nbits, readyvalid=False, 
                 data_in=None, valid_in=None, ready_out=None
    ):
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
    def __init__(self, name, nbits, readyvalid=False, 
                 data_out=None, valid_out=None, ready_in=None
    ):
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


class StateMachine(CoopGenerator):

    # FIXME/TODO should not have to pass 'num_r_cols' as a separate parameter, yes?
    def __init__(self, SRAM_Definition, state_machine_graph, num_r_cols, **kwargs):
        self.SRAM_Definition = SRAM_Definition
        self.smg = state_machine_graph
        self.num_r_cols = num_r_cols
        super().__init__(**kwargs)

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

            offer       = m.In(m.Bits[Command.nbits]),
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

        # Init reg because I don't understand @inline_combinational :(
        self.initreg = m.Register(
            init=m.Bits[1](1),
            has_enable=False,
        )()
        self.initreg.name = "initreg"

        # redundancy reg holds redundancy data from ?client? for future ref
        # self.redundancy_reg = reg("redundancy_reg", nbits=16); # "redundancy" reg
        # ncols = SRAM_params['num_r_cols']
        # 
        # FIXME/TODO should not have to pass 'num_r_cols' as a
        # separate parameter, yes?
        ncols = self.num_r_cols
        self.redundancy_reg = m.Register(
            T=m.Bits[ncols],
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

        # mem_data reg holds data from client for writing to SRAM
        self.mem_data_reg = m.Register(
            T=m.Bits[16],
            has_enable=True,
        )()
        self.mem_data_reg.name = "mem_data_reg"

        # Instantiate SRAM using given definition
        self.MOCK = self.SRAM_Definition()

        # Formerly used registers o_reg, r_reg, and s_reg for IO.
        # Now, instead of registers, have ready/valid message
        # queues CommandFromClient, DataFromClient, DataToClient

        # Note: Redundancy info and address info both come in via DFC queue

        self.CommandFromClient = RcvQueue(
            "CommandFromClient", nbits=Command.nbits, readyvalid=True,
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

        self.DataToClient = XmtQueue(
            "DataToClient", nbits=16, readyvalid=True,
            ready_in  = self.io.send_ready,
            valid_out = self.io.send_valid,
            data_out  = self.io.send,
        );



    def _connect(self, **kwargs):
        super()._connect(**kwargs)
        self.io.current_state @= self.state_reg.O

        # =========================================================================
        # Note inline_combinational() is not very robust i.e. very particular about
        # indentation even on comments, also should avoid e.g. one-line if-then
        # ('if a: b=1'), multiple statements on one line separated by semicolon etc.

        @m.inline_combinational()
        def controller():
            cur_addr = self.mem_addr_reg.O

            # Init reg allows one-time reg initialization etc.
            init = self.initreg.O
            if init == m.Bits[1](1):
                addr_to_mem     = 13  # changes on read, write request
                data_from_mem   = 14  # magically changes when addr_to_mem changes
                data_to_client  = 15
                # redundancy_data = 16  # changes when we enter meminit state
                
                # Seed SRAM with correct value for fault test; need SRAM[0x66] = 0x1066
                MOCK_addr  = m.Bits[11](0x66)
                MOCK_wdata = m.Bits[16](0x1066)

                init_next = m.Bits[1](0)

            else:
                addr_to_mem = cur_addr

            self.initreg.I @= init_next

            # Convenient shortcuts
            cur_state = self.state_reg.O

            # Constants
            READY = m.Bits[1](1)
            VALID = m.Bits[1](1)
            ENABLE = True          # ??

            # Reset all ready-valid signals that we control.
            # Reset ready signals in FROM queues, valid signals in TO queues
            ready_for_dfc = ~READY     # Not ready for input from client
            ready_for_cmd = ~READY     # Not ready for command from client
            dtc_valid     = ~VALID     # Not ready to send data to client

            # Reset reg-enable signals
            redundancy_reg_enable = ~ENABLE
            addr_to_mem_enable    = ~ENABLE
            dtc_enable            = ~ENABLE
            cmd_enable            = ~ENABLE

            cfc = self.CommandFromClient
            dfc = self.DataFromClient
            dtc = self.DataToClient

            # Default is to stay in the same state as before
            next_state = cur_state
                
            # Given current state, find required action e.g.
            # 'Action.GetRedundancy' or 'Action.GetCommand'
            # info = match_action(cur_state)
            info = self.smg.action(cur_state)

            if info == Action.GetCommand:

                # Enable command reg, ready cmd queue
                cmd_enable = ENABLE
                ready_for_cmd = READY

                # E.g. cur_state==MemOff and cfc.data==PowerOn => goto MemOn
                if cfc.is_valid():
                    new_state = self.smg.state( cur_state, cfc.data)
                    if (new_state != cur_state):
                        ready_for_cmd = ~READY     # Got data, not yet ready for next command
                        next_state = new_state

            # FIXME remaining elif's should have more parallel structure :(

            # State.MemInit => Action.GetRedundancy()
            elif info == Action.GetRedundancy:

                # Wake up and turn on the power (FIXME or should this be in SendAck()?)
                self.MOCK.deep_sleep @= hw.Bit(0)
                self.MOCK.power_gate @= hw.Bit(0)

                # Enable regs
                redundancy_reg_enable = ENABLE

                # Get redundancy info from client/testbench
                # If successful, go to next_state

                ready_for_dfc = READY        # Ready for new data
                dfc_enable = ENABLE

                if dfc.is_valid():
                    redundancy_data = dfc.data[0:2]

                    # Using jimmied-up data
                    # ncols = SRAM_params['num_r_cols']
                    # self.MOCK.RCE @= hw.BitVector[ncols](-1)

                    # Using data from user
                    self.MOCK.RCE @= redundancy_data

                    # Want to do:
                    #   nbits = m.bitutils.clog2safe(ncols)
                    #   self.MOCK.RCF0A @= hw.BitVector[nbits](0)
                    #   self.MOCK.RCF1A @= hw.BitVector[nbits](1)

                    # Huh this seems to work???
                    # FIXME/TODO need to test this and see if it works :(
                    # Because I'm pretty sure it doesn't...
                    connect_RFCs(self.MOCK)

                    ready_for_dfc = ~READY   # Got data, not yet ready for next data
                    next_state = self.smg.state(cur_state)

            # State.MemOff + Command.PowerOn => State.SendAck => Action.SendAck()
            elif info == Action.SendAck:

                # Setup
                dtc_enable = ENABLE
                data_to_client = m.bits(self.MOCK.wake_ack, 16)
                dtc_valid = VALID

                # dtc READY means they got the data and we can all move on
                if dtc.is_ready() & self.MOCK.wake_ack:
                    # next_state = State.MemOn
                    next_state = self.smg.state(cur_state)

                    # Reset
                    dtc_valid  = ~VALID
                    dtc_enable = ~ENABLE
 

            # State MemOn: GONE!!! See far below for old State MemOn

            # State ReadAddr
            elif info == Action.GetAddr:

                # Don't know yet if address will be used for READ or WRITE
                MOCK_we = m.Enable(1)
                MOCK_re = m.Enable(1)

                # Setup
                dfc_enable         = ENABLE
                addr_to_mem_enable = ENABLE

                # Get read-address info from client/testbench
                # If successful, go to state ReadData

                ready_for_dfc = READY        # Ready for new data
                if dfc.is_valid():
                    addr_to_mem = dfc.data   # Get data (mem addr) from client requesting read
                    ready_for_dfc = ~READY   # Got data, not yet ready for next data
                    next_state = self.smg.state(cur_state)


            # State WriteData is similar to ReadAddr/WriteAddr
            # elif cur_state == State.WriteData:
            elif info == Action.WriteData:

                # Enable WRITE, disable READ
                MOCK_re = m.Enable(0)
                MOCK_we = m.Enable(1)

                # Get data from client, write it to SRAM
                # If successful, go to state MemOn

                # Setup
                dfc_enable = ENABLE
                data_to_mem_enable = ENABLE

                ready_for_dfc = READY        # Ready for new data
                if dfc.is_valid():
                    # FIXME hm so it looks like data_to_mem is never used,
                    # except if we delete it we have to eliminate the fault
                    # test that checks to see that it got set !? :(
                    data_to_mem = dfc.data   # Get data-to-write-to-SRAM from client

                    # FIXME should probably turn WE on and off to prevent data shmearing

                    MOCK_addr  = addr_to_mem[0:11]    # Address from prev step
                    MOCK_wdata = dfc.data             # Data from client
                    ready_for_dfc = ~READY            # Not yet ready for next data
                    next_state = self.smg.state(cur_state) # GOTO State.MemOn


            # State ReadData
            elif info == Action.ReadData:

                # Enable READ, disable WRITE
                MOCK_re = m.Enable(1)
                MOCK_we = m.Enable(0)

                # Setup
                dtc_enable = ENABLE

                MOCK_addr = addr_to_mem[0:11]   # Address from prev step
                data_to_client = self.MOCK.RDATA

                dtc_valid = VALID

                # dtc READY means they got the data and we can all move on
                if dtc.is_ready():
                    next_state = self.smg.state(cur_state) # GOTO State.MemOn

                    # Reset
                    dtc_valid  = ~VALID
                    dtc_enable = ~ENABLE

            self.MOCK.ADDR  @= MOCK_addr
            self.MOCK.WDATA @= MOCK_wdata

            # CEn is active low :(
            # REn and WEn are both active high :(
            self.MOCK.CEn   @= m.Enable(0)
            self.MOCK.WEn   @= MOCK_we
            self.MOCK.REn   @= MOCK_re

            # Wire up our shortcuts
            self.state_reg.I      @= next_state

            self.mem_addr_reg.I   @= addr_to_mem
            self.mem_addr_reg.CE  @= addr_to_mem_enable

            self.mem_data_reg.I   @= data_to_mem
            self.mem_data_reg.CE  @= data_to_mem_enable

            self.redundancy_reg.I  @= redundancy_data
            self.redundancy_reg.CE @= redundancy_reg_enable

            # "to" MessageQueue inputs
            self.CommandFromClient.ready  @= ready_for_cmd
            self.CommandFromClient.Reg.CE @= cmd_enable

            self.DataFromClient.ready    @= ready_for_dfc
            self.DataFromClient.Reg.CE   @= dfc_enable

            self.DataToClient.Reg.I      @= data_to_client
            self.DataToClient.valid      @= dtc_valid
            self.DataToClient.Reg.CE     @= dtc_enable


# FIXME (below) what even is this

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

