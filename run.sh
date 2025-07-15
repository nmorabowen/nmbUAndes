#!/bin/bash
#SBATCH --exclude=node17,node18
#SBATCH --job-name=nmbTEMP
#SBATCH --ntasks=8
#SBATCH --output=log.log

pwd; hostname; date

export OMP_NUM_THREADS=1
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/mnt/nfshare/lib

LOGFILE="memtrack_node.txt"

# Ensure file starts clean
echo "Memory tracking started at $(date)" > "$LOGFILE"

# Start memory logging loop in background
(
while true; do
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    echo "$TIMESTAMP" >> "$LOGFILE"

    # Capture total memory used (in GiB or MiB)
    USED=$(free -h | awk '/^Mem:/ {print $3}')
    echo "Mem: $USED" >> "$LOGFILE"

    echo "-----------" >> "$LOGFILE"

    # Get the current mpirun PID (may not be started yet)
    MPIRUN_PID=$(pgrep -f "mpirun.*openseesmp")

    if [[ -n "$MPIRUN_PID" ]]; then
        # Get child PIDs of mpirun (each MPI rank)
        PIDS=$(ps --ppid $MPIRUN_PID -o pid=)
        for PID in $PIDS; do
            CMD=$(ps -p $PID -o cmd=)
            echo "PID: $PID" >> "$LOGFILE"
            ps -p $PID -o pid,%mem,rss,vsz,cmd --no-headers >> "$LOGFILE"
        done
    fi

    echo "======================" >> "$LOGFILE"
    sleep 30
done
) &


# Guarda el PID del proceso de monitoreo
MONITOR_PID=$!

# Ejecuta el análisis con OpenSeesMP
SECONDS=0
mpirun /mnt/nfshare/bin/opensees-14072025 main.tcl
# Al terminar, mata el monitoreo
kill $MONITOR_PID

echo "Elapsed: $SECONDS seconds."
echo "Code finished successfully."
echo "LARGA VIDA AL LADRUÑO!!!"
