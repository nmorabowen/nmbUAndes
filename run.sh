#!/bin/bash
#SBATCH --exclude=node17,node18
#SBATCH --job-name=nmbTEMP
#SBATCH --ntasks=8                    # Valor por defecto si no se pasa desde afuera
#SBATCH --output=log.log

pwd; hostname; date

export OMP_NUM_THREADS=1
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/mnt/nfshare/lib

SECONDS=0
mpirun /mnt/nfshare/bin/openseesmp-26062025 main.tcl

echo "Elapsed: $SECONDS seconds."
echo "Code finished successfully."
echo "LARGA VIDA AL LADRUÑO!!!"
