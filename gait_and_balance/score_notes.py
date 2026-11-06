"""Score every note in a directory for one concept and save the top-n note IDs.

score = keyword matches + regex matches (case-insensitive, every occurrence counts).
"""
import argparse
import csv
import re
from collections import Counter
from pathlib import Path

# Rules per concept -> sub-feature -> keywords and regexes.
# Definitions come from Appendix_NLP_Feature_Definitions_20261028.docx.
CONCEPTS = {
    "gait_and_balance": {
        "gait_abnormality": {
            "keywords": ["unsteady gait", "shuffling gait", "wide-based gait", "slow gait"],
            "regex": [r"\b(unsteady|shuffling|wide[- ]based|slow(ed)?|abnormal)\s+(gait|walk(ing)?)\b"],
        },
        "balance_impairment": {
            "keywords": ["poor balance", "impaired balance", "unsteadiness", "loss of balance"],
            "regex": [r"\b(poor|impaired|reduced|loss of|difficulty (with|keeping|maintaining))\s+balance\b"],
        },
        "unsafe_ambulation": {
            "keywords": ["ambulating without assistance", "unsafe ambulation", "walking without walker"],
            "regex": [r"\b(walk|walks|walking|ambulat\w+)\s+(without|against)\s+(\w+\s+){0,2}(assist\w*|walker|cane|restrictions?|orders?)\b"],
        },
    },
    "musculoskeletal": {
        "frailty": {
            "keywords": ["frail", "frailty", "exhaustion", "low activity level"],
            "regex": [
                r"\b(clinical frailty scale|CFS)\s*(score\s*)?(of\s*|[:=]\s*)?[4-9]\b",
                r"\b(slow(ed)?|decreased|reduced)\s+(gait speed|walking speed|walk speed)\b",
                r"\b(low|decreased|reduced|minimal)\s+(physical\s+)?activity\b",
            ],
        },
        "weakness": {
            "keywords": ["generalized weakness", "muscle weakness", "leg weakness", "legs feel heavy"],
            "regex": [
                r"\b(generali[sz]ed|proximal|distal|muscle|leg|lower extremity|bilateral)\s+weakness\b",
                r"\b(legs?|arms?)\s+(feel(s|ing)?|felt)\s+(heavy|weak)\b",
                r"\b(difficult\w*|hard|trouble)\s+(\w+\s+){0,2}lift(ing)?\s+(\w+\s+)?(legs?|feet|foot)\b",
                r"\b[0-4][+-]?/5\s+(strength|power)\b",
            ],
        },
    },
    "sensory": {
        "vision_impairment": {
            "keywords": ["vision impairment", "visual impairment", "low vision", "blurry vision", "blurred vision",
                         "legally blind", "macular degeneration"],
            "regex": [
                r"\b(decreased|reduced|poor|impaired|declining|worsening)\s+(vision|visual acuity|eyesight)\b",
                r"\b(difficult\w*|trouble|unable to|can(no|')t)\s+(\w+\s+){0,2}(see(ing)?|read(ing)?)\b",
                r"\b20/([4-9]\d|[1-9]\d{2,})\b",
            ],
        },
        "hearing_impairment": {
            "keywords": ["hearing loss", "hard of hearing", "hearing impairment", "presbycusis"],
            "regex": [
                r"\b(decreased|reduced|poor|impaired|diminished)\s+hearing\b",
                r"\b(difficult\w*|trouble)\s+(\w+\s+){0,2}hear(ing)?\b",
                r"\bhearing\s+aids?\b",
                r"\bHOH\b",
            ],
        },
        "numbness_neuropathy": {
            "keywords": ["numbness", "tingling", "pins and needles"],
            "regex": [
                r"\b((peripheral|diabetic|sensory)\s+)?(poly)?neuropath(y|ic)\b",
                r"\b(numb|burning)\s+(\w+\s+){0,2}(hands?|feet|foot|toes|fingers)\b",
                r"\b(decreased|diminished|reduced|absent|impaired|loss of)\s+(light touch|sensation|"
                r"vibrat\w*( sense)?|proprioception|monofilament( sensation)?|pinprick)\b",
                r"\binsensate\b",
            ],
        },
    },
    "cardiovascular": {
        "dizziness": {
            "keywords": ["dizziness", "dizzy", "lightheadedness", "lightheaded", "vertigo", "presyncope",
                         "symptomatic hypotension"],
            "regex": [
                r"\blight-headed(ness)?\b",
                r"\bnear[- ]syncop(e|al)\b",
                r"\b(feel(s|ing)?|felt)\s+(faint|woozy)\b",
                r"\b(room|head|everything)\s+((is|was)\s+)?spinning\b",
                r"\b(orthostatic|postural)\s+hypotension\b",
                r"\b(blood pressure|BP)\s+(drops?|dropped|fell|falls)\b",
            ],
        },
    },
    "mental_health": {
        "anxiety": {
            "keywords": ["anxiety", "anxious", "nervousness", "panic attacks"],
            "regex": [
                r"\b(excessive|persistent|constant)\s+worry(ing)?\b",
                r"\bworr(y|ies|ied|ying)\s+(a lot|constantly|all the time)\b",
                r"\bGAD-?7\s*(score\s*)?(of\s*|[:=]\s*)?([5-9]|1\d|2[01])\b",
            ],
        },
        "depression": {
            "keywords": ["depression", "depressed", "hopelessness", "anhedonia"],
            "regex": [
                r"\bMDD\b",
                r"\b(feel(s|ing)?|felt)\s+(sad|hopeless|down|worthless)\b",
                r"\b(loss of|lost|little|decreased)\s+interest\b",
                r"\bPHQ-?9\s*(score\s*)?(of\s*|[:=]\s*)?([5-9]|1\d|2[0-7])\b",
                r"\bPHQ-?2\s*(score\s*)?(of\s*|[:=]\s*)?[3-6]\b",
            ],
        },
        "sleep_disturbance": {
            "keywords": ["insomnia", "sleep disturbance", "trouble sleeping"],
            "regex": [
                r"\b(difficult\w*|trouble|problems?)\s+(\w+\s+){0,2}(falling|staying)\s+asleep\b",
                r"\b(poor|disrupted|interrupted|fragmented|restless)\s+sleep\b",
                r"\b(wakes?|waking|woke|awakens?|awakening)\s+(up\s+)?(\w+\s+){0,2}(at night|overnight|during the night|too early)\b",
                r"\bsleep(s|ing)?\s+(only\s+)?[1-4]\s+hours\b",
            ],
        },
        "sleep_apnea": {
            "keywords": ["sleep apnea", "CPAP", "BiPAP"],
            "regex": [
                r"\bOSA\b",
                r"\b(stops?|stopped|pauses?|paused)\s+breathing\b",
                r"\b(apneic|apnea)\s+(episodes|events|spells)\b",
                r"\bAHI\s*(of\s*|[:=]\s*)?([5-9]|[1-9]\d+)\b",
            ],
        },
    },
    "laboratory_and_nutrition": {
        "malnutrition": {
            "keywords": ["malnutrition", "malnourished", "undernutrition", "undernourished", "cachexia",
                         "unintentional weight loss", "unintended weight loss", "poor appetite"],
            "regex": [
                r"\b(poor|decreased|reduced|low|minimal|inadequate)\s+(oral\s+|PO\s+|food\s+|caloric\s+|nutritional\s+)?intake\b",
                r"\b(lost|losing|loss of)\s+\d+(\.\d+)?\s*(lbs?|pounds|kg)\b",
                r"\b(decreased|reduced|loss of)\s+appetite\b",
                r"\b(muscle|temporal|fat)\s+wasting\b",
                r"\balbumin\s*(of\s*|[:=]\s*)?([0-2](\.\d+)?|3(\.[0-4]\d*)?)(?!\.?\d)",
                r"\bBMI\s*(of\s*|[:=]\s*)?(1[0-7](\.\d+)?|18(\.[0-4]\d*)?)(?!\.?\d)",
            ],
        },
    },
    "medication": {
        "medication_reconciliation_concern": {
            "keywords": ["medication discrepancy", "therapeutic duplication", "duplicate therapy"],
            "regex": [
                r"\b(medication|med|drug|dose|dosing)\s+(discrepanc(y|ies)|errors?|mismatch(es)?)\b",
                r"\bdiscrepanc(y|ies)\s+(\w+\s+){0,3}(medications?|meds?|list|doses?|dosing|pharmacy)\b",
                r"\b(duplicate|duplicated)\s+(\w+\s+){0,2}(medications?|meds?|prescriptions?|bottles?|orders?)\b",
                r"\b(not|no longer)\s+(on|in)\s+(\w+\s+){0,2}(medication|med)\s+list\b",
                r"\b(missing|omitted)\s+from\s+(\w+\s+){0,2}(medication|med)\s+list\b",
                r"\bnever\s+(filled|picked up|started)\b",
                r"\bconflicting\s+(\w+\s+){0,2}(medications?|meds?|lists?|instructions|doses|prescriptions?)\b",
                r"\b(does not|doesn't|did not)\s+match\s+(\w+\s+){0,3}(medications?|meds?|pharmacy|list|bottles?)\b",
            ],
        },
        "deprescribing_discussion": {
            "keywords": ["deprescribe", "deprescribing", "pill burden", "polypharmacy", "Beers criteria"],
            "regex": [
                r"\b(discontinued|tapered off|weaned off)\b",
                r"\b(was|were|has been|have been|is being)\s+stopped\b",
                r"\b(stop|stopping|discontinue|discontinuing|taper|tapering|wean|weaning|cut back on)\s+(\w+\s+){0,3}(medications?|meds?|pills?)\b",
                r"\b(reduce|reduced|reducing|decrease|decreased|decreasing|lower|lowered|lowering)\s+(the\s+|his\s+|her\s+)?(\w+\s+)?(dose|dosage)\b",
                r"\bdose\s+(was\s+)?(reduced|decreased|lowered|halved)\b",
            ],
        },
    },
}


