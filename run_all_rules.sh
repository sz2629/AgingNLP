
INPUT_DIR="data/input"
JAR="MedTagger-fit-context.jar"

for RULES in models/*/; do
  NAME=$(basename "$RULES")
  OUT="data/results/$NAME"
  mkdir -p "$OUT"

  echo "Running $NAME"
  java -Xms512M -Xmx2000M -jar "$JAR" "$INPUT_DIR" "$OUT" "$RULES"
done

echo "Done. Results are in data/results/"