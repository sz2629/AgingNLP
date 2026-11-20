# Laboratory and Nutrition NLP Algorithm (MedTaggerIE rules)

Rule-based extraction of the **Laboratory and Nutrition** feature class (see `Appendix_NLP_Feature_Definitions_20261028.docx`) from clinical
notes, using the same MedTaggerIE setup as `musculoskeletal/`, `gait_and_balance/` and `delirium/`
(`MedTagger-fit-context.jar`, Java 1.8+).

## Concepts

| NORM | Schema feature | Definition | Rule file (`models/Laboratory_and_Nutrition/regexp/`) | Examples |
| --- | --- | --- | --- | --- |
| Malnutrition | `malnutrition` | Documentation of malnutrition or inadequate nutritional intake, including unintended weight loss, low intake, or clinical signs of undernutrition. | `resources_regexp_remalnutrition.txt` | malnutrition, malnourished, cachexia, unintentional weight loss, lost 12 lbs, poor appetite / oral intake, temporal wasting, BMI < 18.5, albumin < 3.5 |

Each line of a regexp file is a keyword or regex (matched case-insensitively); `rules/resources_rules_matchrules.txt`
maps each file to its NORM. Negation / certainty / experiencer come from `context/contextRule.txt`.

## Run

From the repo root, `bash run_all_rules.sh` picks this model up automatically and writes
`results/Laboratory_and_Nutrition/*.ann`. To run only this model:

```
bash run_MedTagger-fit-laboratory_and_nutrition_step1.sh            # ../notes -> data/output/*.ann
```
