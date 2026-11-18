#!/bin/bash
# Run every MedTaggerIE rule model in this repo over a folder of notes.
#
# Usage (from anywhere):  bash run_all_rules.sh [INPUT_DIR] [OUTPUT_ROOT]
#   INPUT_DIR    folder of .txt notes             (default: notes)
#   OUTPUT_ROOT  results go to OUTPUT_ROOT/<MODEL> (default: data/results)
#
# A rule model is any folder containing used_resources.txt
# (e.g. delirium/models/DELIRIUM, fall/rule/RuleEngine, gait_and_balance/models/GAIT_BALANCE).

set -uo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"

INPUT_DIR="$(realpath "${1:-notes}")"
OUTPUT_ROOT="$(realpath -m "${2:-data/results}")"
JAR="${JAR:-$ROOT/delirium/MedTagger-fit-context.jar}"

[ -d "$INPUT_DIR" ] || { echo "Input folder not found: $INPUT_DIR" >&2; exit 1; }
[ -f "$JAR" ] || { echo "MedTagger jar not found: $JAR" >&2; exit 1; }
command -v java >/dev/null || { echo "java is not installed or not on PATH" >&2; exit 1; }

FAILED=()
while IFS= read -r RES; do
  RULES="$(dirname "$RES")"
  NAME="$(basename "$RULES")"
  OUT="$OUTPUT_ROOT/$NAME"
  mkdir -p "$OUT"

  echo "Running $NAME  (${RULES#./})"
  if ! java -Xms512M -Xmx2000M -jar "$JAR" "$INPUT_DIR" "$OUT" "$ROOT/${RULES#./}" > "$OUT/medtagger.log" 2>&1; then
    echo "  FAILED - see $OUT/medtagger.log"
    FAILED+=("$NAME")
  fi
done < <(find . -name used_resources.txt -not -path './.git/*' -not -path './data/*' | sort)

echo "Done. Results are in $OUTPUT_ROOT/"
if [ ${#FAILED[@]} -gt 0 ]; then
  echo "Failed models: ${FAILED[*]}" >&2
  exit 1
fi
