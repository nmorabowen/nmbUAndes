#!/bin/bash
#SBATCH --exclude=node17,node18
#SBATCH --job-name=nmbTEMP
#SBATCH --ntasks=8
#SBATCH --output=log.log

pwd; hostname; date

export OMP_NUM_THREADS=1
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/mnt/nfshare/lib

# Ejecutar simulación
SECONDS=0
mpirun /mnt/nfshare/bin/openseesmp-16102024-explicitbathe main.tcl
EXIT_CODE=$?
DURATION=$SECONDS

echo "Elapsed: $DURATION seconds."
echo "Code finished with exit code $EXIT_CODE."
echo "LARGA VIDA AL LADRUÑO!!!"

# Definir rutas
ORIG_PATH=$(pwd)
REL_PATH="${ORIG_PATH#/mnt/deadmanschest/nmorabowen/}"
DEST_BASE="/mnt/krakenschest/home/nmorabowen"
DEST_PATH="${DEST_BASE}/${REL_PATH}"

# Crear status.txt
STATUS_FILE="status.txt"
{
  echo "Execution Date: $(date)"
  echo "Executed By: $(whoami)"
  echo "Duration: $DURATION seconds"
  echo "Exit Code: $EXIT_CODE"
  echo "Original Path: $ORIG_PATH"
  echo "Destination Path: $DEST_PATH"
} > "$STATUS_FILE"

# Solo continuar si el job terminó bien
if [ "$EXIT_CODE" -eq 0 ]; then
  echo "📁 Copiando a destino: $DEST_PATH"
  mkdir -p "$DEST_PATH"

  # Copiar todo excepto el status.txt (que se copiará luego)
  rsync -a --exclude="status.txt" ./ "$DEST_PATH/"

  if [ $? -eq 0 ]; then
    echo "✅ Copia completada. Limpiando carpeta original (excepto status.txt)..."
    find . -mindepth 1 ! -name "status.txt" -exec rm -rf {} +
    echo "🧼 Limpieza completa."
  else
    echo "⚠️ Error en la copia. No se elimina nada."
  fi
else
  echo "❌ Simulación fallida. No se copia ni borra nada."
fi
