"""Step 2: summarize MedTagger gait and balance output.

Reads the MedTagger .ann files from step 1 and writes:
  1. A note-level CSV (data/summarized_result.csv by default) with the
     extracted concepts and gait / balance status for each note.
  2. MedTator XML files (data/medtator/) so the NLP output can be reviewed
     or corrected in MedTator (https://medtator.ohnlp.org).
"""

import argparse
import csv
import glob
import os
import re
import xml.etree.ElementTree as ET

MODEL_NAME = "Gait_Balance_schema_1_0"

# Concept (MedTagger NORM, lower case) -> domain used for the note-level status.
CONCEPT_DOMAIN = {
    "gait_abnormality": "gait",
    "ataxia": "gait",
    "balance_impairment": "balance",
    "assistive_device": "device",
    "fall_risk": "fall_risk",
    "gait_balance_assessment": "assessment",
    "normal_gait_balance": "normal",
}

FIELD_RE = re.compile(r'(\w+)="(.*?)"(?=\t|$)')


def read_txt(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def parse_ann_line(line):
    """Parse one MedTagger output line into a dict.

    Format: <file>\\t\\t<type>\\ttext="..."\\tstart="..."\\tend="..."\\t...
    """
    parts = line.rstrip("\n").split("\t")
    if len(parts) < 4:
        return None
    rec = {"file": parts[0], "type": parts[2]}
    for part in parts[3:]:
        m = FIELD_RE.match(part)
        if m:
            rec[m.group(1)] = m.group(2)
    return rec


def read_ann(path):
    records = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.strip():
                rec = parse_ann_line(line)
                if rec is not None:
                    records.append(rec)
    return records


def is_positive(rec):
    return (
        "positive" in rec.get("certainty", "").lower()
        and "patient" in rec.get("experiencer", "").lower()
    )


def summarize_note(records):
    norms, texts, domains = [], [], []
    for rec in records:
        if not is_positive(rec):
            continue
        norm = rec.get("norm", "").strip().lower()
        norms.append(norm)
        texts.append(rec.get("text", "").strip().lower())
        domains.append(CONCEPT_DOMAIN.get(norm, "other"))

    gait = int("gait" in domains)
    balance = int("balance" in domains)
    device = int("device" in domains)
    # Overall impairment: any abnormal gait, abnormal balance, or use of an
    # assistive mobility device. Fall risk / assessments are reported only.
    impairment = int(gait or balance or device)
    return norms, texts, gait, balance, device, int("fall_risk" in domains), impairment


def output_evidence(input_dir, output_dir, summary_path):
    note_files = sorted(glob.glob(os.path.join(input_dir, "*.txt")))
    ann_by_note = {
        os.path.basename(p)[: -len(".ann")]: p
        for p in glob.glob(os.path.join(output_dir, "*.ann"))
    }
    # Include notes that only exist as .ann (e.g. input files without .txt).
    names = [os.path.basename(p) for p in note_files]
    names += [n for n in sorted(ann_by_note) if n not in names]

    os.makedirs(os.path.dirname(os.path.abspath(summary_path)), exist_ok=True)
    with open(summary_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "FileName",
                "Tags",
                "Texts",
                "Gait_Abnormality",
                "Balance_Impairment",
                "Assistive_Device",
                "Fall_Risk",
                "Gait_Balance_Impairment_Status",
            ]
        )
        for name in names:
            records = read_ann(ann_by_note[name]) if name in ann_by_note else []
            norms, texts, gait, balance, device, fall_risk, status = summarize_note(records)
            writer.writerow([name, norms, texts, gait, balance, device, fall_risk, status])
    print(f"Wrote note-level summary for {len(names)} notes: {summary_path}")


def create_combined_xml(raw_note, records, model_name):
    root = ET.Element(model_name)
    text_element = ET.SubElement(root, "TEXT")
    text_element.text = f"<![CDATA[{raw_note}]]>"
    tags_element = ET.SubElement(root, "TAGS")

    for idx, rec in enumerate(records):
        tag_name = rec.get("norm", "Concept") or "Concept"
        attrs = {
            "spans": f"{rec.get('start', '')}~{rec.get('end', '')}",
            "id": tag_name[:2].upper() + str(idx),
            "certainty": rec.get("certainty", "").lower(),
            "status": rec.get("status", "").lower(),
            "experiencer": rec.get("experiencer", "").lower(),
            "text": rec.get("text", ""),
            "exclusion": "",
            "comment": "",
        }
        ET.SubElement(tags_element, tag_name, attrs)

    xml_str = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")
    xml_str = xml_str.replace("&lt;![CDATA[", "<![CDATA[").replace("]]&gt;", "]]>")
    return f'<?xml version="1.0" encoding="UTF-8" ?>\n{xml_str}'


def prepare_medtator_annotation(input_dir, output_dir, medtator_dir, model_name):
    os.makedirs(medtator_dir, exist_ok=True)
    for ann_path in glob.glob(os.path.join(output_dir, "*.ann")):
        if os.path.getsize(ann_path) == 0:
            continue
        note_name = os.path.basename(ann_path)[: -len(".ann")]
        txt_path = os.path.join(input_dir, note_name)
        if not os.path.exists(txt_path):
            print(f"Skipping MedTator export, raw note not found: {txt_path}")
            continue
        xml = create_combined_xml(read_txt(txt_path), read_ann(ann_path), model_name)
        out_path = os.path.join(medtator_dir, note_name + ".xml")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(xml)
        print(out_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input_dir", default="data/input", help="raw .txt notes")
    parser.add_argument("--output_dir", default="data/output", help="MedTagger .ann output")
    parser.add_argument("--medtator_dir", default="data/medtator", help="MedTator XML output")
    parser.add_argument("--summary", default="data/summarized_result.csv", help="note-level CSV")
    args = parser.parse_args()

    output_evidence(args.input_dir, args.output_dir, args.summary)
    prepare_medtator_annotation(args.input_dir, args.output_dir, args.medtator_dir, MODEL_NAME)


if __name__ == "__main__":
    main()
