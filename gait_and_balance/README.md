# Gait and Balance NLP Algorithm

A rule-based NLP algorithm (MedTaggerIE) that extracts gait and balance findings from clinical notes. It is set up the same way as the [delirium](../delirium) algorithm: step 1 runs MedTagger, step 2 summarizes each note and exports MedTator files for review.

## Concepts

| Concept (NORM)            | Example terms                                                          | Counts toward impairment status |
| ------------------------- | ---------------------------------------------------------------------- | ------------------------------- |
| Gait_Abnormality          | abnormal gait, unsteady gait, shuffling gait, gait is slow, difficulty walking | Yes (gait)              |
| Ataxia                    | ataxia, ataxic                                                         | Yes (gait)                      |
| Balance_Impairment        | poor/impaired balance, loss of balance, unsteady on feet, positive Romberg | Yes (balance)               |
| Assistive_Device          | walker, front-wheeled walker, cane, rollator, wheelchair               | Yes (device)                    |
| Fall_Risk                 | high fall risk, at risk for falls, fall precautions, fear of falling   | No (reported only)              |
| Gait_Balance_Assessment   | Timed Up and Go, Berg Balance Scale, Tinetti, gait speed, SPPB         | No (reported only)              |
| Normal_Gait_Balance       | normal gait, steady gait, balance intact, negative Romberg, ambulates independently | No (normal evidence)  |

Only mentions with `certainty="Positive"` and `experiencer="Patient"` are counted, so negated ("no ataxia"), hypothetical, and family-member mentions are ignored. The negation/context rules are in `models/GAIT_BALANCE/context/contextRule.txt` (shared with the ENACT delirium model).

**Note-level status** (`Gait_Balance_Impairment_Status`): 1 if the note has a positive patient mention of a gait abnormality, ataxia, balance impairment, or assistive device; otherwise 0.

## Folder layout

```
gait_and_balance/
├── run_gait_and_balance.sh                  # runs step 1 + step 2
├── run_MedTagger-fit-gait_balance_step1.sh  # step 1: MedTagger extraction
├── run_post_processing_step2.py             # step 2: summary CSV + MedTator XML
├── models/GAIT_BALANCE/                     # rules
│   ├── regexp/       # keyword lists, one regex per line
│   ├── rules/        # match rules mapping keyword lists to concepts
│   ├── context/      # negation / experiencer / historical context rules
│   └── sectag/       # section detection
└── data/
    ├── input/        # put clinical notes here (.txt, one note per file)
    ├── output/       # MedTagger .ann output (step 1)
    ├── medtator/     # MedTator XML for chart review (step 2)
    └── summarized_result.csv   # note-level summary (step 2)
```

## Prerequisites

- Java 1.8 or later
- Python 3 (standard library only)
- `MedTagger-fit-context.jar`: the scripts use `gait_and_balance/MedTagger-fit-context.jar` if present, otherwise `../delirium/MedTagger-fit-context.jar`.

## Run

From the repository root:

```bash
bash gait_and_balance/run_gait_and_balance.sh
```

With your own folders (input, output, rules):

```bash
bash gait_and_balance/run_gait_and_balance.sh /path/to/notes /path/to/output models/GAIT_BALANCE
```

Run the steps separately:

```bash
bash gait_and_balance/run_MedTagger-fit-gait_balance_step1.sh
```

```bash
cd gait_and_balance && python3 run_post_processing_step2.py --input_dir data/input --output_dir data/output
```

## Output

`data/summarized_result.csv`:

| Column | Meaning |
| --- | --- |
| FileName | note file name |
| Tags / Texts | positive patient concepts and the matched text |
| Gait_Abnormality, Balance_Impairment, Assistive_Device, Fall_Risk | 1 if found in the note |
| Gait_Balance_Impairment_Status | overall note-level status (see above) |

## Refine

Add or remove keywords in `models/GAIT_BALANCE/regexp/*.txt`. To add a new concept, create `resources_regexp_re<name>.txt`, add a line to `rules/resources_rules_matchrules.txt` (keep the `cm_` prefix on `RULENAME`, which is what turns on negation/context detection), and list the file in `used_resources.txt`.

These rules have not been validated by chart review. As with the delirium algorithm, we recommend a local evaluation and keyword refinement before use. See https://github.com/OHNLP/annotation-best-practices.
