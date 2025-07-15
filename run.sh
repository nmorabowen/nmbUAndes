#!/bin/bash
#SBATCH --exclude=node17,node18
#SBATCH --job-name=nmbTEMP
#SBATCH --ntasks=8
#SBATCH --output=log.log

pwd; hostname; date
export OMP_NUM_THREADS=1
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/mnt/nfshare/lib

LOGFILE="memtrack_node.txt"
echo "Memory tracking started at $(date)" > "$LOGFILE"

# Trap ensures we always kill the monitor on exit
cleanup() {
    echo "Killing monitor PID $MONITOR_PID"
    kill $MONITOR_PID 2>/dev/null
}
trap cleanup EXIT

# Start memory monitor in background
(
while true; do
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    echo "$TIMESTAMP" >> "$LOGFILE"
    USED=$(free -m | awk '/^Mem:/ {print $3 " MB"}')  # Numeric MB value
    echo "Mem: $USED" >> "$LOGFILE"
    echo "-----------" >> "$LOGFILE"

    MPIRUN_PID=$(pgrep -f "mpirun.*openseesmp")
    if [[ -n "$MPIRUN_PID" ]]; then
        CHILDREN=$(pgrep -P "$MPIRUN_PID")
        for PID in $CHILDREN; do
            RSS=$(ps -p $PID -o rss=)
            if [[ -n "$RSS" ]]; then
                echo "PID: $PID" >> "$LOGFILE"
                ps -p $PID -o pid,%mem,rss,vsz,cmd --no-headers >> "$LOGFILE"
            fi
        done
    else
        echo "No mpirun yet..." >> "$LOGFILE"
    fi

    echo "======================" >> "$LOGFILE"
    sleep 30
done
) &
MONITOR_PID=$!

SECONDS=0
mpirun /mnt/nfshare/bin/opensees-14072025 main.tcl
echo "Elapsed: $SECONDS seconds."
echo "Code finished successfully."
echo "LARGA VIDA AL LADRUÑO!!!"
