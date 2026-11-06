# AgingNLP - Gait and Balance Rule-Based Scoring

A lightweight keyword + regular-expression scorer that ranks clinical notes by how much
gait and balance evidence they contain. Rule definitions come from
`Appendix_NLP_Feature_Definitions_20261028.docx`.

## Sub-features (`gait_and_balance` concept)

| Sub-feature | Keywords | Regex |
|---|---|---|
| `gait_abnormality` | unsteady gait, shuffling gait, wide-based gait, slow gait | `\b(unsteady\|shuffling\|wide[- ]based\|slow(ed)?\|abnormal)\s+(gait\|walk(ing)?)\b` |
| `balance_impairment` | poor balance, impaired balance, unsteadiness, loss of balance | `\b(poor\|impaired\|reduced\|loss of\|difficulty (with\|keeping\|maintaining))\s+balance\b` |
| `unsafe_ambulation` | ambulating without assistance, unsafe ambulation, walking without walker | `\b(walk\|walks\|walking\|ambulat\w+)\s+(without\|against)\s+(\w+\s+){0,2}(assist\w*\|walker\|cane\|restrictions?\|orders?)\b` |

`score_notes.py` also contains rules for other concepts (`musculoskeletal`, `sensory`,
`cardiovascular`, `mental_health`, `laboratory_and_nutrition`, `medication`), selectable with
`--concept`.

## Scoring

`score = keyword matches + regex matches` — case-insensitive, and every occurrence counts.
A phrase matched by both a keyword and a regex (e.g. "unsteady gait") counts twice.

## Usage

Requires Python 3 (standard library only). Input is a directory of `.txt` notes, one note per
file; the file name (without `.txt`) is the note ID.

```bash
python score_notes.py --concept gait_and_balance --notes_dir ../notes --top_n 3
```

## Output

Written to the current working directory:

| File | Contents |
|---|---|
| `gait_and_balance_scores.csv` | `note_id, score` for every note |
| `gait_and_balance_scores_with_evidence.csv` | `note_id, score, evidence` for every note |
| `gait_and_balance_top_n_file_ids.csv` | `note_id` of the top-n notes |
| `gait_and_balance_top_n_with_evidence.csv` | `rank, note_id, score, evidence` for the top-n notes |

Ties are broken by note ID order. Matched phrases and counts are also printed to the terminal.
