"""Step 2: summarize MedTagger gait & balance output (.ann) into one row per note.

Only mentions with certainty=Positive and experiencer=Patient are counted.
Run from this folder after step 1:  python run_post_processing_step2.py
"""
import csv
import glob
import os
import re

CONCEPTS = ["Gait_abnormality", "Balance_impairment", "Assistive_device", "Normal_gait"]
INPUT_DIR = "../notes"
ANN_DIR = "data/output"
OUT_CSV = "data/summarized_result.csv"

FIELD = re.compile(r'(\w+)="(.*?)"')


def parse_ann(path):
    with open(path) as f:
        for line in f:
            if line.strip():
                yield dict(FIELD.findall(line))


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    notes = sorted(glob.glob(os.path.join(INPUT_DIR, "*.txt")),
                   key=lambda p: (len(p), p))
    with open(OUT_CSV, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["FileName"] + CONCEPTS + ["Gait_Balance_Problem", "Texts"])
        for note in notes:
            name = os.path.basename(note)
            ann = os.path.join(ANN_DIR, name + ".ann")
            hits = {c: [] for c in CONCEPTS}
            if os.path.exists(ann):
                for m in parse_ann(ann):
                    if m.get("certainty") == "Positive" and m.get("experiencer") == "Patient" \
                            and m.get("norm") in hits:
                        hits[m["norm"]].append(m["text"].strip())
            problem = int(bool(hits["Gait_abnormality"] or hits["Balance_impairment"]))
            texts = "; ".join(f"{c}:{t}" for c in CONCEPTS for t in hits[c])
            w.writerow([name] + [int(bool(hits[c])) for c in CONCEPTS] + [problem, texts])
    print("wrote", OUT_CSV)


if __name__ == "__main__":
    main()
