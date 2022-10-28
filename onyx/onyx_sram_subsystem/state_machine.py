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

from enum import Enum
class Command(m.Enum):
    NoCommand= 0
    PowerOff = 1
    PowerOn  = 2
    Read     = 3
    Write    = 4
    Idle     = 5
    DeepSleep      = 6
    TotalRetention = 7
    Retention      = 8


class Action(m.Enum):
    NoAction      = 0
    GetCommand    = 1
    GetRedundancy = 2
    SendAck       = 3
    GetAddr       = 4
    ReadData      = 5
    WriteData     = 6
    SetMode       = 7


# FIXME Argh try as I might, could not make this work as m.Enum :(
class State():
    #----------------------------------
    num_states = 10; i=0
    nbits = (num_states).bit_length()
    #----------------------------------

    # FIXME/NOTE I think everything breaks if MemInit != 0 
    # and/or MemInit is not first state in state machine...

    MemInit   = m.Bits[nbits](i); i=i+1 # 0
    MemOff    = m.Bits[nbits](i); i=i+1 # 1
    SetMode   = m.Bits[nbits](i); i=i+1 # 2 UNUSED???
    MemOn     = m.Bits[nbits](i); i=i+1 # 3
    ReadAddr  = m.Bits[nbits](i); i=i+1 # 4
    ReadData  = m.Bits[nbits](i); i=i+1 # 5
    WriteAddr = m.Bits[nbits](i); i=i+1 # 6
    WriteData = m.Bits[nbits](i); i=i+1 # 7
    DeepSleep = m.Bits[nbits](i); i=i+1 # 8
    TotalRetention = m.Bits[nbits](i); i=i+1 # 9
    Retention      = m.Bits[nbits](i); i=i+1 # 10
    # When adding new states remember to update num_states above!!


##############################################################################
# begin side quest

def match_enum(enum_class, enum_value):
    '''
    Given enum class and value, return the name of enum as a string.
    Examples:
          match_enum(State, State.MemOff)     => "MemOff"
          match_enum(Action, Action.ReadData) => "ReadData"
    '''
    for i in dir(enum_class):
        val = getattr(enum_class, i)
        if type(val) == type(enum_value):
            if int(val) == int(enum_value): return i


# end side quest
##############################################################################
# Example of input to StateMachineGraph():
# 
# ANY = Command.NoCommand
# mygraph = (
#     (State.MemInit,   ANY,                Action.GetRedundancy, State.MemOff),
#     (State.MemOff,    Command.PowerOn,    Action.GetCommand,    State.SetMode),
#     (State.MemOn,     Command.PowerOff,   Action.GetCommand,    State.MemOff),
#     (State.MemOn,     Command.Read,       Action.GetCommand,    State.ReadAddr),
#     (State.MemOn,     Command.Write,      Action.GetCommand,    State.WriteAddr),
#     (State.SetMode,   ANY,                Action.SendAck,       State.MemOn),
#     (State.ReadAddr,  ANY,                Action.GetAddr,       State.ReadData),
#     (State.WriteAddr, ANY,                Action.GetAddr,       State.WriteData),
#     (State.WriteData, ANY,                Action.WriteData,     State.MemOn),
#     (State.ReadData,  ANY,                Action.ReadData,      State.MemOn),
# )

