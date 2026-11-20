# Mental Health NLP Algorithm (MedTaggerIE rules)

Rule-based extraction of the **Mental Health** feature class (see `Appendix_NLP_Feature_Definitions_20261028.docx`) from clinical
notes, using the same MedTaggerIE setup as `musculoskeletal/`, `gait_and_balance/` and `delirium/`
(`MedTagger-fit-context.jar`, Java 1.8+).

## Concepts

| NORM | Schema feature | Definition | Rule file (`models/Mental_Health/regexp/`) | Examples |
| --- | --- | --- | --- | --- |
| Anxiety | `anxiety` | A mood state marked by persistent worry, nervousness, or fear that may affect function, sleep, or engagement with care. | `resources_regexp_reanxiety.txt` | anxiety, anxious, generalized anxiety disorder, panic attacks, excessive worry, nervousness, GAD-7 >= 10 |
| Depression | `depression` | A mood disorder marked by persistent sadness, hopelessness, and loss of interest or pleasure, with cognitive, behavioral, and physical symptoms such as fatigue, poor concentration, and changes in appetite or sleep. | `resources_regexp_redepression.txt` | depression, depressed mood, major depressive disorder, hopeless, anhedonia, loss of interest, PHQ-9 >= 10, PHQ-2 >= 3, GDS-15 >= 5 |
| Sleep_disturbance | `sleep_disturbance` | Documentation of disrupted sleep, such as insomnia, difficulty falling or staying asleep, or poor sleep quality. | `resources_regexp_resleepdisturbance.txt` | insomnia, difficulty falling/staying asleep, trouble sleeping, poor sleep quality, wakes up several times at night |
| Sleep_apnea | `sleep_apnea` | Documentation of sleep apnea or repeated pauses in breathing during sleep. | `resources_regexp_resleepapnea.txt` | (obstructive/central) sleep apnea, OSA, sleep-disordered breathing, CPAP/BiPAP, stops breathing during sleep, AHI >= 5 |

Each line of a regexp file is a keyword or regex (matched case-insensitively); `rules/resources_rules_matchrules.txt`
maps each file to its NORM. Negation / certainty / experiencer come from `context/contextRule.txt`.

## Run

From the repo root, `bash run_all_rules.sh` picks this model up automatically and writes
`results/Mental_Health/*.ann`. To run only this model:

```
bash run_MedTagger-fit-mental_health_step1.sh            # ../notes -> data/output/*.ann
```
