# Musculoskeletal NLP Algorithm (MedTaggerIE rules)

Rule-based extraction of musculoskeletal concepts from clinical notes, using the same MedTaggerIE
setup as `gait_and_balance/` and `delirium/` (`MedTagger-fit-context.jar`, Java 1.8+).

## Concepts

| NORM | Schema feature | Definition | Rule file (`models/Musculoskeletal/regexp/`) | Examples |
| --- | --- | --- | --- | --- |
| Frailty | `frailty` | A state of reduced physiological reserve and increased vulnerability to stressors, documented as frailty or reflected in features such as weakness, slowness, exhaustion, and low activity. | `resources_regexp_refrailty.txt` | frail, frailty, Clinical Frailty Scale 5–9, exhaustion, low activity level |
| Weakness | `weakness` | Documentation of reduced muscle strength or generalized weakness affecting function or mobility, including patient-described leg heaviness (legs feeling heavy or difficult to lift). | `resources_regexp_reweakness.txt` | generalized/proximal weakness, 0–4/5 strength, legs feel heavy, trouble lifting her legs |

Each line of a regexp file is a keyword or regex (matched case-insensitively); `rules/resources_rules_matchrules.txt`
maps each file to its NORM. Negation / certainty / experiencer come from `context/contextRule.txt`.
Normal strength (`5/5`) and Clinical Frailty Scale scores 1–4 are deliberately not matched.

## Run

From the repo root, `bash run_all_rules.sh` picks this model up automatically and writes
`results/Musculoskeletal/*.ann`. To run only this model:

```
bash run_MedTagger-fit-musculoskeletal_step1.sh            # ../notes -> data/output/*.ann
```
