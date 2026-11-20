# Medication Reconciliation Concern NLP Algorithm (MedTaggerIE rules)

Rule-based extraction of the **Medications** feature class (see `Appendix_NLP_Feature_Definitions_20261028.docx`) from clinical
notes, using the same MedTaggerIE setup as `musculoskeletal/`, `gait_and_balance/` and `delirium/`
(`MedTagger-fit-context.jar`, Java 1.8+).

## Concepts

| NORM | Schema feature | Definition | Rule file (`models/Medication_Reconciliation_Concern/regexp/`) | Examples |
| --- | --- | --- | --- | --- |
| Medication_reconciliation_concern | `medication_reconciliation_concern` | Documentation of a discrepancy or problem identified during medication reconciliation, such as a missing, duplicate, or conflicting medication. | `resources_regexp_remedreconconcern.txt` | medication discrepancy, duplicate bottles / therapeutic duplication, not on the medication list, prescription never filled, conflicting medication lists |

Each line of a regexp file is a keyword or regex (matched case-insensitively); `rules/resources_rules_matchrules.txt`
maps each file to its NORM. Negation / certainty / experiencer come from `context/contextRule.txt`.

A routine reconciliation with no problem (`Medication list reconciled ... all medications confirmed`) is deliberately
not matched: only the discrepancy or problem itself (missing, duplicate, conflicting, unfilled) is tagged.

## Run

From the repo root, `bash run_all_rules.sh` picks this model up automatically and writes
`results/Medication_Reconciliation_Concern/*.ann`. To run only this model:

```
bash run_MedTagger-fit-medication_reconciliation_concern_step1.sh            # ../notes -> data/output/*.ann
```
