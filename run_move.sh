#!/bin/bash
#SBATCH --exclude=node17,node18
#SBATCH --job-name=nmbTEMP
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=48:00:00
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err

set -euo pipefail

echo "PWD: $(pwd)"; echo "HOST: $(hostname)"; date

# --- Env ---
export OMP_NUM_THREADS=1
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}:/mnt/nfshare/lib"

# --- Run simulation ---
SECONDS=0
EXIT_CODE=0

# Prefer srun under SLURM; if you must use mpirun, replace the next line with your mpirun line.
if ! srun --mpi=pmix_v3 /mnt/nfshare/bin/opensees-14072025 main.tcl; then
  EXIT_CODE=$?
fi

DURATION=$SECONDS
echo "Elapsed: $DURATION seconds."
echo "Code finished with exit code $EXIT_CODE."
echo "LARGA VIDA AL LADRUÑO!!!"

# --- Paths ---
ORIG_PATH="$(pwd)"
ROOT_PREFIX="/mnt/deadmanschest/nmorabowen/"
DEST_BASE="/mnt/krakenschest/home/nmorabowen"
REL_PATH=""

if [[ "$ORIG_PATH/" == "$ROOT_PREFIX"* ]]; then
  # Mirror the tree under DEST_BASE
  REL_PATH="${ORIG_PATH#${ROOT_PREFIX}}"
else
  # Fallback: put under a flat folder name if outside expected root
  REL_PATH="$(basename "$ORIG_PATH")"
fi

DEST_PATH="${DEST_BASE}/${REL_PATH}"

# --- Status file ---
STATUS_FILE="status.txt"
{
  echo "Execution Date: $(date)"
  echo "Executed By: $(whoami)"
  echo "Duration: $DURATION seconds"
  echo "Exit Code: $EXIT_CODE"
  echo "Original Path: $ORIG_PATH"
  echo "Destination Path: $DEST_PATH"
  echo "SLURM JobID: ${SLURM_JOB_ID:-NA}"
  echo "Tasks: ${SLURM_NTASKS:-NA}  Cpus/Task: ${SLURM_CPUS_PER_TASK:-NA}"
} > "$STATUS_FILE"

# --- Safety rails for cleanup ---
safe_rm_tree() {
  local target="$1"

  # Never delete if path is empty, root, home, or equals destination
  if [[ -z "$target" || "$target" == "/" || "$target" == "$DEST_BASE" || "$target" == "$DEST_PATH" ]]; then
    echo "⚠️  Refusing to remove suspicious target: '$target'"
    return 1
  fi

  # Only remove contents, keep the folder and status.txt
  find "$target" -mindepth 1 ! -name "status.txt" -exec rm -rf {} + 2>/dev/null
}

# Ensure we don’t cleanup if script dies unexpectedly
trap 'echo "Trap fired; not cleaning source."; exit 1' INT TERM

# --- Copy + verify + cleanup ---
if [[ "$EXIT_CODE" -eq 0 ]]; then
  echo "📁 Copying to destination: $DEST_PATH"
  mkdir -p "$DEST_PATH"

  # Copy everything except status.txt first
  # -a: archive; -HAX preserve hardlinks/ACLs/xattrs if supported; --info=stats2: nicer stats
  # Use a simple 1-time retry pattern for transient issues.
  RSYNC_COMMON_OPTS=(-a --delete-excluded --exclude="status.txt" --info=stats2)
  if ! rsync "${RSYNC_COMMON_OPTS[@]}" ./ "$DEST_PATH/"; then
    echo "⚠️  First rsync attempt failed, retrying once..."
    sleep 3
    rsync "${RSYNC_COMMON_OPTS[@]}" ./ "$DEST_PATH/"
  fi

  # Also copy the final status.txt at the end so it reflects final metadata
  cp -f "$STATUS_FILE" "$DEST_PATH/"

  # Quick integrity check: ensure destination has main artifacts (e.g., main.tcl or results)
  if [[ -f "$DEST_PATH/main.tcl" || -d "$DEST_PATH" ]]; then
    echo "✅ Copy completed. Cleaning original folder (except $STATUS_FILE)..."

    # Extra safety: do not clean if DEST_PATH == ORIG_PATH
    if [[ "$DEST_PATH" == "$ORIG_PATH" ]]; then
      echo "⚠️  Destination equals source—refusing to clean."
      exit 1
    fi

    safe_rm_tree "$ORIG_PATH" || { echo "⚠️  Cleanup safeguards triggered; nothing deleted."; exit 1; }
    echo "🧼 Cleanup complete."
  else
    echo "⚠️  Destination seems incomplete; not deleting source."
    exit 1
  fi
else
  echo "❌ Simulation failed (exit $EXIT_CODE). Skipping copy and cleanup."
  exit "$EXIT_CODE"
fi
