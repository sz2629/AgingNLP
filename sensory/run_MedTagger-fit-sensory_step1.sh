#!/bin/bash
# Step 1: run MedTaggerIE with the Sensory rule model over clinical notes.
#
# Concepts extracted (NORM values; rules in models/Sensory/rules):
#   Vision_impairment - low vision, blurry vision, legally blind, macular degeneration, visual acuity 20/50 or worse, trouble reading / seeing at night
#   Hearing_impairment - hearing loss, hard of hearing, HOH, deaf, presbycusis, uses hearing aids, cochlear implant
#   Numbness_neuropathy - numbness, tingling, pins and needles, burning feet, peripheral neuropathy, decreased vibration sense, insensate to monofilament
#
# Usage: bash run_MedTagger-fit-sensory_step1.sh [INPUT_DIR] [OUTPUT_DIR]
set -euo pipefail
cd "$(dirname "$0")"

INPUT_DIR="${1:-../notes}"
OUTPUT_DIR="${2:-data/output}"
RULES_DIR="models/Sensory"
JAR="MedTagger-fit-context.jar"
[ -f "$JAR" ] || JAR="../MedTagger-fit-context.jar"
[ -f "$JAR" ] || JAR="../delirium/MedTagger-fit-context.jar"

mkdir -p "$OUTPUT_DIR"
java -Xms512M -Xmx2000M -jar "$JAR" "$INPUT_DIR" "$OUTPUT_DIR" "$RULES_DIR"
