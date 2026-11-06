# Gait and Balance NLP Algorithm (MedTaggerIE rules)

Rule-based extraction of gait and balance concepts from clinical notes, using the same
MedTaggerIE setup as `delirium/` (jar: `../delirium/MedTagger-fit-context.jar`, Java 1.8+).

## Concepts

| NORM | Rule file (`models/GAIT_BALANCE/regexp/`) | Examples |
| --- | --- | --- |
| Gait_abnormality | `resources_regexp_regaitabnormality.txt` | unsteady gait, shuffling gait, wide-based gait, slow(ed) gait, abnormal walking |
| Balance_impairment | `resources_regexp_rebalanceimpairment.txt` | loss of balance, reduced/poor/impaired balance, imbalance, unsteadiness |
| Assistive_device | `resources_regexp_reassistivedevice.txt` | walker, rollator, cane, wheelchair |
| Normal_gait | `resources_regexp_renormalgait.txt` | gait normal, steady gait |

Each line of a regexp file is a keyword or regex; `rules/resources_rules_matchrules.txt` maps each
file to its NORM. Negation / certainty / experiencer are handled by `context/contextRule.txt`
(e.g. "walking without her walker" -> Assistive_device, certainty=Negated).

## Run

```
bash run_MedTagger-fit-gait_and_balance_step1.sh            # ../notes -> data/output/*.ann
python run_post_processing_step2.py                          # -> data/summarized_result.csv + data/medtator/*.xml
```

Pass other folders with `bash run_MedTagger-fit-gait_and_balance_step1.sh INPUT_DIR OUTPUT_DIR`.
`Gait_Balance_Problem` = 1 when a Positive, Patient-experienced Gait_abnormality or Balance_impairment is found.

## MedTator export

Step 2 converts every `data/output/*.ann` file into one MedTator XML file in `data/medtator/`, using the
AgeTech schema (`../20261028_AgeTech_Schema.dtd`). The script reads the DTD when it runs and checks every tag,
`feature` and context value against it, so it stops with an error rather than write XML that MedTator would
reject. The raw note text comes from `../notes/<name>.txt`, so offsets match the `.ann` spans. In MedTator,
load the DTD, then load the XML files.

Use other folders or another schema file with:

```
python run_post_processing_step2.py --ann-dir data/output --notes-dir ../notes \
    --xml-dir data/medtator --csv data/summarized_result.csv --dtd ../20261028_AgeTech_Schema.dtd
```

| NORM | Schema tag | `feature` |
| --- | --- | --- |
| Gait_abnormality | `gait_and_balance` | `gait_abnormality` |
| Balance_impairment | `gait_and_balance` | `balance_impairment` |
| Assistive_device | `functional_status` | `assistive_device_use` |
| Normal_gait | `gait_and_balance` | `gait_abnormality` with certainty inverted (normal gait → `negated`; negated normal gait → `positive`) |

`certainty`, `status` and `experiencer` come from MedTagger's context output and are lowercased to the
schema values. `exclusion` is set to `no` for every tag, and `comment` records the original NORM
(for example `NLP:Gait_abnormality`). The export includes every mention, not only the Positive/Patient
ones counted in the CSV, so reviewers can check the negated and possible mentions too.
