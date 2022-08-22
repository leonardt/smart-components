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

        # StateMachine.Register_inst1?
        self.s_reg = m.Register(
            T=m.Bits[16],
            has_enable=True,
        )()

        # StateMachine.Register_inst2?
        self.r_reg = m.Register(
            T=m.Bits[16],
            has_enable=True,
        )()

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
        




##############################################################################
        # FIXME added inits to avoid errors

        # % python state_machine_debug.py |& grep driven
        # ERROR:magma:StateMachine.Register_inst0.I not driven (state_reg?)
        # ERROR:magma:StateMachine.Register_inst1.I not driven (s_reg?)
        # ERROR:magma:StateMachine.Register_inst4.I not driven (redundancy_reg)
        
        # self.state_reg.I      @= m.Bits[2](0)  # StateMachine.Register_inst4
        # self.s_reg.I          @= m.Bits[16](0) # StateMachine.Register_inst4
        # self.redundancy_reg.I @= m.Bits[16](0) # StateMachine.Register_inst4
##############################################################################





        ################################################################
        # This is the state machine we want to implement

        # State MemInit
        # Enable receive register 'r_reg'
        # GOTO MemOff

        # State MemOff
        # Enable offer/cmd reg 'o_reg'
        # If cmd == poweroff => GOTO MemOff
        # if cmd == poweron  => GOTO Send

        # State Send
        # Enable send reg 's_reg'
        # send wakeAckT
        # GOTO MemOn

        # State MemOn
        # Enable offer/cmd reg 'o_reg'
        # if cmd == poweroff => goto memoff
        # if cmd == poweron => stay in state 2 (memon)
        ################################################################

        # States
        MemInit = m.Bits[2](0)
        MemOff  = m.Bits[2](1)
        Send    = m.Bits[2](2)
        MemOn   = m.Bits[2](3)

        # Commands
        PowerOff = m.Bits[4](0)
        PowerOn  = m.Bits[4](1)

        # Convenient shortcuts
        cur_state = self.state_reg.O
        cmd       = self.o_reg.O
        rcv       = self.r_reg.O

        # Enable registers only where needed (why? maybe not strictly necessary?)
        # TODO can try wiring all enables to 1'b1 and see if anything changes...?

        # MemInit uses r_reg, redundancy reg
        self.r_reg.CE          @= (cur_state == MemInit)
        self.redundancy_reg.CE @= (cur_state == MemInit)

        # Send uses s_reg
        self.s_reg.CE          @= (cur_state == Send)

        # MemOff, MemOn use o_reg
        self.o_reg.CE          @= ((cur_state == MemOff) | (cur_state == MemOn))

        # state update functions
        # if state == MemInit: state = MemOff
        # if cur_state == MemInit: cur_state = MemOff
        # if cur_state == 0: cur_state = 1

        # So, @mydecorator is just an easier way of saying
        # myfunc = mydecorator(myfunc)

        # Note inline_combinational() is not very robust i.e.
        # very particular about indentation even on comments, also
        # should avoid e.g. one-line if-then ('if a: b=1'),
        # multiple statements on one line separated by semicolon etc.

        @m.inline_combinational()
        def controller():

            # ehere is a comment



            # Dummy values for now
            send_data       = m.Bits[16](0)
            redundancy_data = m.Bits[16](0)
            WakeAcktT       = m.Bits[16](1)

            if cur_state == MemInit:
                redundancy_data = rcv; next_state = MemOff

            elif ((cur_state == MemOff) & (cmd == PowerOff)):
                next_state = MemOff
            elif ((cur_state == MemOff) & (cmd == PowerOn )):
                next_state = Send

            elif cur_state == Send:
                send_data  = WakeAcktT
                next_state = MemOn

            elif ((cur_state == MemOn) & (cmd == PowerOff)):
                next_state = MemOff
            elif ((cur_state == MemOn) & (cmd == PowerOn )):
                next_state = MemOn

            # Wire up our shortcuts
            self.state_reg.I      @= next_state
            self.s_reg.I          @= send_data
            self.redundancy_reg.I @= redundancy_data

#         def receive_redundancy():
#             # WRITEME
#             # ?? return (rcv == RedundancyT)
#             return True
# 
#         def send_wakeAckT():
#             # WRITEME
#             return True


##############################################################################
# UNUSED (for now)
##############################################################################
        def controller_alt():
            next_state = state_machine([
                MemInit, receive_redundancy,  MemOff,

                MemOff, cmd == PowerOff,      MemOff,
                MemOff, cmd == PowerOn,       Send  ,

                Send,   cmd == send_wakeAckT, MemOn ,

                MemOn,  cmd == PowerOff,      MemOff,
                MemOn,  cmd == PowerOn,       MemOn ,
            ])
            self.state_reg.I @= next_state



        def state_machine (smlist):
            # assert n_elements%3 == 0?
            while smlist:
                state1 = smlist.pop(0); # assert type int?
                action = smlist.pop(0); # assert type bool or func?
                state2 = smlist.pop(0); # assert type int?
                if cur_state == state1:
                    # DO NOT eval action unless we are in appropriate state!
                    if type(action) != bool: action = action()
                    if action:
                        return state2

            # ERROR? ASSERT?
            return state1
##############################################################################

# FIFO = make_FIFO(HSFloatIn, HSFloatOut, 4)
# m.compile("examples/build/FIFO", FIFO, output="coreir-verilog")

def show_verilog():
    FSM = StateMachine()
    m.compile("tmpdir/fsm0", FSM, output="coreir-verilog")
    with open('tmpdir/fsm0.v', 'r') as f: print(f.read())

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
