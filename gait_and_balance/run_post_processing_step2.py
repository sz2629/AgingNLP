"""Step 2: summarize MedTagger gait & balance output (.ann) into one row per note.

Only mentions with certainty=Positive and experiencer=Patient are counted.
Also writes one MedTator XML per note (data/medtator/<note>.xml) using the
AgeTech schema (../20261028_AgeTech_Schema.dtd), so the NLP output can be
loaded into MedTator for review / pre-annotation.

Run from this folder after step 1:  python run_post_processing_step2.py
"""
import csv
import glob
import os
import re
from xml.sax.saxutils import quoteattr

CONCEPTS = ["Gait_abnormality", "Balance_impairment", "Assistive_device", "Normal_gait"]
INPUT_DIR = "../notes"
ANN_DIR = "data/output"
OUT_CSV = "data/summarized_result.csv"
XML_DIR = "data/medtator"

# MedTator project name = the <!ENTITY name> in 20261028_AgeTech_Schema.dtd
SCHEMA_NAME = "Age_Tech"
# MedTagger norm -> (DTD tag, DTD feature, forced certainty or None).
# Normal_gait has no schema feature of its own; it is the absence of a gait
# abnormality, so it is exported as a negated gait_abnormality.
NORM_TO_SCHEMA = {
    "Gait_abnormality": ("gait_and_balance", "gait_abnormality", None),
    "Balance_impairment": ("gait_and_balance", "balance_impairment", None),
    "Assistive_device": ("functional_status", "assistive_device_use", None),
    "Normal_gait": ("gait_and_balance", "gait_abnormality", "negated"),
}
TAG_ID_PREFIX = {"gait_and_balance": "GB", "functional_status": "FS"}
CERTAINTY = {"positive", "negated", "possible", "hypothetical"}

FIELD = re.compile(r'(\w+)="(.*?)"')


def parse_ann(path):
    with open(path) as f:
        for line in f:
            if line.strip():
                yield dict(FIELD.findall(line))


def to_schema_attrs(m):
    """Map one MedTagger mention to (tag, attrs) valid under the AgeTech DTD."""
    if m.get("norm") not in NORM_TO_SCHEMA:
        return None
    tag, feature, forced = NORM_TO_SCHEMA[m["norm"]]
    certainty = forced or m.get("certainty", "").lower()
    if certainty not in CERTAINTY:
        certainty = "positive"
    status = "history" if m.get("status", "").lower().startswith("hist") else "present"
    experiencer = "patient" if m.get("experiencer", "").lower() == "patient" else "other"
    return tag, {
        "spans": f'{m["start"]}~{m["end"]}',
        "text": m["text"],
        "feature": feature,
        "certainty": certainty,
        "status": status,
        "experiencer": experiencer,
        "exclusion": "no",
        "comment": f'NLP:{m["norm"]}',
    }


def write_medtator_xml(note_path, mentions, out_path):
    with open(note_path) as f:
        raw = f.read()
    counters = {}
    tags = []
    for m in mentions:
        mapped = to_schema_attrs(m)
        if mapped is None:
            continue
        tag, attrs = mapped
        n = counters.get(tag, 0)
        counters[tag] = n + 1
        attrs = {"id": f"{TAG_ID_PREFIX.get(tag, tag[:2].upper())}{n}", **attrs}
        attr_str = " ".join(f"{k}={quoteattr(v)}" for k, v in attrs.items())
        tags.append(f"<{tag} {attr_str} />")
    # CDATA keeps offsets identical to the raw note; split any literal "]]>"
    text = raw.replace("]]>", "]]]]><![CDATA[>")
    xml = (
        '<?xml version="1.0" encoding="UTF-8" ?>\n'
        f"<{SCHEMA_NAME}>\n<TEXT><![CDATA[{text}]]></TEXT>\n<TAGS>\n"
        + "".join(t + "\n" for t in tags)
        + f"</TAGS>\n<META/>\n</{SCHEMA_NAME}>\n"
    )
    with open(out_path, "w") as f:
        f.write(xml)


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    notes = sorted(glob.glob(os.path.join(INPUT_DIR, "*.txt")),
                   key=lambda p: (len(p), p))
    os.makedirs(XML_DIR, exist_ok=True)
    with open(OUT_CSV, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["FileName"] + CONCEPTS + ["Gait_Balance_Problem", "Texts"])
        for note in notes:
            name = os.path.basename(note)
            ann = os.path.join(ANN_DIR, name + ".ann")
            hits = {c: [] for c in CONCEPTS}
            mentions = list(parse_ann(ann)) if os.path.exists(ann) else []
            write_medtator_xml(note, mentions, os.path.join(XML_DIR, name[:-4] + ".xml"))
            if mentions:
                for m in mentions:
                    if m.get("certainty") == "Positive" and m.get("experiencer") == "Patient" \
                            and m.get("norm") in hits:
                        hits[m["norm"]].append(m["text"].strip())
            problem = int(bool(hits["Gait_abnormality"] or hits["Balance_impairment"]))
            texts = "; ".join(f"{c}:{t}" for c in CONCEPTS for t in hits[c])
            w.writerow([name] + [int(bool(hits[c])) for c in CONCEPTS] + [problem, texts])
    print("wrote", OUT_CSV)
    print("wrote MedTator XML to", XML_DIR)


if __name__ == "__main__":
    main()
