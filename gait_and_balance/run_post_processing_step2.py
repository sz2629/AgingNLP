"""Step 2: post-process MedTagger gait & balance output (*.ann).

1. Converts every MedTagger .ann file into one MedTator XML file that conforms
   to the AgeTech schema (../20261028_AgeTech_Schema.dtd). The DTD is parsed at
   run time, and every tag, feature and attribute value is checked against it,
   so the XML loads in MedTator with that schema.
2. Writes a one-row-per-note summary CSV (only certainty=Positive and
   experiencer=Patient mentions are counted).

Run from anywhere after step 1:
    python run_post_processing_step2.py
    python run_post_processing_step2.py --ann-dir data/output --notes-dir ../notes \
        --xml-dir data/medtator --dtd ../20261028_AgeTech_Schema.dtd
"""
import argparse
import csv
import glob
import os
import re
import sys
from xml.sax.saxutils import quoteattr

HERE = os.path.dirname(os.path.abspath(__file__))

CONCEPTS = ["Gait_abnormality", "Balance_impairment", "Assistive_device", "Normal_gait"]

# MedTagger norm -> (DTD tag, DTD feature, invert certainty?).
# Normal_gait has no schema feature of its own: "normal gait" is the absence of
# a gait abnormality, so it is exported as gait_abnormality with the certainty
# inverted (positive normal gait -> negated abnormality, and vice versa).
NORM_TO_SCHEMA = {
    "Gait_abnormality": ("gait_and_balance", "gait_abnormality", False),
    "Balance_impairment": ("gait_and_balance", "balance_impairment", False),
    "Assistive_device": ("functional_status", "assistive_device_use", False),
    "Normal_gait": ("gait_and_balance", "gait_abnormality", True),
}
INVERT = {"positive": "negated", "negated": "positive"}
TAG_ID_PREFIX = {"gait_and_balance": "GB", "functional_status": "FS"}

FIELD = re.compile(r'(\w+)="(.*?)"')
DTD_ENTITY = re.compile(r'<!ENTITY\s+name\s+"([^"]+)"\s*>')
DTD_ELEMENT = re.compile(r'<!ELEMENT\s+(\w+)\s')
DTD_ATTR = re.compile(r'<!ATTLIST\s+(\w+)\s+(\w+)\s+(\(([^)]*)\)|CDATA)\s*(#REQUIRED|#IMPLIED)?')


# ---------------------------------------------------------------- DTD schema
def load_dtd(path):
    """Parse a MedTator DTD -> (schema name, {tag: {attr: (values|None, required)}})."""
    with open(path) as f:
        text = re.sub(r"<!--.*?-->", "", f.read(), flags=re.S)
    m = DTD_ENTITY.search(text)
    if not m:
        sys.exit(f"{path}: no <!ENTITY name ...> found")
    tags = {t: {} for t in DTD_ELEMENT.findall(text)}
    for tag, attr, _, values, flag in DTD_ATTR.findall(text):
        allowed = [v.strip() for v in values.split("|")] if values else None
        tags.setdefault(tag, {})[attr] = (allowed, flag == "#REQUIRED")
    return m.group(1), tags


def check_tag(schema, tag, attrs):
    """Raise ValueError if (tag, attrs) is not valid under the DTD."""
    if tag not in schema:
        raise ValueError(f"tag <{tag}> is not in the DTD")
    for attr, (allowed, required) in schema[tag].items():
        if attr not in attrs:
            if required:
                raise ValueError(f"<{tag}> missing required attribute {attr}")
        elif allowed is not None and attrs[attr] not in allowed:
            raise ValueError(f"<{tag}> {attr}={attrs[attr]!r} not in {allowed}")


# ---------------------------------------------------------------- .ann -> tags
def parse_ann(path):
    with open(path) as f:
        for line in f:
            if line.strip():
                yield dict(FIELD.findall(line))


def to_schema_attrs(m):
    """Map one MedTagger mention to (tag, attrs) using the AgeTech vocabulary."""
    if m.get("norm") not in NORM_TO_SCHEMA:
        return None
    tag, feature, invert = NORM_TO_SCHEMA[m["norm"]]
    certainty = m.get("certainty", "").lower()
    if certainty not in ("positive", "negated", "possible", "hypothetical"):
        certainty = "positive"
    if invert:
        certainty = INVERT.get(certainty, certainty)
    status = "history" if m.get("status", "").lower().startswith("hist") else "present"
    experiencer = "patient" if m.get("experiencer", "").lower() == "patient" else "other"
    return tag, {
        "feature": feature,
        "certainty": certainty,
        "status": status,
        "experiencer": experiencer,
        "exclusion": "no",
        "comment": f'NLP:{m["norm"]}',
    }


