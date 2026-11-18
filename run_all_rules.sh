#!/bin/bash
# Run MedTagger with every rule model in the repo over notes/.
# Usage: bash run_all_rules.sh [INPUT_DIR] [OUTPUT_ROOT]
set -euo pipefail
cd "$(dirname "$0")"

INPUT_DIR="${1:-notes}"
OUT_ROOT="${2:-results}"
JAR="delirium/MedTagger-fit-context.jar"

find . -type d -name rules -not -path "./.git/*" | sort | while read -r R; do
  RULES="$(dirname "$R")"
  NAME="$(basename "$RULES")"
  OUT="$OUT_ROOT/$NAME"
  mkdir -p "$OUT"
  echo "Running $NAME"
  java -Xms512M -Xmx2000M -jar "$JAR" "$INPUT_DIR" "$OUT" "$RULES"
done

echo "Done. Results are in $OUT_ROOT/"
