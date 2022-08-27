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

class StateMachine(CoopGenerator):
    def _decl_attrs(self, **kwargs):
        super()._decl_attrs(**kwargs)
        self.num_states = 4

        # States
        nbits = 2
        self.MemInit = m.Bits[nbits](0)
        self.MemOff  = m.Bits[nbits](1)
        self.Send    = m.Bits[nbits](2)
        self.MemOn   = m.Bits[nbits](3)




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

        # StateMachine.Register_inst0?
        self.state_reg = m.Register(
            init=m.Bits[2](0),
            has_enable=False,
        )()

        # "send" reg
        # StateMachine.Register_inst1?
        self.s_reg = m.Register(
            T=m.Bits[16],
            has_enable=True,
        )()

        # "receive" reg
        # StateMachine.Register_inst2?
        self.r_reg = m.Register(
            T=m.Bits[16],
            has_enable=True,
        )()

        # "offer" (cmd) reg
        # StateMachine.Register_inst3?
        self.o_reg = m.Register(
            T=m.Bits[4],
            has_enable=True,
        )()

        # StateMachine.Register_inst4
        self.redundancy_reg = m.Register(
            T=m.Bits[16],
            has_enable=True,
        )()

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
        self.r_reg.CE          @= (cur_state == self.MemInit)
        self.redundancy_reg.CE @= (cur_state == self.MemInit)

        # Send uses s_reg
        self.s_reg.CE          @= (cur_state == self.Send)

        # MemOff, MemOn use o_reg
        self.o_reg.CE          @= ((cur_state == self.MemOff) | (cur_state == self.MemOn))

        # So, @mydecorator is just an easier way of saying myfunc = mydecorator(myfunc)

        # ==============================================================================
        # Note inline_combinational() is not very robust i.e. very particular
        # about indentation even on comments, also should avoid e.g. one-line
        # if-then ('if a: b=1'), multiple statements on one line separated by semicolon etc.

        @m.inline_combinational()
        def controller():

            # Dummy values for now
            addr            = m.Bits[16](0)
            send_data       = m.Bits[16](0)
            redundancy_data = m.Bits[16](0)
            WakeAcktT       = m.Bits[16](1)

            # State MemInit
            if cur_state == self.MemInit:
                redundancy_data = self.r_reg.O    # Receive redundancy: output of receive reg => input of redundancy r
                next_state = self.MemOff

            # State MemOff
            elif ((cur_state == self.MemOff) & (cmd == PowerOff)):
                next_state = self.MemOff

            elif ((cur_state == self.MemOff) & (cmd == PowerOn )):
                send_data  = WakeAcktT      # Send(WakeAck)
                next_state = self.MemOn

            # State MemOn
            elif ((cur_state == self.MemOn) & (cmd == PowerOff)):
                next_state = self.MemOff

            elif ((cur_state == self.MemOn) & (cmd == Idle )):
                next_state = self.MemOn

            # READ: get address from client, send back data from mem
            elif ((cur_state == self.MemOn) & (cmd == Read )):
                # TODO Receive(Addr)
                # TODO Send(Data)
                next_state = self.MemOn

            # READ: get address and data from client, send to memory
            # messages from client arrive via r_reg (receive reg)
            elif ((cur_state == self.MemOn) & (cmd == Write )):
                # TODO Receive(Addr)
                addr = self.r_reg.O
                # TODO Receive(Data)
                data = self.r_reg.O
                next_state = self.MemOn



            # Wire up our shortcuts
            self.state_reg.I      @= next_state
            self.s_reg.I          @= send_data
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

import fault

def test_state_machine_fault():
    
    # generator = SRAM_FEATURE_TABLE[base][frozenset(mixins)]
    # Definition = generator(ADDR_WIDTH, DATA_WIDTH, debug=True, **params)
    # tester = fault.Tester(Definition, Definition.CLK)

    # States
    MemInit = m.Bits[2](0)
    MemOff  = m.Bits[2](1)
    Send    = m.Bits[2](2)
    MemOn   = m.Bits[2](3)
    
    # Commands
    PowerOff = m.Bits[4](0)
    PowerOn  = m.Bits[4](1)

    Definition = StateMachine()
    tester = fault.Tester(Definition, Definition.CLK)

    print("beep boop testing state_machine circuit")
    
    # See _devl_io_ in StateMachine() for 'current_state'
    tester.circuit.current_state.expect(MemInit) # yes
    print("beep boop successful booted in state MemInit maybe")

    # if cur_state == MemInit:
    #     redundancy_data = rcv; next_state = MemOff

    tester.step(1)
    print("beep boop and now we should be in state Memoff")
    tester.circuit.current_state.expect(MemOff)

    # print("beep boop redundancy data is now", tester.circuit.redundancy_reg.O)
    # NOPE

    # print("beep boop redundancy data is now", tester.circuit.Register_inst4.O)
    # beep boop redundancy data is now <fault.wrapper.PortWrapper object at 0x7f8f42444fa0>

    print("beep boop redundancy data is now")
    # tester.print("O=%d\n", tester.circuit.config_reg.conf_reg.O)
    tester.print("O=%d\n", tester.circuit.Register_inst4.O)
    # <STDOUT>
    # O=0
    # </STDOUT>
    # <STDERR>

    # print("beep boop redundancy data is now %d" % tester.circuit.Register_inst4.O)
    # TypeError: %d format: a number is required, not PortWrapper

    print("beep boop redundancy data is now %d" % tester.circuit.Register_inst4.O.peek())






    print("\n----------------------")
    print("beep boop now we fail")
    tester.circuit.current_state.expect(MemOn) # no



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
    




show_verilog()
exit()

print("==============================================================================")
print("okay so that was the verilog")
print("==============================================================================")





test_state_machine_fault()
