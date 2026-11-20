#!/bin/bash
# Step 1: run MedTaggerIE with the Mental Health rule model over clinical notes.
#
# Concepts extracted (NORM values; rules in models/Mental_Health/rules):
#   Anxiety - anxiety, anxious, generalized anxiety disorder, panic attacks, excessive worry, nervousness, GAD-7 >= 10
#   Depression - depression, depressed mood, major depressive disorder, hopeless, anhedonia, loss of interest, PHQ-9 >= 10, PHQ-2 >= 3, GDS-15 >= 5
#   Sleep_disturbance - insomnia, difficulty falling/staying asleep, trouble sleeping, poor sleep quality, wakes up several times at night
#   Sleep_apnea - (obstructive/central) sleep apnea, OSA, sleep-disordered breathing, CPAP/BiPAP, stops breathing during sleep, AHI >= 5
#
# Usage: bash run_MedTagger-fit-mental_health_step1.sh [INPUT_DIR] [OUTPUT_DIR]
set -euo pipefail
cd "$(dirname "$0")"

INPUT_DIR="${1:-../notes}"
OUTPUT_DIR="${2:-data/output}"
RULES_DIR="models/Mental_Health"
JAR="MedTagger-fit-context.jar"
[ -f "$JAR" ] || JAR="../MedTagger-fit-context.jar"
[ -f "$JAR" ] || JAR="../delirium/MedTagger-fit-context.jar"

mkdir -p "$OUTPUT_DIR"
java -Xms512M -Xmx2000M -jar "$JAR" "$INPUT_DIR" "$OUTPUT_DIR" "$RULES_DIR"
