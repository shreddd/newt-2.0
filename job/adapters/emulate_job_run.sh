#!/bin/sh
# Usage: echo "sleep 5; ls" | ./test.sh hi.out

process_dir="/tmp/newt_processes"
mkdir -p $process_dir
if [ ! -d "$process_dir" ]; then
    echo "The process folder could not be created!"
    exit 126
fi

tmpfile=$1
cmd=$2

# Run the command
touch "/tmp/newt_processes/$tmpfile"
eval "$cmd > /tmp/newt_processes/$tmpfile"&

process_pid=$!

echo $process_pid
time_start=`date -u +%s`

while ps -p $process_pid >> /dev/null
do
    echo "$process_pid; 999; $time_start; " > "/tmp/newt_processes/$process_pid.log"
    sleep 3
done

wait $process_pid
my_status=$?
time_end=`date -u +%s`
echo "$process_pid; $my_status; $time_start; $time_end" > "/tmp/newt_processes/$process_pid.log"
cat "/tmp/newt_processes/$tmpfile" >> "/tmp/newt_processes/$process_pid.log"
