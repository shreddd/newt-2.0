#!/bin/bash
# Usage: echo "sleep 5; ls" | ./test.sh hi.out


# Creates (if does not exist) the processes folder
process_dir="/tmp/newt_processes"
mkdir -p $process_dir
if [ ! -d "$process_dir" ]; then
    echo "The process folder could not be created!"
    exit 126
fi

# Get command and tempfile from input
tmpfile=$1
user=$2
cmd=$3

# Creates the tmpfile
touch "/tmp/newt_processes/$tmpfile.out"
touch "/tmp/newt_processes/$tmpfile.err"

# Run the command
eval "$cmd 2>/tmp/newt_processes/$tmpfile.err 1>/tmp/newt_processes/$tmpfile.out"&

process_pid=$!

echo $process_pid
time_start=`date -u +%s`
echo "$process_pid; $user; 999; $time_start; " > "/tmp/newt_processes/$process_pid.log"

wait $process_pid
my_status=$?
time_end=`date -u +%s`

# Print the completed status to the log file
echo "$process_pid; $user; $my_status; $time_start; $time_end" > "/tmp/newt_processes/$process_pid.log"

# Append the data from the command output (to the log file)
cat "/tmp/newt_processes/$tmpfile.out" >> "/tmp/newt_processes/$process_pid.log"
cat "/tmp/newt_processes/$tmpfile.err" >> "/tmp/newt_processes/$process_pid.log"
