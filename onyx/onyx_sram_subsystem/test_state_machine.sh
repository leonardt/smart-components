#!/bin/bash

testdir=../tests
tmpdir=$testdir/tmpdir

echo "========================================================================"
echo "Running state machine and fault test: 'python state_machine.py'"
echo "------------------------------------------------------------------------"
# python state_machine.py || exit 13
(cd $testdir; pytest --disable-warnings test_state_machine.py) || exit 13


echo -n "========================================================================"
# echo    "stdout from test: cat tmpdir/obj_dir/StateMachine.log"
f=tmpdir/obj_dir/StateMachine.log
f=$tmpdir/obj_dir/StateMachine.log
cat $f | sed 's/beep/\
beep/g'

# cmd="diff ref/StateMachine.v $tmpdir/StateMachine.v"
# echo ""
# echo "========================================================================"
# echo "Compare verilog-out to previous runs: $cmd"
# $cmd && echo PASS || echo FAIL
