#!/bin/bash
# Step 1: run MedTaggerIE with the Medication Reconciliation Concern rule model over clinical notes.
#
# Concepts extracted (NORM values; rules in models/Medication_Reconciliation_Concern/rules):
#   Medication_reconciliation_concern - medication discrepancy, duplicate bottles / therapeutic duplication, not on the medication list, prescription never filled, conflicting medication lists
#
# Usage: bash run_MedTagger-fit-medication_reconciliation_concern_step1.sh [INPUT_DIR] [OUTPUT_DIR]
set -euo pipefail
cd "$(dirname "$0")"

INPUT_DIR="${1:-../notes}"
OUTPUT_DIR="${2:-data/output}"
RULES_DIR="models/Medication_Reconciliation_Concern"
JAR="MedTagger-fit-context.jar"
[ -f "$JAR" ] || JAR="../MedTagger-fit-context.jar"
[ -f "$JAR" ] || JAR="../delirium/MedTagger-fit-context.jar"

mkdir -p "$OUTPUT_DIR"
java -Xms512M -Xmx2000M -jar "$JAR" "$INPUT_DIR" "$OUTPUT_DIR" "$RULES_DIR"
