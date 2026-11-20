# Sensory NLP Algorithm (MedTaggerIE rules)

Rule-based extraction of the **Sensory** feature class (see `Appendix_NLP_Feature_Definitions_20261028.docx`) from clinical
notes, using the same MedTaggerIE setup as `musculoskeletal/`, `gait_and_balance/` and `delirium/`
(`MedTagger-fit-context.jar`, Java 1.8+).

## Concepts

| NORM | Schema feature | Definition | Rule file (`models/Sensory/regexp/`) | Examples |
| --- | --- | --- | --- | --- |
| Vision_impairment | `vision_impairment` | Documentation of reduced visual function affecting daily activities, whether or not corrected by lenses. | `resources_regexp_revisionimpairment.txt` | low vision, blurry vision, legally blind, macular degeneration, visual acuity 20/50 or worse, trouble reading / seeing at night |
| Hearing_impairment | `hearing_impairment` | Documentation of reduced hearing affecting communication or daily activities, whether or not aided by hearing devices. | `resources_regexp_rehearingimpairment.txt` | hearing loss, hard of hearing, HOH, deaf, presbycusis, uses hearing aids, cochlear implant |
| Numbness_neuropathy | `numbness_neuropathy` | Documentation of reduced, lost, or abnormal peripheral sensation, typically in the hands or feet, either reported by the patient (numbness, tingling, pins and needles, burning) or found on exam (diminished light touch, monofilament, vibration, or proprioception), including diagnosed peripheral neuropathy of any cause. Relevant to balance, gait, and fall risk. | `resources_regexp_renumbnessneuropathy.txt` | numbness, tingling, pins and needles, burning feet, peripheral neuropathy, decreased vibration sense, insensate to monofilament |

Each line of a regexp file is a keyword or regex (matched case-insensitively); `rules/resources_rules_matchrules.txt`
maps each file to its NORM. Negation / certainty / experiencer come from `context/contextRule.txt`.

## Run

From the repo root, `bash run_all_rules.sh` picks this model up automatically and writes
`results/Sensory/*.ann`. To run only this model:

```
bash run_MedTagger-fit-sensory_step1.sh            # ../notes -> data/output/*.ann
```
