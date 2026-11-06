#/bin/bash


INPUT_DIR="data/input"
OUTPUT_DIR="data/output"
RULES_DIR="models/ENACT_DELIRIUM"

java -Xms512M -Xmx2000M -jar MedTagger-fit-context.jar $INPUT_DIR $OUTPUT_DIR $RULES_DIR


