#!/bin/bash
# Step 1: run MedTaggerIE with the GAIT_BALANCE rule model over clinical notes.
#
# Concepts extracted (NORM values; rules in models/GAIT_BALANCE/rules):
#   Gait_abnormality   - unsteady / shuffling / wide-based / slow(ed) / abnormal gait or walking
#   Balance_impairment - loss of balance, poor/reduced/impaired balance, imbalance, unsteadiness
#   Assistive_device   - walker, rollator, cane, wheelchair
#   Normal_gait        - "gait normal", "steady gait" (negative evidence)
# Negation/certainty/experiencer come from models/GAIT_BALANCE/context/contextRule.txt.
#
# Usage (from anywhere):  bash run_MedTagger-fit-gait_and_balance_step1.sh [INPUT_DIR] [OUTPUT_DIR]
# Defaults process the fake notes in ../notes and write .ann files to data/output.

set -euo pipefail
cd "$(dirname "$0")"

INPUT_DIR="${1:-../notes}"
OUTPUT_DIR="${2:-data/output}"
RULES_DIR="models/GAIT_BALANCE"
# Reuse the MedTagger jar shipped with the delirium model (or drop a copy into this folder).
JAR="MedTagger-fit-context.jar"
[ -f "$JAR" ] || JAR="../delirium/MedTagger-fit-context.jar"

mkdir -p "$OUTPUT_DIR"
java -Xms512M -Xmx2000M -jar "$JAR" "$INPUT_DIR" "$OUTPUT_DIR" "$RULES_DIR"
