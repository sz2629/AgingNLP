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
python run_post_processing_step2.py                          # -> data/summarized_result.csv
```

Pass other folders with `bash run_MedTagger-fit-gait_and_balance_step1.sh INPUT_DIR OUTPUT_DIR`.
`Gait_Balance_Problem` = 1 when a Positive, Patient-experienced Gait_abnormality or Balance_impairment is found.
