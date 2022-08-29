# To see state machine diagram:
    display state_machine.png

# To run state machine
    python state_machine.py

# To see output from state machine run
    cat tmpdir/obj_dir/StateMachine.log | sed 's/beep/\
beep/g'

# To compare state machine verilog vs. prev successful run(s)
    diff ref/StateMachine.v build/StateMachine.v && echo PASS || echo FAIL

# To automatically run, see output, and compare to prev
    ./test_machine.sh
