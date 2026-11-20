#!/bin/bash
# Step 1: run MedTaggerIE with the Deprescribing Discussion rule model over clinical notes.
#
# Concepts extracted (NORM values; rules in models/Deprescribing_Discussion/rules):
#   Deprescribing_discussion - deprescribing, tapered off, discontinued, stopped, dose reduced, reduce the gabapentin dose, wean off
#
# Usage: bash run_MedTagger-fit-deprescribing_discussion_step1.sh [INPUT_DIR] [OUTPUT_DIR]
set -euo pipefail
cd "$(dirname "$0")"

INPUT_DIR="${1:-../notes}"
OUTPUT_DIR="${2:-data/output}"
RULES_DIR="models/Deprescribing_Discussion"
JAR="MedTagger-fit-context.jar"
[ -f "$JAR" ] || JAR="../MedTagger-fit-context.jar"
[ -f "$JAR" ] || JAR="../delirium/MedTagger-fit-context.jar"

mkdir -p "$OUTPUT_DIR"
java -Xms512M -Xmx2000M -jar "$JAR" "$INPUT_DIR" "$OUTPUT_DIR" "$RULES_DIR"
