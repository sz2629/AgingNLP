#!/bin/bash
# Step 1: run MedTaggerIE with the Cardiovascular rule model over clinical notes.
#
# Concepts extracted (NORM values; rules in models/Cardiovascular/rules):
#   Dizziness - dizzy, dizziness, lightheaded, vertigo, room spinning, feels faint, near-syncope, symptomatic (orthostatic) hypotension
#
# Usage: bash run_MedTagger-fit-cardiovascular_step1.sh [INPUT_DIR] [OUTPUT_DIR]
set -euo pipefail
cd "$(dirname "$0")"

INPUT_DIR="${1:-../notes}"
OUTPUT_DIR="${2:-data/output}"
RULES_DIR="models/Cardiovascular"
JAR="MedTagger-fit-context.jar"
[ -f "$JAR" ] || JAR="../MedTagger-fit-context.jar"
[ -f "$JAR" ] || JAR="../delirium/MedTagger-fit-context.jar"

mkdir -p "$OUTPUT_DIR"
java -Xms512M -Xmx2000M -jar "$JAR" "$INPUT_DIR" "$OUTPUT_DIR" "$RULES_DIR"
