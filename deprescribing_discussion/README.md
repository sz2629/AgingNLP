# Deprescribing Discussion NLP Algorithm (MedTaggerIE rules)

Rule-based extraction of the **Medications** feature class (see `Appendix_NLP_Feature_Definitions_20261028.docx`) from clinical
notes, using the same MedTaggerIE setup as `musculoskeletal/`, `gait_and_balance/` and `delirium/`
(`MedTagger-fit-context.jar`, Java 1.8+).

## Concepts

| NORM | Schema feature | Definition | Rule file (`models/Deprescribing_Discussion/regexp/`) | Examples |
| --- | --- | --- | --- | --- |
| Deprescribing_discussion | `deprescribing_discussion` | Documentation of a discussion about stopping or reducing a medication to lower risk or pill burden, including any mention that a medication has been stopped or discontinued. Excludes temporary deprescription for a procedure (a medication held before and resumed after surgery, endoscopy, imaging, or another procedure). | `resources_regexp_redeprescribing.txt` | deprescribing, tapered off, discontinued, stopped, dose reduced, reduce the gabapentin dose, wean off |

Each line of a regexp file is a keyword or regex (matched case-insensitively); `rules/resources_rules_matchrules.txt`
maps each file to its NORM. Negation / certainty / experiencer come from `context/contextRule.txt`.

Temporary holds around a procedure are excluded, per the Appendix: the lexicon does not match `held`/`hold`, and
model-specific context rules (end of `context/contextRule.txt`) negate stop/discontinue mentions followed by
`before/prior to <procedure>` or `resumed after`. Non-medication uses such as `stopped smoking` are excluded too.

## Run

From the repo root, `bash run_all_rules.sh` picks this model up automatically and writes
`results/Deprescribing_Discussion/*.ann`. To run only this model:

```
bash run_MedTagger-fit-deprescribing_discussion_step1.sh            # ../notes -> data/output/*.ann
```
