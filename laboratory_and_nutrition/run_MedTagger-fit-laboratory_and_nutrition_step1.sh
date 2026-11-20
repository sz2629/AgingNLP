#!/bin/bash
# Step 1: run MedTaggerIE with the Laboratory and Nutrition rule model over clinical notes.
#
# Concepts extracted (NORM values; rules in models/Laboratory_and_Nutrition/rules):
#   Malnutrition - malnutrition, malnourished, cachexia, unintentional weight loss, lost 12 lbs, poor appetite / oral intake, temporal wasting, BMI < 18.5, albumin < 3.5
#
# Usage: bash run_MedTagger-fit-laboratory_and_nutrition_step1.sh [INPUT_DIR] [OUTPUT_DIR]
set -euo pipefail
cd "$(dirname "$0")"

INPUT_DIR="${1:-../notes}"
OUTPUT_DIR="${2:-data/output}"
RULES_DIR="models/Laboratory_and_Nutrition"
JAR="MedTagger-fit-context.jar"
[ -f "$JAR" ] || JAR="../MedTagger-fit-context.jar"
[ -f "$JAR" ] || JAR="../delirium/MedTagger-fit-context.jar"

mkdir -p "$OUTPUT_DIR"
java -Xms512M -Xmx2000M -jar "$JAR" "$INPUT_DIR" "$OUTPUT_DIR" "$RULES_DIR"
