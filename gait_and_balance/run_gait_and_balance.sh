#!/bin/bash
# Full pipeline: step 1 (MedTagger extraction) + step 2 (post-processing).
# Usage: bash run_gait_and_balance.sh [INPUT_DIR] [OUTPUT_DIR] [RULES_DIR]
set -euo pipefail
cd "$(dirname "$0")"

INPUT_DIR="${1:-data/input}"
OUTPUT_DIR="${2:-data/output}"
RULES_DIR="${3:-models/GAIT_BALANCE}"

echo "== Step 1: MedTagger extraction =="
bash run_MedTagger-fit-gait_balance_step1.sh "$INPUT_DIR" "$OUTPUT_DIR" "$RULES_DIR"

echo "== Step 2: post-processing =="
python3 run_post_processing_step2.py --input_dir "$INPUT_DIR" --output_dir "$OUTPUT_DIR"

echo "Done. Note-level summary: data/summarized_result.csv"