def score_note(text, rules):
    """Return (score, hits): hits counts each matched phrase (lowercased)."""
    hits = Counter()
    for sub in rules.values():
        patterns = [r"\b" + re.escape(kw) + r"\b" for kw in sub["keywords"]] + sub["regex"]
        for rx in patterns:
            for m in re.finditer(rx, text, re.IGNORECASE):
                hits[" ".join(m.group(0).lower().split())] += 1
    return sum(hits.values()), hits


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--concept", required=True, choices=CONCEPTS)
    p.add_argument("--notes_dir", required=True)
    p.add_argument("--top_n", type=int, default=3)
    args = p.parse_args()

    rules = CONCEPTS[args.concept]
    files = sorted(Path(args.notes_dir).glob("*.txt"),
                   key=lambda f: (not f.stem.isdigit(), int(f.stem) if f.stem.isdigit() else 0, f.stem))
    width = max((len(f.stem) for f in files), default=0)
    print(f"{args.concept} | {len(files)} notes", flush=True)

    scores = []
    evidence = {}
    for f in files:
        score, hits = score_note(f.read_text(encoding="utf-8", errors="ignore"), rules)
        scores.append((f.stem, score))
        # Same phrases and counts as the terminal log, in one CSV cell.
        evidence[f.stem] = "; ".join(f"+{n} {phrase}" for phrase, n in hits.most_common())
        if score:
            print(f"\nNote {f.stem:<{width}} | score {score}", flush=True)
            for phrase, n in hits.most_common():
                print(f"  +{n}  {phrase}", flush=True)

    with open(f"{args.concept}_scores.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["note_id", "score"])
        w.writerows(scores)

    with open(f"{args.concept}_scores_with_evidence.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["note_id", "score", "evidence"])
        w.writerows([nid, score, evidence[nid]] for nid, score in scores)

    # Highest score first; ties keep note ID order (sort is stable).
    top = sorted(scores, key=lambda s: -s[1])[: args.top_n]
    with open(f"{args.concept}_top_n_file_ids.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["note_id"])
        w.writerows([[nid] for nid, _ in top])

    with open(f"{args.concept}_top_n_with_evidence.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["rank", "note_id", "score", "evidence"])
        w.writerows([rank, nid, score, evidence[nid]] for rank, (nid, score) in enumerate(top, 1))

    print(f"\nTOP {args.top_n}")
    for rank, (nid, score) in enumerate(top, 1):
        print(f"  {rank}. Note {nid:<{width}} | score {score}")
    matched = sum(1 for _, score in scores if score)
    print(f"\n{matched} of {len(scores)} notes matched")


if __name__ == "__main__":
    main()