def ann_to_xml(ann_path, note_path, schema_name, schema):
    """Build the MedTator XML string for one note."""
    with open(note_path) as f:
        raw = f.read()
    counters, tags = {}, []
    for m in parse_ann(ann_path):
        mapped = to_schema_attrs(m)
        if mapped is None:
            continue
        tag, attrs = mapped
        start, end = int(m["start"]), int(m["end"])
        if raw[start:end] != m["text"]:
            print(f"warning: {ann_path}: span {start}~{end} does not match "
                  f"{m['text']!r} in {note_path}", file=sys.stderr)
        check_tag(schema, tag, attrs)
        n = counters.get(tag, 0)
        counters[tag] = n + 1
        prefix = TAG_ID_PREFIX.get(tag, tag[:2].upper())
        attrs = {"id": f"{prefix}{n}", "spans": f"{start}~{end}", "text": m["text"], **attrs}
        tags.append(f"<{tag} " + " ".join(f"{k}={quoteattr(v)}" for k, v in attrs.items()) + " />")
    # CDATA keeps offsets identical to the raw note; split any literal "]]>"
    text = raw.replace("]]>", "]]]]><![CDATA[>")
    return (
        '<?xml version="1.0" encoding="UTF-8" ?>\n'
        f"<{schema_name}>\n<TEXT><![CDATA[{text}]]></TEXT>\n<TAGS>\n"
        + "".join(t + "\n" for t in tags)
        + f"</TAGS>\n<META/>\n</{schema_name}>\n"
    )


# ---------------------------------------------------------------- summary CSV
def summarize(ann_path):
    hits = {c: [] for c in CONCEPTS}
    if ann_path and os.path.exists(ann_path):
        for m in parse_ann(ann_path):
            if m.get("certainty") == "Positive" and m.get("experiencer") == "Patient" \
                    and m.get("norm") in hits:
                hits[m["norm"]].append(m["text"].strip())
    return hits


def natural_key(p):
    return [int(s) if s.isdigit() else s for s in re.split(r"(\d+)", os.path.basename(p))]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ann-dir", default=os.path.join(HERE, "data/output"))
    ap.add_argument("--notes-dir", default=os.path.join(HERE, "../notes"))
    ap.add_argument("--xml-dir", default=os.path.join(HERE, "data/medtator"))
    ap.add_argument("--csv", default=os.path.join(HERE, "data/summarized_result.csv"))
    ap.add_argument("--dtd", default=os.path.join(HERE, "../20261028_AgeTech_Schema.dtd"))
    args = ap.parse_args()

    schema_name, schema = load_dtd(args.dtd)
    os.makedirs(args.xml_dir, exist_ok=True)

    anns = sorted(glob.glob(os.path.join(args.ann_dir, "*.ann")), key=natural_key)
    if not anns:
        sys.exit(f"no .ann files in {args.ann_dir} (run step 1 first)")

    n_xml = 0
    with open(args.csv, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["FileName"] + CONCEPTS + ["Gait_Balance_Problem", "Texts"])
        for ann in anns:
            name = os.path.basename(ann)[: -len(".ann")]          # e.g. 1.txt
            note = os.path.join(args.notes_dir, name)
            if os.path.exists(note):
                xml = ann_to_xml(ann, note, schema_name, schema)
                with open(os.path.join(args.xml_dir, os.path.splitext(name)[0] + ".xml"), "w") as f:
                    f.write(xml)
                n_xml += 1
            else:
                print(f"warning: note {note} not found; no XML for {ann}", file=sys.stderr)

            hits = summarize(ann)
            problem = int(bool(hits["Gait_abnormality"] or hits["Balance_impairment"]))
            texts = "; ".join(f"{c}:{t}" for c in CONCEPTS for t in hits[c])
            w.writerow([name] + [int(bool(hits[c])) for c in CONCEPTS] + [problem, texts])

    print("wrote", args.csv)
    print(f"wrote {n_xml} MedTator XML files ({schema_name} schema) to {args.xml_dir}")


if __name__ == "__main__":
    main()
