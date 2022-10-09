# For latest info see README at top of state_machine.py
# "single source of truth"

# To automatically run, see output, and compare to prev
    ./test_state_machine.sh

# To see state machine diagram:
    display state_machine.png

# To run state machine
    python state_machine.py

# To see output from state machine run
    cat tmpdir/obj_dir/StateMachine.log | sed 's/beep/\
beep/g'

# To compare state machine verilog vs. prev successful run(s)
    diff ref/StateMachine.v build/StateMachine.v && echo PASS || echo FAIL

# ------------------------------------------------------------------------
# Sample output as of 09/28/2022

```
beep boop TESTING STATE_MACHINE CIRCUIT
beep boop (tester data not valid yet so setting dfc valid=0)
beep boop (offer not valid yet so setting offer_valid=0)
beep boop -----------------------------------------------
beep boop Successfully booted in state MemInit maybe
beep boop   - sending redundancy data to MC
beep boop   - check that MC received redundancy data '17'
beep boop   - and now we should be in state Memoff
beep boop -----------------------------------------------
beep boop Check transition MemOff => MemOff on command PowerOff
beep boop -----------------------------------------------
beep boop Check transition MemOff => SendAck => MemOn on command PowerOn 752
beep boop   - check that MC sent WakeAck data '1'
beep boop   - and now we should be in state MemOn (0x3)
beep boop -----------------------------------------------
beep boop Check transition MemOn => MemOn on command Idle
beep boop Check transition MemOn => MemOff on command PowerOff
beep boop -----------------------------------------------
beep boop Check transition MemOff => SendAck => MemOn on command PowerOn 787
beep boop   - check that MC sent WakeAck data '1'
beep boop   - and now we should be in state MemOn (0x3)
beep boop -----------------------------------------------
beep boop check SRAM[66] == 10066 ?
beep boop -----------------------------------------------
beep boop Check transition MemOn => ReadAddr on command Read
beep boop Check that MC received mem addr '66'
beep boop Verify arrival in state ReadData
beep boop Check that MC sent data '10066'
beep boop Verify arrival in state MemOn
beep boop Verify *still* in state MemOn
beep boop -----------------------------------------------
beep boop Check transition MemOn => WriteAddr on command Write
beep boop Check that MC received mem addr '88'
beep boop Verify arrival in state WriteData
```


