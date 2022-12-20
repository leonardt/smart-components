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
from .mock_mem import SRAMSingle
debug("* Done importing python packages...")

ADDR_WIDTH = 8
DATA_WIDTH = 8

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
    RedOn    = 6    # Turn on redundancy
    RedOff   = 7    # Turn off Redundancy
    DeepSleep      = 8
    TotalRetention = 9
    Retention      = 10


class Action(m.Enum):
    NoAction      = 0
    GetCommand    = 1
    GetRedundancy = 2  # Deprecated? FIXME
    GetAddr       = 3
    ReadData      = 4
    WriteData     = 5
    SetMode       = 6  # Deep sleep, retention, etc.
    RedMode       = 7  # Redundancy ON or OFF


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
    SetMode   = m.Bits[nbits](i); i=i+1 # 2
    MemOn     = m.Bits[nbits](i); i=i+1 # 3
    ReadAddr  = m.Bits[nbits](i); i=i+1 # 4
    ReadData  = m.Bits[nbits](i); i=i+1 # 5
    WriteAddr = m.Bits[nbits](i); i=i+1 # 6
    WriteData = m.Bits[nbits](i); i=i+1 # 7
    DeepSleep = m.Bits[nbits](i); i=i+1 # 8
    TotalRetention = m.Bits[nbits](i); i=i+1 # 9
    Retention      = m.Bits[nbits](i); i=i+1 # 10
    # When adding new states remember to update num_states above!!

def match_enum(enum_class, enum_value):
    '''
    Given enum class and value, return the name of enum as a string.
    Examples:
          match_enum(State,  State.MemOff)    => "MemOff"
          match_enum(Action, Action.ReadData) => "ReadData"
    '''
    for cls in enum_class.mro():
        for name,val in cls.__dict__.items():
            if type(val) == type(enum_value):
                if int(val) == int(enum_value): return name

##############################################################################
# Example of input to StateMachineGraph():
#
# ANY = Command.NoCommand
# mygraph = (
#     (State.MemInit,   ANY,                State.MemOff),
#     (State.MemOff,    Command.PowerOn,    State.SetMode),
#     (State.MemOn,     Command.PowerOff,   State.MemOff),
#     (State.MemOn,     Command.Read,       State.ReadAddr),
#     (State.MemOn,     Command.Write,      State.WriteAddr),
#     (State.SetMode,   ANY,                State.MemOn),
#     (State.ReadAddr,  ANY,                State.ReadData),
#     (State.WriteAddr, ANY,                State.WriteData),
#     (State.WriteData, ANY,                State.MemOn),
#     (State.ReadData,  ANY,                State.MemOn),
# )

