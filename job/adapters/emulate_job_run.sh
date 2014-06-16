#!/bin/sh
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
cmd=$2

# Creates the tmpfile
touch "/tmp/newt_processes/$tmpfile"

# Run the command
eval "$cmd > /tmp/newt_processes/$tmpfile"&

process_pid=$!

echo $process_pid
time_start=`date -u +%s`

while ps -p $process_pid >> /dev/null
do
    # Print the status to the log file as long as the PID exists in the ps command
    echo "$process_pid; 999; $time_start; " > "/tmp/newt_processes/$process_pid.log"
    sleep 3
done

wait $process_pid
my_status=$?
time_end=`date -u +%s`

# Print the completed status to the log file
echo "$process_pid; $my_status; $time_start; $time_end" > "/tmp/newt_processes/$process_pid.log"

# Append the data from the command output (to the log file)
cat "/tmp/newt_processes/$tmpfile" >> "/tmp/newt_processes/$process_pid.log"
