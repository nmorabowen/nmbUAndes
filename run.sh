#!/bin/bash
#SBATCH --job-name=nmbTEMP
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=48:00:00
#SBATCH --partition=general
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err
#SBATCH --exclude=node17,node18

set -euo pipefail

echo "PWD: $(pwd)"; echo "HOST: $(hostname)"; date

export OMP_NUM_THREADS=1
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}:/mnt/nfshare/lib"

JOBLOG="memtrack_node_%j.txt"
LOGFILE="${JOBLOG//%j/${SLURM_JOB_ID:-nojob}}"
{
  echo "Memory tracking started at $(date)"
  echo "JobID: ${SLURM_JOB_ID:-NA}  Node: $(hostname)"
  echo "Tasks: ${SLURM_NTASKS:-NA}  Cpus/Task: ${SLURM_CPUS_PER_TASK:-NA}"
} > "$LOGFILE"

# ─────────────────────────────────────────────────────────────
# Cleanup monitor on exit
cleanup() {
  echo "[$(date)] Killing monitor PID ${MONITOR_PID:-NA}" >> "$LOGFILE" || true
  [[ -n "${MONITOR_PID:-}" ]] && kill "$MONITOR_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# ─────────────────────────────────────────────────────────────
# Start memory tracking in background (SLURM-aware)
(
  # Poll both node memory and per-task memory via sstat (cross-node)
  while :; do
    ts="$(date '+%Y-%m-%d %H:%M:%S')"
    echo "$ts" >> "$LOGFILE"

    # Node total memory use (this node)
    if command -v free >/dev/null 2>&1; then
      used_mb=$(free -m | awk '/^Mem:/ {print $3}')
      echo "Node Mem Used: ${used_mb} MB" >> "$LOGFILE"
    fi

    # Per-task RSS via sstat (aggregates across nodes)
    if [[ -n "${SLURM_JOB_ID:-}" ]] && command -v sstat >/dev/null 2>&1; then
      # MaxRSS and AveRSS in KB; format them and append
      sstat -j "$SLURM_JOB_ID" --format=JobID,MaxRSS,AveRSS,MaxVMSize,AveVMSize -P \
        | awk -F'|' 'NR==1 || $2!="" {print "sstat:", $0}' >> "$LOGFILE" || true
    fi

    echo "======================" >> "$LOGFILE"
    sleep 30
  done
) & MONITOR_PID=$!

# ─────────────────────────────────────────────────────────────
# Launch OpenSeesMP analysis (prefer srun under SLURM)
SECONDS=0

# If your OpenSees uses MPI ranks = ntasks, srun will fan out
srun --mpi=pmix_v3 /mnt/nfshare/bin/opensees-14072025 main.tcl

# ─────────────────────────────────────────────────────────────
echo "Elapsed: $SECONDS seconds."
echo "Code finished successfully."
echo "LARGA VIDA AL LADRUÑO!!!"
