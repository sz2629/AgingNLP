# Cardiovascular NLP Algorithm (MedTaggerIE rules)

Rule-based extraction of the **Cardiovascular** feature class (see `Appendix_NLP_Feature_Definitions_20261028.docx`) from clinical
notes, using the same MedTaggerIE setup as `musculoskeletal/`, `gait_and_balance/` and `delirium/`
(`MedTagger-fit-context.jar`, Java 1.8+).

## Concepts

| NORM | Schema feature | Definition | Rule file (`models/Cardiovascular/regexp/`) | Examples |
| --- | --- | --- | --- | --- |
| Dizziness | `dizziness` | Patient-reported sensation of lightheadedness, faintness, or spinning that may signal orthostatic change, arrhythmia, or increased fall risk. Includes symptomatic hypotension, in which low or falling blood pressure is accompanied by symptoms such as lightheadedness or near-syncope. | `resources_regexp_redizziness.txt` | dizzy, dizziness, lightheaded, vertigo, room spinning, feels faint, near-syncope, symptomatic (orthostatic) hypotension |

Each line of a regexp file is a keyword or regex (matched case-insensitively); `rules/resources_rules_matchrules.txt`
maps each file to its NORM. Negation / certainty / experiencer come from `context/contextRule.txt`.

## Run

From the repo root, `bash run_all_rules.sh` picks this model up automatically and writes
`results/Cardiovascular/*.ann`. To run only this model:

```
bash run_MedTagger-fit-cardiovascular_step1.sh            # ../notes -> data/output/*.ann
```
