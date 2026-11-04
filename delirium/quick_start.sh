#!/bin/bash
# Quick start for the delirium NLP pipeline:
#   step 1 - MedTagger extracts delirium/CAM concepts  -> OUTPUT_DIR/*.ann
#   step 2 - post-processing applies the CAM rules     -> RESULT_CSV, MEDTATOR_DIR/*.xml
# Usage: cp .env.example .env   (edit paths)   then   bash quick_start.sh
set -euo pipefail

cd "$(dirname "$0")"

if [ -f .env ]; then
  set -a; source .env; set +a
else
  echo "No .env found, using defaults from .env.example"
  set -a; source .env.example; set +a
fi

abs() { case "$1" in /*) echo "$1" ;; *) echo "$PWD/$1" ;; esac; }
export INPUT_DIR="$(abs "$INPUT_DIR")"
export OUTPUT_DIR="$(abs "$OUTPUT_DIR")"
export RULES_DIR="$(abs "$RULES_DIR")"
export MEDTATOR_DIR="$(abs "$MEDTATOR_DIR")"
export RESULT_CSV="$(abs "$RESULT_CSV")"

command -v java >/dev/null || { echo "Java (1.8+) is required"; exit 1; }
[ -f "$MEDTAGGER_JAR" ] || { echo "MedTagger jar not found: $MEDTAGGER_JAR"; exit 1; }
[ -d "$INPUT_DIR" ]     || { echo "Input folder not found: $INPUT_DIR"; exit 1; }
[ -d "$RULES_DIR" ]     || { echo "Rules folder not found: $RULES_DIR"; exit 1; }
mkdir -p "$OUTPUT_DIR" "$MEDTATOR_DIR"

echo "== Step 1: MedTagger ($RULES_DIR)"
java $JAVA_OPTS -jar "$MEDTAGGER_JAR" "$INPUT_DIR" "$OUTPUT_DIR" "$RULES_DIR"

echo "== Step 2: post-processing"
python3 run_post_processting_step2.py

echo "== Done"
echo "  concepts : $OUTPUT_DIR/*.ann"
echo "  summary  : $RESULT_CSV"
echo "  MedTator : $MEDTATOR_DIR/*.xml"