class StateMachineGraph():

    def __init__(self, graph): self.graph = list(graph)

    # Low-tech labels for our "edge" data structure/list
    def curstate  (self, edge): return edge[0]
    def command   (self, edge): return edge[1]
    def action    (self, edge): return edge[2]
    def nextstate (self, edge): return edge[3]

    def get_action(self, cur_state):
        '''If cur_state matches and no command needed, return target action'''
        action = Action.NoAction # default    
        for e in self.graph:
            e_state  = self.curstate(e)
            e_action = self.action(e)
            # If we are in the indicated state, tell SM to do the indicated action (duh)
            action = (cur_state == e_state).ite(e_action, action)
        return action
            
    def get_next_state(self, cur_state, command=Command.NoCommand):
        '''If cur_state and command both match, return target state'''
        state = cur_state # default    
        for e in self.graph:
            e_command  = self.command(e)
            e_curstate = self.curstate(e)
            e_nextstate = self.nextstate(e)

            state_match = (cur_state == e_curstate)
            command_match = (command == e_command)

            state = state_match.ite(
                command_match.ite(
                    e_nextstate,
                    state
                ),
                state)
        return state

    def build_dot_graph(graph):
        '''
        Given a graph in StateMachine format, build a dot input file.
        # Example: build_dot_graph(mygraph) =>
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
        for edge in graph:
            curstate  = match_enum(State, edge[0])
            command   = match_enum(Command, edge[1])
            action    = match_enum(Action, edge[2])
            nextstate = match_enum(State, edge[3])

            if action == "GetCommand": label = command
            else:                      label = action + "()"

            print(f'  {quote(curstate):11} -> {quote(nextstate):11} [label={quote(label)}];')
        print('}\n')



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


########################################################################
# FIXME yeah, this whole connect_RCF mechanism is not great...

# ------------------------------------------------------------------------
# Programmatically connect RFC signals for SRAMs w redundancy
# FIXME this is terrible
# FIXME also: not even sure if it's right

# Use this one when SRAM_params = { 'num_r_cols': 1 }
def connect_RCFs_1col(ckt):
    nbits=1
    ckt.RCF0A @= hw.BitVector[nbits](0)

# Use this one when SRAM_params = { 'num_r_cols': 2 }
def connect_RCFs_2col(ckt):
    nbits=1
    ckt.RCF0A @= hw.BitVector[nbits](0)
    ckt.RCF1A @= hw.BitVector[nbits](1)

# Use this one when SRAM_params = { 'num_r_cols': 3 }?
def connect_RCFs_3col(ckt):
    nbits=2
    ckt.RCF0A @= hw.BitVector[nbits](0)
    ckt.RCF1A @= hw.BitVector[nbits](1)
    ckt.RCF2A @= hw.BitVector[nbits](2)

# Use this one for non-redundant SRAMs
def connect_RCFs_pass(ckt): pass



class StateMachine(CoopGenerator):

    def connect_addr(self, w):
        if self.is_single:
            self.mem.ADDR  @= w
        else:
            self.mem.RADDR  @= w
            self.mem.WADDR  @= w

    def connect_ds_pg(self, ds, pg):
        if self.needs_wake_ack:
            self.mem.deep_sleep @= ds
            self.mem.power_gate @= pg

    def connect_RCE(self, w):
        if self.has_redundancy:
            self.mem.RCE @= w


    def connect_redundancy_signals(self, w, w2):
        if self.has_redundancy:
            self.redundancy_reg.I  @= w
            self.redundancy_reg.CE @= w2

    # No this does not work :(
    # def power_on(self):
    #     if self.needs_wake_ack:
    #         self.mem.deep_sleep @= hw.Bit(0)
    #         self.mem.power_gate @= hw.Bit(0)

    def send_wake_ack(self, cur_state, cond, cur_cmd=Command.NoCommand):

        # All active high
        ENABLE = True
        READY  = m.Bits[1](1)
        VALID  = m.Bits[1](1)

        if self.needs_wake_ack:

            # cond HI means client is ready to receive wake_ack signal, so
            # can advance to next state and pull v/e low; else remain in
            # current state and signal ready/waiting for client ready (v/e hi)
            new_state = self.smg.get_next_state(cur_state, command=cur_cmd)

            next_state = cond.ite(new_state, cur_state)
            v          = cond.ite(~VALID,  VALID) 
            e          = cond.ite(~ENABLE, ENABLE)

            return (m.bits(self.mem.wake_ack, 16), v, e, next_state)

        else:
            # dummy values. does not compile w/out this else clause :(
            return (m.Bits[16](0),                      VALID,  ENABLE, cur_state)


    def got_wake_ack(self, expected_value):
        if self.needs_wake_ack:
            return (self.mem.wake_ack == expected_value)
        else:
            return (m.Bits[1](1) == m.Bits[1](1))

    # FIXME/TODO should not have to pass 'num_r_cols' as a separate parameter, yes?
    def __init__(self, MemDefinition, state_machine_graph, **kwargs):
        self.MemDefinition = MemDefinition
        self.smg = state_machine_graph

        # FIXME I'm sure there's a better way...
        # self.num_r_cols = MemDefinition.num_r_cols
        if 'num_r_cols' in dir(self.MemDefinition):
            self.num_r_cols = MemDefinition.num_r_cols
            self.has_redundancy = True
        else:
            self.has_redundancy = False

        if 'wake_ack' in dir(MemDefinition):
            self.needs_wake_ack = True
            self.wake_ack = self.MemDefinition.wake_ack
        else:
            self.needs_wake_ack = False
            self.wake_ack = hw.Bit(0) # dummy value

        # Single-port SRAM has 'ADDR', double-port has 'RADDR/WADDR'
        self.is_single = ('ADDR' in dir(MemDefinition))

        # print(dir(MemDefinition))        # 'RCE', 'RCF0A', 'RCF1A'
        # print( getattr(MemDefinition, 'IO') )
        # assert False

        # FIXME yeah, this whole connect_RCF mechanism is not great...
        # Note ORDER IS IMPORTANT here
        dm = dir(MemDefinition)

        if   'RCF2A' in dm: connect_RCFs = connect_RCFs_3col
        elif 'RCF1A' in dm: connect_RCFs = connect_RCFs_2col
        elif 'RCF0A' in dm: connect_RCFs = connect_RCFs_1col
        else:               connect_RCFs = connect_RCFs_pass

        self.n_redundancy_bits = 1
        if   'RCF2A' in dm: self.n_redundancy_bits = 3 # not sure this is correct...
        elif 'RCF1A' in dm: self.n_redundancy_bits = 2
        elif 'RCF0A' in dm: self.n_redundancy_bits = 1


        super().__init__(**kwargs)

    def _decl_attrs(self, **kwargs):
        super()._decl_attrs(**kwargs)

    def _decl_io(self, **kwargs):
        super()._decl_io(**kwargs)

        # dfcq = "data-from-client queue" (i.e. receive)
        # dtcq = "data-to-client queue" (i.e. send)
        self.io += m.IO(
            receive       = m.In(m.Bits[16]),
            receive_valid = m.In(m.Bits[ 1]),
            receive_ready = m.Out(m.Bits[1]),

            offer       = m.In(Command),
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
        if self.has_redundancy:
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

        # FIXME move this up *before* any usage of self.mem :(
        # Instantiate SRAM using given definition
        self.mem = self.MemDefinition()

        # Formerly used registers o_reg, r_reg, and s_reg for IO.
        # Now, instead of registers, have ready/valid message
        # queues CommandFromClient, DataFromClient, DataToClient

        # Note: Redundancy info and address info both come in via DFC queue

        # EXAMPLE
        #   getattr(Command, '_info_')
        #   => (Bits, 2, Bit)

        nbits = getattr(Command, '_info_')[1]
        self.CommandFromClient = RcvQueue(
            "CommandFromClient", nbits=nbits, readyvalid=True,
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
                
                # FIXME what? why?
                # Seed SRAM_addr with any random value
                # For some reason it breaks without this!!??
                SRAM_addr  = m.Bits[11](0x6)

                # So we only do this ONCE on start-up
                init_next = m.Bits[1](0)

                # self.power_on()
                ds = hw.Bit(0); pg = hw.Bit(0)

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

            if self.has_redundancy:
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
            next_action = self.smg.get_action(cur_state)

            if next_action == Action.GetCommand:

                # Enable command reg, ready cmd queue
                cmd_enable = ENABLE
                ready_for_cmd = READY

                # E.g. cur_state==MemOff and cfc.data==PowerOn => goto MemOn
                if cfc.is_valid():
                    new_state = self.smg.get_next_state( cur_state, cfc.data)
                    if (new_state != cur_state):
                        ready_for_cmd = ~READY     # Got data, not yet ready for next command
                        next_state = new_state

            # FIXME remaining elif's should have more parallel structure :(

            elif next_action == Action.NoAction:
                # next_state = self.smg.get_next_state(cur_state)
                next_state = State.MemOff


            # State.MemInit => Action.GetRedundancy()
            elif next_action == Action.GetRedundancy:

                # Enable regs
                redundancy_reg_enable = ENABLE

                # Get redundancy info from client/testbench
                # If successful, go to next_state

                ready_for_dfc = READY        # Ready for new data
                dfc_enable = ENABLE

                if dfc.is_valid():

                    # FIXME need better way to wrap up all this
                    # SRAM-specific redundancy stuff---like n_redundancy_bits :(

                    # redundancy_data = dfc.data[0:2]
                    # redundancy_data = dfc.data[0:1]
                    redundancy_data = dfc.data[0:self.n_redundancy_bits]

                    # Using jimmied-up data
                    # ncols = SRAM_params['num_r_cols']
                    # self.mem.RCE @= hw.BitVector[ncols](-1)

                    # Using data from user
                    # self.mem.RCE @= redundancy_data
                    self.connect_RCE(redundancy_data)

                    # Want to do:
                    #   nbits = m.bitutils.clog2safe(ncols)
                    #   self.mem.RCF0A @= hw.BitVector[nbits](0)
                    #   self.mem.RCF1A @= hw.BitVector[nbits](1)

                    # Huh this seems to work???
                    # FIXME/TODO move this up to a better place, make sure it still works...
                    connect_RCFs(self.mem)

                    ready_for_dfc = ~READY   # Got data, not yet ready for next data
                    next_state = self.smg.get_next_state(cur_state)

            # State.MemOff + Command.PowerOn => State.SetMode => Action.SendAck()
            elif next_action == Action.SendAck:

                # self.power_on()
                ds = hw.Bit(0); pg = hw.Bit(0)

                # Setup
                # data_to_client = self.send_wake_ack()
                # dtc READY means they got the data and we can all move on
                (
                    data_to_client, 
                    dtc_valid,
                    dtc_enable,
                    next_state,
                ) = self.send_wake_ack(
                    cur_state,
                    dtc.is_ready() & self.got_wake_ack(m.Bits[1](1)),
                )

            # State MemOn: GONE!!! See far below for old State MemOn

            # State ReadAddr
            elif next_action == Action.GetAddr:

                # Don't know yet if address will be used for READ or WRITE
                SRAM_re = m.Enable(1)
                SRAM_we = m.Enable(1)

                # Setup
                dfc_enable         = ENABLE
                addr_to_mem_enable = ENABLE

                # Get read-address info from client/testbench
                # If successful, go to state ReadData

                ready_for_dfc = READY        # Ready for new data
                if dfc.is_valid():
                    addr_to_mem = dfc.data   # Get data (mem addr) from client requesting read
                    ready_for_dfc = ~READY   # Got data, not yet ready for next data
                    next_state = self.smg.get_next_state(cur_state)


            # State.MemOff + Command.PowerOn => State.SetMode => Action.SendAck()
            elif next_action == Action.SetMode:

                command = Command.NoCommand
                if cfc.data == Command.DeepSleep:
                    # self.goto_deep_sleep()
                    ds = hw.Bit(1); pg = hw.Bit(1); ack = m.Bits[1](0)
                elif cfc.data == Command.TotalRetention:
                    ds = hw.Bit(0); pg = hw.Bit(1); ack = m.Bits[1](0)
                elif cfc.data == Command.PowerOn:
                    ds = hw.Bit(0); pg = hw.Bit(0); ack = m.Bits[1](1)

                # Setup
                # data_to_client = self.send_wake_ack()
                # dtc READY means they got the data and we can all move on
                (
                    data_to_client, 
                    dtc_valid,
                    dtc_enable,
                    next_state,
                ) = self.send_wake_ack(
                    cur_state,
                    # dtc.is_ready() & self.got_wake_ack(m.Bits[1](0)),
                    dtc.is_ready() & self.got_wake_ack(ack),
                    cur_cmd=cfc.data,
                )

            # State WriteData is similar to ReadAddr/WriteAddr
            elif next_action == Action.WriteData:

                # Enable WRITE, disable READ
                SRAM_re = m.Enable(0)
                SRAM_we = m.Enable(1)

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

                    SRAM_addr  = addr_to_mem[0:11]    # Address from prev step
                    SRAM_wdata = dfc.data             # Data from client
                    ready_for_dfc = ~READY            # Not yet ready for next data
                    next_state = self.smg.get_next_state(cur_state) # GOTO State.MemOn


            # State ReadData
            elif next_action == Action.ReadData:

                # Enable READ, disable WRITE
                SRAM_re = m.Enable(1)
                SRAM_we = m.Enable(0)

                # Setup
                dtc_enable = ENABLE

                SRAM_addr = addr_to_mem[0:11]   # Address from prev step
                data_to_client = self.mem.RDATA

                dtc_valid = VALID

                # dtc READY means they got the data and we can all move on
                if dtc.is_ready():
                    next_state = self.smg.get_next_state(cur_state) # GOTO State.MemOn

                    # Reset
                    dtc_valid  = ~VALID
                    dtc_enable = ~ENABLE

            # FIXME/TODO these could both be simply 'self.connect_ad(SRAM_addr, SRAM_wdata)'
            # self.mem.ADDR  @= SRAM_addr
            self.connect_addr(SRAM_addr)
            self.mem.WDATA @= SRAM_wdata

            # CEn is active low :(
            # REn and WEn are both active high :(
            self.mem.CEn   @= m.Enable(0)
            self.mem.WEn   @= SRAM_we
            self.mem.REn   @= SRAM_re

            # self.mem.deep_sleep @= ds; self.mem.power_gate @= pg
            self.connect_ds_pg(ds, pg)

            # Wire up our shortcuts
            self.state_reg.I      @= next_state

            self.mem_addr_reg.I   @= addr_to_mem
            self.mem_addr_reg.CE  @= addr_to_mem_enable

            self.mem_data_reg.I   @= data_to_mem
            self.mem_data_reg.CE  @= data_to_mem_enable

            # self.redundancy_reg.I  @= redundancy_data
            # self.redundancy_reg.CE @= redundancy_reg_enable

            self.connect_redundancy_signals(redundancy_data, redundancy_reg_enable)

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

