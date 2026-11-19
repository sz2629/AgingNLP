#!/bin/bash
# Step 1: run MedTaggerIE with the Musculoskeletal rule model over clinical notes.
#
# Concepts extracted (NORM values; rules in models/Musculoskeletal/rules):
#   Frailty  - frail, frailty, Clinical Frailty Scale 5-9, exhaustion, low activity
#   Weakness - generalized/proximal weakness, reduced strength (0-4/5), legs feel heavy / hard to lift
#
# Usage: bash run_MedTagger-fit-musculoskeletal_step1.sh [INPUT_DIR] [OUTPUT_DIR]
set -euo pipefail
cd "$(dirname "$0")"

INPUT_DIR="${1:-../notes}"
OUTPUT_DIR="${2:-data/output}"
RULES_DIR="models/Musculoskeletal"
JAR="MedTagger-fit-context.jar"
[ -f "$JAR" ] || JAR="../MedTagger-fit-context.jar"
[ -f "$JAR" ] || JAR="../delirium/MedTagger-fit-context.jar"

mkdir -p "$OUTPUT_DIR"
java -Xms512M -Xmx2000M -jar "$JAR" "$INPUT_DIR" "$OUTPUT_DIR" "$RULES_DIR"
