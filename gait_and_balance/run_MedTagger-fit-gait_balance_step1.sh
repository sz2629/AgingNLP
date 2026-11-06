#!/bin/bash
# Step 1: run MedTagger with the gait and balance rules.
# Usage: bash run_MedTagger-fit-gait_balance_step1.sh [INPUT_DIR] [OUTPUT_DIR] [RULES_DIR]
set -euo pipefail
cd "$(dirname "$0")"

INPUT_DIR="${1:-data/input}"
OUTPUT_DIR="${2:-data/output}"
RULES_DIR="${3:-models/GAIT_BALANCE}"

# Use a local jar if present, otherwise reuse the one shipped in ../delirium
JAR="MedTagger-fit-context.jar"
if [ ! -f "$JAR" ]; then
  JAR="../delirium/MedTagger-fit-context.jar"
fi
if [ ! -f "$JAR" ]; then
  echo "ERROR: MedTagger-fit-context.jar not found in gait_and_balance/ or delirium/" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"
java -Xms512M -Xmx2000M -jar "$JAR" "$INPUT_DIR" "$OUTPUT_DIR" "$RULES_DIR"
