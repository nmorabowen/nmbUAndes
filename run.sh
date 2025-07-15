#!/bin/bash
#SBATCH --exclude=node17,node18
#SBATCH --job-name=nmbTEMP
#SBATCH --ntasks=8
#SBATCH --output=log.log

pwd; hostname; date

export OMP_NUM_THREADS=1
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/mnt/nfshare/lib

# Inicia monitoreo del uso de memoria total del nodo y de cada proceso OpenSeesMP
( while true; do
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    echo "$TIMESTAMP" >> memtrack_node.txt
    free -h >> memtrack_node.txt
    echo "-----------" >> memtrack_node.txt

    # Monitorear todos los procesos relacionados con OpenSeesMP
    pgrep -af openseesmp | while read PID CMD; do
        echo "PID: $PID" >> memtrack_node.txt
        ps -p $PID -o pid,%mem,rss,vsz,cmd --no-headers >> memtrack_node.txt
    done
    echo "======================" >> memtrack_node.txt
    sleep 30
done ) &

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
