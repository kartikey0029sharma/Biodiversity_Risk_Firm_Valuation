# BRFV: Biodiversity Risk Disclosure and Firm Valuation

 Every project file carries the short code BRFV.

Question: is biodiversity risk, as US listed firms discuss it in their 10-K filings, reflected in firm valuation (Tobin's Q)?

Public repository: https://github.com/kartikey0029sharma/Biodiversity_Risk_Firm_Valuation. It holds the code, the documents, the result tables, the figures and two versions of the draft. It holds no data.

## The draft

| Version | File | What it is |
| --- | --- | --- |
| Version 2 (current) | 04_manuscript/draft_complete_v2/draft_complete_v2.pdf | The paper without the author name, the date, the acknowledgements and the declaration on the use of generative AI |
| Version 1 | 04_manuscript/draft_complete_v1/draft_complete_v1.pdf | The first complete draft of 19 November 2026, which carries those four items |

The two versions have the same text, tables and figures from the abstract to the appendix. Each folder holds the LaTeX source beside the PDF. This is a working draft and it has not been peer reviewed.

The results come from the pipeline run of 19 November 2026 on 16,808 firm-years of 2,774 US non-financial firms, fiscal years 2015 to 2024.

## How to run the code

The code is written in Python and was tested with Python 3.10 and 3.13.

```
pip install -r requirements.txt
cd 02_code
python -m pytest tests -q          # checks the code on invented data, needs no data file
python brfv_99_run_all.py          # runs steps 01, 03, 04, 05, 06, 07 and 08 on the real data
```

The tests need no data. The full run needs the two data sources described in the next section, and it stops with a clear message at the first step whose input is missing. Each step can also be run on its own, for example python brfv_06_estimate.py.

| Step | Script | What it does | What it writes |
| --- | --- | --- | --- |
| 01 | brfv_01_import_scores.py | Checks the score files against their SHA-256 and cleans them | T01, T02, F01 |
| 02 | brfv_02_pull_compustat_wrds.py | Optional. Pulls the Compustat extract from WRDS Cloud. Run by hand, because it asks for your WRDS login | The raw Compustat extract |
| 03 | brfv_03_build_compustat.py | Builds the firm-year variables, Tobin's Q among them | The cleaned Compustat file |
| 04 | brfv_04_build_panel.py | Matches scores to firms, tests the meaning of the score year and builds the panel | T03, T04, the analysis panel |
| 05 | brfv_05_descriptives.py | Descriptive statistics | T05 to T08, T14, F02 |
| 06 | brfv_06_estimate.py | Main regressions | T09 to T12 |
| 07 | brfv_07_robustness.py | Robustness checks | T13 |
| 08 | brfv_08_make_latex_assets.py | Turns the tables into LaTeX and collects every number quoted in the text | F03, and the tables, figures and numbers.tex of the current draft |

Every setting (paths, sample years, thresholds, the name of the current draft) is in 02_code/brfv_00_config.py.

## How to reproduce the results

1. Clone the repository and install the requirements as above.
2. Download the five score files of Giglio, Kuchler, Stroebel and Zeng (2026) from https://www.biodiversityrisk.org/download/ into 01_data/raw/giglio. Their names are listed in 01_data/raw/BRFV_raw_README.md. Step 01 stops if a file differs from the SHA-256 recorded in 02_code/brfv_00_config.py.
3. Pull the Compustat extract with your own WRDS access, as 05_docs/BRFV_wrds_query_spec.md describes, and save it as 01_data/raw/compustat/BRFV_compustat_funda_raw.csv.
4. Run python brfv_99_run_all.py from 02_code.
5. Check three points before reading any regression.
   - The log of step 01 says "comparison with recorded values: match".
   - 03_output/tables/BRFV_T03_year_alignment_test.md ends with the verdict fiscal.
   - 03_output/tables/BRFV_T04_sample_attrition.md ends with 16,808 firm-years and 2,774 firms.
6. Compare your tables with the tables in the repository. The command git diff 03_output/tables shows every difference.
7. Compile the draft with latexmk -pdf draft_complete_v2.tex inside 04_manuscript/draft_complete_v2, or upload that folder to Overleaf. Step 08 has already written the tables, the figures and every quoted number into it.

A later Compustat extract can give slightly different numbers, because Compustat is revised over time. The extract used here is recorded in 05_docs/BRFV_data_log.csv with its date, size and SHA-256. Other package versions can change the last decimal places.

## Folder map

| Folder | Holds | Rule |
| --- | --- | --- |
| 01_data/raw | Files exactly as their source gave them | Never edited, never renamed (except the Compustat extract, which you name). Empty in the repository |
| 01_data/interim | One cleaned file per source | Rebuilt by code, never edited by hand. Empty in the repository |
| 01_data/processed | The firm-year analysis panel | Rebuilt by code. Empty in the repository |
| 02_code | Pipeline scripts, numbered in run order, and tests | One rule lives in one place: brfv_00_config.py |
| 03_output/tables | Tables T01 to T14 as .csv and .md | Written by code only |
| 03_output/figures | Figures F01 to F03 as .png | Written by code only |
| 03_output/logs | Run logs | One log per run. Not kept in the repository |
| 04_manuscript | The two drafts with their tables, figures and quoted numbers, and the version log | Tables and numbers are written by step 08, never typed |
| 05_docs | Naming convention, data dictionary, data log, WRDS query, AI-use log | Updated whenever data or method changes |

## Error proofs built into the code

- Raw score files are checked against the SHA-256 recorded on the download day.
- Step 01 must reproduce the row counts recorded on 18 November 2026, or it stops.
- Identifiers are read as text, so the tickers NA and TRUE and CUSIPs with leading zeros survive.
- Step 04 tests whether the score file's year is the fiscal year or the filing year, and stops if the data contradict the setting.
- One row per firm and fiscal year is asserted after every merge.
- Every table is written by code. No number in the manuscript is typed from memory.
- The list of regression models was fixed before any firm-level data were merged.

## Data

No data file is stored in the repository.

- The biodiversity scores are the public files of Giglio, Kuchler, Stroebel and Zeng (2026). They are not copied here. Please take them from the source page and cite the paper.
- Compustat data are licensed and cannot be shared.
- The tables in 03_output are aggregate results. The interim and processed data files are rebuilt by the code and are listed in .gitignore.
- The test fixture in 02_code/tests is invented data, written to a temporary folder when the tests run. It never feeds a table, a figure or a sentence of the draft.

Two documents that belong to other parties (the original dissertation plan and a university handbook) sit in the author's working folder and are not part of the repository.

