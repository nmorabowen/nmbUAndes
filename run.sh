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

# ─────────────────────────────────────────────────────────────
# Cleanup monitor on exit
cleanup() {
    echo "Killing monitor PID $MONITOR_PID" >> "$LOGFILE"
    kill $MONITOR_PID 2>/dev/null
}
trap cleanup EXIT

# ─────────────────────────────────────────────────────────────
# Start memory tracking in background
(
# Wait for mpirun to appear
while true; do
    MPIRUN_PID=$(pgrep -f "mpirun.*opensees")
    if [[ -n "$MPIRUN_PID" ]]; then
        echo "Found mpirun PID $MPIRUN_PID at $(date)" >> "$LOGFILE"
        break
    fi
    echo "Waiting for mpirun..." >> "$LOGFILE"
    sleep 5
done

# Begin memory logging
while true; do
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    echo "$TIMESTAMP" >> "$LOGFILE"

    # Log total RAM usage in MB
    USED=$(free -m | awk '/^Mem:/ {print $3}')
    echo "Mem: ${USED} MB" >> "$LOGFILE"
    echo "-----------" >> "$LOGFILE"

    MPIRUN_PID=$(pgrep -f "mpirun.*opensees")
    CHILDREN=$(pgrep -P "$MPIRUN_PID")

    if [[ -z "$CHILDREN" ]]; then
        echo "No MPI child processes yet" >> "$LOGFILE"
    fi

    for PID in $CHILDREN; do
        if ps -p "$PID" > /dev/null; then
            echo "PID: $PID" >> "$LOGFILE"
            ps -p "$PID" -o pid,%mem,rss,vsz,cmd --no-headers >> "$LOGFILE"
        fi
    done

    echo "======================" >> "$LOGFILE"
    sleep 30
done
) &
MONITOR_PID=$!

# ─────────────────────────────────────────────────────────────
# Launch OpenSeesMP analysis
SECONDS=0
mpirun /mnt/nfshare/bin/opensees-14072025 main.tcl

# Clean up
echo "Elapsed: $SECONDS seconds."
echo "Code finished successfully."
echo "LARGA VIDA AL LADRUÑO!!!"