class StateMachineGraph():

    def __init__(self, graph): self.graph = list(graph)

    # Low-tech labels for our "edge" data structure/list
    def curstate  (self, edge): return edge[0]
    def command   (self, edge): return edge[1]
    def nextstate (self, edge): return edge[2]

    # (State.MemOn,     Command.PowerOff,       State.MemOff),
    # (State.MemOn,     Command.Read,           State.ReadAddr),
    # (State.MemOn,     Command.Write,          State.WriteAddr),
    # (State.WriteAddr, ANY,                    State.WriteData),
    # (State.WriteData, ANY,                    State.MemOn),

    def get_next_state(self, cur_state, command=Command.NoCommand):
        '''If cur_state and command both match, return target state'''
        state = cur_state # default
        for e in self.graph:
            e_command  = self.command(e)
            e_curstate = self.curstate(e)
            e_nextstate = self.nextstate(e)

            state_match   = (cur_state == e_curstate)
            command_match = (command   == e_command)

            state = state_match.ite(
                command_match.ite(
                    e_nextstate,
                    state,
                ),
                state)
        return state

    def build_dot_graph(graph):
        '''
        Given a graph in StateMachine format, build a dot input file.
        # Example: build_dot_graph(mygraph) =>
        #
        #     digraph Diagram { node [shape=box];
        #       "MemInit"   -> "MemOff"    [label="NoCommand"];
        #       "MemOff"    -> "SetMode"   [label="PowerOn"];
        #       "MemOn"     -> "MemOff"    [label="PowerOff"];
        #       "MemOn"     -> "ReadAddr"  [label="Read"];
        #       "MemOn"     -> "WriteAddr" [label="Write"];
        #       "SetMode"   -> "MemOn"     [label="PowerOn"];
        #       "ReadAddr"  -> "ReadData"  [label="NoCommand"];
        #       "WriteAddr" -> "WriteData" [label="NoCommand"];
        #       "WriteData" -> "MemOn"     [label="NoCommand"];
        #       "ReadData"  -> "MemOn"     [label="NoCommand"];
        #     }
        '''
        def quote(word): return '"' + word + '"'
        print('digraph Diagram { node [shape=box];')
        for edge in graph:
            # FIXME should use curstate(edge) etc. instead of edge[0] etc.
            curstate  = match_enum(State,   edge[0])
            command   = match_enum(Command, edge[1])
            nextstate = match_enum(State,   edge[2])

            # New: always use command for the edges
            # b/c actions are redundant w/ state
            label = command
            if command == "NoCommand": label = ""

            print(f'  {quote(curstate):11} -> {quote(nextstate):11} [label={quote(label)}];')
        print('}\n')



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
            self.redundancy_reg.I @= w
            self.mem.RCE @= self.redundancy_reg.O

    def get_redreg_out(self):
        if self.has_redundancy:
            return self.redundancy_reg.O
        else:
            return  m.Bits[self.num_r_cols](0)

    # No this does not work :(
    # def power_on(self):
    #     if self.needs_wake_ack:
    #         self.mem.deep_sleep @= hw.Bit(0)
    #         self.mem.power_gate @= hw.Bit(0)

    def send_wake_ack(self, cond, cur_state, cur_cmd=Command.NoCommand):

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

            return (m.bits(self.mem.wake_ack, DATA_WIDTH), v, e, next_state)

        else:
            # dummy values. does not compile w/out this else clause :(
            # return (m.Bits[16](0), VALID,  ENABLE, cur_state)
            return (m.Bits[DATA_WIDTH](0), VALID,  ENABLE, cur_state)


    def got_wake_ack(self, expected_value):
        if self.needs_wake_ack:
            return (self.mem.wake_ack == expected_value)
        else:
            return (m.Bits[1](1) == m.Bits[1](1))

    def __init__(self, MemDefinition, state_machine_graph, **kwargs):
        self.MemDefinition = MemDefinition
        self.smg = state_machine_graph

        self.num_r_cols = getattr(MemDefinition, 'num_r_cols', None)
        if self.num_r_cols is None:
            self.has_redundancy = False
            self.num_r_cols = 1
        else:
            self.has_redundancy = True

        self.wake_ack = getattr(MemDefinition, 'wake_ack', None)
        if self.wake_ack is None:
            self.needs_wake_ack = False
            self.wake_ack = hw.Bit(0)
        else:
            self.needs_wake_ack = True

        # Single-port SRAM has 'ADDR', double-port has 'RADDR/WADDR'
        # self.is_single = ('ADDR' in dir(MemDefinition))
        # self.is_single = hasattr(MemDefinition, 'ADDR')
        self.is_single = isinstance(MemDefinition, SRAMSingle)


        # print(dir(MemDefinition))        # 'RCE', 'RCF0A', 'RCF1A'
        # print( getattr(MemDefinition, 'IO') )
        # assert False

        # FIXME yeah, this whole connect_RCF mechanism is not great...
        # Note ORDER IS IMPORTANT here
        # dm = dir(MemDefinition)

        RCF2 = (self.num_r_cols == 3)
        RCF1 = (self.num_r_cols == 2)
        RCF0 = (self.num_r_cols == 1) and (self.has_redundancy)

        if   RCF2: connect_RCFs = connect_RCFs_3col
        elif RCF1: connect_RCFs = connect_RCFs_2col
        elif RCF0: connect_RCFs = connect_RCFs_1col
        else:      connect_RCFs = connect_RCFs_pass
        self.connect_RCFs = connect_RCFs

        self.n_redundancy_bits = 1
        if   RCF2: self.n_redundancy_bits = 3 # not sure this is correct...
        elif RCF1: self.n_redundancy_bits = 2
        elif RCF0: self.n_redundancy_bits = 1

        super().__init__(**kwargs)

    def _decl_attrs(self, **kwargs):
        super()._decl_attrs(**kwargs)

    def _decl_io(self, **kwargs):
        super()._decl_io(**kwargs)

        # dfcq = "data-from-client queue" (i.e. receive)
        # dtcq = "data-to-client queue" (i.e. send)
        self.io += m.IO(
            receive       = m.In(m.Bits[DATA_WIDTH]),
            receive_valid = m.In(m.Bits[ 1]),
            receive_ready = m.Out(m.Bits[1]),

            offer       = m.In(Command),
            offer_valid = m.In(m.Bits[1]),
            offer_ready = m.Out(m.Bits[1]),

            send       = m.Out(m.Bits[DATA_WIDTH]),
            send_ready = m.In(m.Bits[1]),
            send_valid = m.Out(m.Bits[1]),
            dfcq_valid = m.Out(m.Bits[1]),
            dfcq_enable = m.Out(m.Bit),
            dtcq_ready = m.Out(m.Bits[1]),
            mem_addr_reg_out = m.Out(m.Bits[DATA_WIDTH]),
            mem_addr_reg_CE_out = m.Out(m.Bit),
            mem_data_reg_out = m.Out(m.Bits[DATA_WIDTH]),
            mem_data_reg_CE_out = m.Out(m.Bit),

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

        # redundancy reg holds redundancy data from client
        if self.has_redundancy:
            self.redundancy_reg = m.Register(
                T=m.Bits[self.num_r_cols],
                has_enable=False,
            )()
            self.redundancy_reg.name = "redundancy_reg"

        # mem_addr reg holds mem_addr data from ?client? for future ref
        # self.mem_addr_reg = reg("mem_addr_reg", nbits=16); # "mem_addr" reg
        self.mem_addr_reg = m.Register(
            T=m.Bits[DATA_WIDTH],
            has_enable=True,
        )()
        self.mem_addr_reg.name = "mem_addr_reg"
        self.io.mem_addr_reg_out @= self.mem_addr_reg.O

        # mem_data reg holds data from client for writing to SRAM
        self.mem_data_reg = m.Register(
            T=m.Bits[DATA_WIDTH],
            has_enable=True,
        )()
        self.mem_data_reg.name = "mem_data_reg"
        self.io.mem_data_reg_out @= self.mem_data_reg.O

        # FIXME move this up *before* any usage of self.mem :(
        # Instantiate SRAM using given definition
        self.mem = self.MemDefinition()
        if hasattr(self.mem, 'current_state'):
            self.io += m.IO(mem_current_state=m.Out(type(self.mem.current_state)))
            self.io.mem_current_state @= self.mem.current_state

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
            "DataFromClient", nbits=DATA_WIDTH, readyvalid=True,
            data_in   = self.io.receive,
            valid_in  = self.io.receive_valid,
            ready_out = self.io.receive_ready,
        );

        self.DataToClient = XmtQueue(
            "DataToClient", nbits=DATA_WIDTH, readyvalid=True,
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

        cur_addr = self.mem_addr_reg.O
        addr_to_mem = type(cur_addr).undirected_t()
        self.DataToClient.Reg.I @= self.DataToClient.Reg.O

        # Init reg allows one-time reg initialization etc.
        init = self.initreg.O
        self.initreg.I @= init
        self.connect_ds_pg(0, 0)

        with m.when(init == m.Bits[1](1)):
            addr_to_mem     @= 13  # changes on read, write request
            # data_from_mem   = 14  # magically changes when addr_to_mem changes
            self.DataToClient.Reg.I @= 15

            # So we only do this ONCE on start-up
            self.initreg.I @= m.Bits[1](0)

            # self.power_on()
            self.connect_ds_pg(0, 0)

        with m.otherwise():
            addr_to_mem @= cur_addr

        # Convenient shortcuts
        cur_state = self.state_reg.O

        # Constants
        READY = m.Bits[1](1)
        VALID = m.Bits[1](1)
        ENABLE = True          # ??

        # Reset all ready-valid signals that we control.
        # Reset ready signals in FROM queues, valid signals in TO queues
        self.DataFromClient.ready @= ~READY     # Not ready for input from client
        self.CommandFromClient.ready @= ~READY     # Not ready for command from client
        self.DataToClient.valid @= ~VALID     # Not ready to send data to client

        self.mem_addr_reg.CE @= ~ENABLE
        self.DataToClient.Reg.CE @= ~ENABLE

        # "to" MessageQueue inputs
        self.CommandFromClient.Reg.CE @= ~ENABLE

        cfc = self.CommandFromClient
        dfc = self.DataFromClient
        self.io.dfcq_valid @= dfc.valid
        dtc = self.DataToClient
        self.io.dtcq_ready @= dtc.ready

        # Default is to stay in the same state as before
        self.state_reg.I @= cur_state

        self.mem.WEn @= 0
        self.mem.REn @= 0
        self.connect_RCE(self.get_redreg_out())
        self.mem_data_reg.CE @= ~ENABLE
        self.DataFromClient.Reg.CE @= ~ENABLE

        with m.when((cur_state == State.MemOff) | (cur_state == State.MemOn)):

            # Enable command reg, ready cmd queue
            self.CommandFromClient.Reg.CE @= ENABLE
            self.CommandFromClient.ready @= READY

            # E.g. cur_state==MemOff and cfc.data==PowerOn => goto MemOn
            with m.when(cfc.is_valid()):

                with m.when(cfc.data == Command.RedOn):
                    self.connect_RCE(-1)

                with m.elsewhen(cfc.data == Command.RedOff):
                    self.connect_RCE(0)

                new_state = self.smg.get_next_state( cur_state, cfc.data)
                with m.when(new_state != cur_state):
                    self.CommandFromClient.ready @= ~READY     # Got data, not yet ready for next command
                    self.state_reg.I @= new_state

        # FIXME remaining elif's should have more parallel structure :(

        with m.elsewhen(cur_state == State.MemInit):

            # FIXME should use the get_next _state!!!
            # next_state = self.smg.get_next_state(cur_state)
            self.state_reg.I @= State.MemOff



        # State.MemOff + Command.PowerOn => State.SetMode => Action.SetMode()
        with m.elsewhen(cur_state == State.SetMode):

            ack = m.Bits[1]()
            ack @= 0
            with m.when(cfc.data == Command.DeepSleep):
                # self.goto_deep_sleep()
                self.connect_ds_pg(1, 1)
            with m.elsewhen(cfc.data == Command.TotalRetention):
                self.connect_ds_pg(0, 1)
            with m.elsewhen(cfc.data == Command.PowerOn):
                ack @= 1

            # Setup
            # data_to_client = self.send_wake_ack()
            # dtc READY means they got the data and we can all move on
            (
                data_to_client,
                dtc_valid,
                dtc_enable,
                next_state,
            ) = self.send_wake_ack(
                dtc.is_ready() & self.got_wake_ack(ack),
                cur_state,
                cur_cmd=cfc.data,
            )
            self.state_reg.I @= next_state
            self.DataToClient.Reg.I @= data_to_client
            self.DataToClient.valid @= dtc_valid
            self.DataToClient.Reg.CE @= dtc_enable

        # State ReadAddr
        with m.elsewhen((cur_state == State.ReadAddr) | (cur_state == State.WriteAddr)):

            # Setup
            self.DataFromClient.Reg.CE @= ENABLE
            self.mem_addr_reg.CE @= ENABLE

            # Get read-address info from client/testbench
            # If successful, go to state ReadData

            self.DataFromClient.ready @= READY        # Ready for new data
            with m.when(dfc.is_valid()):
                addr_to_mem @= dfc.data   # Get data (mem addr) from client requesting read
                self.DataFromClient.ready @= ~READY   # Got data, not yet ready for next data
                next_state = self.smg.get_next_state(cur_state)
                self.state_reg.I @= next_state


        # State WriteData is similar to ReadAddr/WriteAddr
        with m.elsewhen(cur_state == State.WriteData):

            # Enable WRITE, disable READ
            self.mem.WEn   @= 1

            # Get data from client, write it to SRAM
            # If successful, go to state MemOn

            # Setup
            self.DataFromClient.Reg.CE @= ENABLE
            self.mem_data_reg.CE  @= ENABLE

            self.DataFromClient.ready @= READY        # Ready for new data
            with m.when(dfc.is_valid()):

                # FIXME should probably turn WE on and off to prevent data shmearing

                self.DataFromClient.ready @= ~READY            # Not yet ready for next data
                next_state = self.smg.get_next_state(cur_state) # GOTO State.MemOn
                self.state_reg.I @= next_state


        # State ReadData
        with m.elsewhen(cur_state == State.ReadData):

            # Enable READ, disable WRITE
            self.mem.REn   @= 1

            # Setup
            self.DataToClient.Reg.CE @= ENABLE

            self.DataToClient.Reg.I @= self.mem.RDATA

            self.DataToClient.valid @= VALID

            # dtc READY means they got the data and we can all move on
            with m.when(dtc.is_ready()):
                next_state = self.smg.get_next_state(cur_state) # GOTO State.MemOn
                self.state_reg.I @= next_state

                # Reset
                self.DataToClient.valid @= ~VALID
                self.DataToClient.Reg.CE @= ~ENABLE


        # FIXME/TODO these could both be simply 'self.connect_ad(SRAM_addr, SRAM_wdata)'
        # self.mem.ADDR  @= SRAM_addr
        self.connect_addr(addr_to_mem[0:ADDR_WIDTH])  # Address from prev step
        self.mem.WDATA @= dfc.data                    # Data from client


        # CEn is active low :(
        # REn and WEn are both active high :(
        self.mem.CEn   @= m.Enable(0)

        # self.mem.deep_sleep @= ds; self.mem.power_gate @= pg

        # FIXME why is one of these "self" and the other one not?
        self.connect_RCFs(self.mem)

        # Wire up our shortcuts

        self.mem_addr_reg.I   @= addr_to_mem

        # FIXME hm so it looks like data_to_mem is never used,
        # except if we delete it we have to eliminate the fault
        # test that checks to see that it got set !? :(
        self.mem_data_reg.I   @= dfc.data

        self.io.dfcq_enable @= dfc.Reg.CE.value()
        self.io.mem_data_reg_CE_out @= self.mem_data_reg.CE.value()
        self.io.mem_addr_reg_CE_out @= self.mem_addr_reg.CE.value()
        if self.has_redundancy:
            self.io += m.IO(RCF0A=m.Out(type(self.mem.RCF0A)))
            self.io.RCF0A @= self.mem.RCF0A.value()
            self.io += m.IO(RCE=m.Out(m.Bits[self.num_r_cols]))
            self.io.RCE @= self.mem.RCE.value()




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

