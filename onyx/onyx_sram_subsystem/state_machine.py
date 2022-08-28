import magma as m
import hwtypes as ht
from mock_mem import SRAMDMR
from session import Offer, Choose, Send, Recieve, Sequence
from session import SessionTypeVisitor, SessionT, LabelT
from util import inverse_look_up, BiMap

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

class State():
    #----------------------------------
    num_states = 4; i=0
    nbits = (num_states-1).bit_length()
    #----------------------------------
    MemInit = m.Bits[nbits](i); i=i+1
    MemOff  = m.Bits[nbits](i); i=i+1
    Send    = m.Bits[nbits](i); i=i+1 # currently unused maybe
    MemOn   = m.Bits[nbits](i); i=i+1

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

        # "state" reg
        nbits = (self.num_states-1).bit_length()
        self.state_reg = m.Register(
            init=m.Bits[nbits](0),
            has_enable=False,
        )()
        self.state_reg.name = "state_reg"

        # "send" reg
        self.s_reg = m.Register(
            T=m.Bits[16],
            has_enable=True,
        )()
        self.s_reg.name = "s_reg"

        # "receive" reg
        self.r_reg = m.Register(
            T=m.Bits[16],
            has_enable=True,
        )()
        self.r_reg.name = "r_reg"

        # "offer" (cmd) reg
        self.o_reg = m.Register(
            T=m.Bits[4],
            has_enable=True,
        )()
        self.o_reg.name = "o_reg"

        # "redundancy" reg
        self.redundancy_reg = m.Register(
            T=m.Bits[16],
            has_enable=True,
        )()
        self.redundancy_reg.name = "redundancy_reg"

    def _connect(self, **kwargs):
        super()._connect(**kwargs)
        self.io.current_state @= self.state_reg.O
        self.r_reg.I @= self.io.receive
        self.o_reg.I @= self.io.offer
        self.io.send @= self.s_reg.O
        
        # Commands
        nbits = 4   # Good for up to 16 commands
        PowerOff = m.Bits[nbits](0)
        PowerOn  = m.Bits[nbits](1) # not used
        Read     = m.Bits[nbits](2)
        Write    = m.Bits[nbits](3)
        Idle     = m.Bits[nbits](4)

        # Convenient shortcuts
        cur_state = self.state_reg.O
        cmd       = self.o_reg.O
        rcv_in    = self.r_reg.O

        # Enable registers only where needed (why? maybe not strictly necessary?)
        # TODO can try wiring all enables to 1'b1 and see if anything changes...?

        # MemInit uses r_reg, redundancy reg
        self.r_reg.CE          @= (cur_state == State.MemInit)
        self.redundancy_reg.CE @= (cur_state == State.MemInit)


        # Send uses s_reg
        self.s_reg.CE          @= (cur_state == State.Send)

        # MemOff, MemOn use o_reg
        self.o_reg.CE          @= ((cur_state == State.MemOff) | (cur_state == State.MemOn))

        # So, @mydecorator is just an easier way of saying myfunc = mydecorator(myfunc)

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

            # Dummy value for now
            WakeAcktT       = m.Bits[16](1)

            # State MemInit
            if cur_state == State.MemInit:
                # Receive redundancy: output of receive reg => input of redundancy reg
                redundancy_data = self.r_reg.O
                next_state = State.MemOff

            # State MemOff
            elif ((cur_state == State.MemOff) & (cmd == PowerOff)):
                next_state = State.MemOff

            elif ((cur_state == State.MemOff) & (cmd == PowerOn)):
                # Send(WakeAck) [to client requesting power-on]
                data_to_client = WakeAcktT
                next_state = State.MemOn

            # State MemOn
            elif ((cur_state == State.MemOn) & (cmd == PowerOff)):
                next_state = State.MemOff

            elif ((cur_state == State.MemOn) & (cmd == Idle)):
                next_state = State.MemOn

            # READ: get address from client, send back data from mem
            # Assumes data_from_mem magically appears when addr changes (I guess)
            elif ((cur_state == State.MemOn) & (cmd == Read)):
                addr_to_mem = self.r_reg.O     # Receive(Addr) [from client requesting read]
                data_to_client = data_from_mem # Send(Data)    [to requesting client]
                next_state = State.MemOn

            # WRITE: get address and data from client, send to memory
            # messages from client arrive via r_reg (receive reg)
            elif ((cur_state == State.MemOn) & (cmd == Write)):
                addr_to_mem = self.r_reg.O      # Receive(Addr) [from client requesting mem write]
                data = self.r_reg.O      # Receive(Data) [from client requesting mem write]
                next_state = State.MemOn

            # else: cur_state == cur_state

            # Wire up our shortcuts
            self.state_reg.I      @= next_state
            self.s_reg.I          @= data_to_client
            self.redundancy_reg.I @= redundancy_data


##############################################################################

# FIFO = make_FIFO(HSFloatIn, HSFloatOut, 4)
# m.compile("examples/build/FIFO", FIFO, output="coreir-verilog")

def show_verilog():
    FSM = StateMachine()
    m.compile("steveri/tmpdir/fsm", FSM, output="coreir-verilog")
    with open('steveri/tmpdir/fsm.v', 'r') as f: print(f.read())

# show_verilog()
print("==============================================================================")
print("okay so that was the verilog")
print("==============================================================================")


#==============================================================================
#==============================================================================
#==============================================================================
import fault

def test_state_machine_fault():
    
    def step(): tester.step(2)

    # Commands
    PowerOff = m.Bits[4](0)
    PowerOn  = m.Bits[4](1)

    Definition = StateMachine()
    tester = fault.Tester(Definition, Definition.CLK)

    tester.print("beep boop testing state_machine circuit\n")
    
    tester.circuit.current_state.expect(State.MemInit)
    tester.print("beep boop successfully booted in state MemInit maybe\n")

    step()

    tester.print("beep boop and now we should be in state Memoff\n")
    tester.circuit.current_state.expect(State.MemOff)

    # Check contents of redundancy_reg
    tester.print("beep boop redundancy data is now O=%d\n", tester.circuit.redundancy_reg.O)
    tester.circuit.redundancy_reg.O.expect(0)
    tester.print("beep boop passed initial redundancy data check\n")

    tester.print("----------------------\n")
    tester.print("beep boop ...and now we fail\n")

    tester.step(2)
    tester.circuit.current_state.expect(State.MemOn) # no



    # Build:
    # opcode = ConfigReg(name="config_reg")(io.config_data, CE=io.config_en)

    # Test:
    # tester.circuit.config_reg.conf_reg.value = i
    # tester.step(2)
    # tester.circuit.config_reg.conf_reg.O.expect(i)





    ################################################################

    # tester.compile_and_run("verilator", flags=["-Wno-fatal"])

    # Fault supports peeking, expecting, and printing internal
    # signals. For the verilator target, you should use the keyword
    # argument magma_opts with "verilator_debug" set to true. This
    # will cause coreir to compile the verilog with the required debug
    # comments. Example:

    # tester.compile_and_run("verilator", flags=["-Wno-fatal"], 
    # magma_opts={"verilator_debug": True}, directory="build")
    tester.compile_and_run(
        "verilator",
        flags=["-Wno-fatal"],
        magma_opts={"verilator_debug": True},
        directory="tmpdir",
    )
    




# show_verilog()
# 
# print("==============================================================================")
# print("okay so that was the verilog")
# print("==============================================================================")





test_state_machine_fault()
