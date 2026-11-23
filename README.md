# BRFV: Biodiversity Risk Disclosure and Firm Valuation

 Every project file carries the short code BRFV.

Question: is biodiversity risk, as US listed firms discuss it in their 10-K filings, reflected in firm valuation (Tobin's Q)?

Public repository: https://github.com/kartikey0029sharma/Biodiversity_Risk_Firm_Valuation. It holds the code, the documents, the result tables, the figures and the versions of the draft listed below. It holds no data.

## The draft

| Version | File | What it is |
| --- | --- | --- |
| V5_final (current) | 06_final/V5_final/V5_final.pdf | Version 5 after one more complete reading, with two sentences of the conclusions and three table notes corrected. 37 pages |
| Version 5 | 06_final/draft_final_v5/draft_final_v5.pdf | Version 4 after a review. Firm counts and rounding are corrected, the slope after 2021 is reported with its standard error, the two findings get their own checks (Tables A8 and A9), and the year of the scores is checked against filings on EDGAR (Tables A3 to A5). Step 08 writes into this folder |
| Version 4 | 06_final/draft_final_v4/draft_final_v4.pdf | The text of Version 3 in another layout, with a first page that holds the abstract and the word count, a table of contents and five sections |
| Version 3 | 04_manuscript/draft_complete_v3/draft_complete_v3.pdf | Version 2 with one more column at the start of the two main tables, which enters the three scores with the fixed effects and without the controls |
| Version 2 | 04_manuscript/draft_complete_v2/draft_complete_v2.pdf | The paper without the author name, the date, the acknowledgements and the declaration on the use of generative AI. It gives the link to this repository before the abstract |
| Version 1 | 04_manuscript/draft_complete_v1/draft_complete_v1.pdf | The first complete draft of 19 November 2026, which carries those four items |

Versions 1 and 2 have the same text, tables and figures from the abstract to the appendix. Each folder holds the LaTeX source beside the PDF. 06_final/BRFV_final_README.md says what Version 5 and V5_final changed. This is a working draft and it has not been peer reviewed.

Versions 1 to 4 read the year in the score file as the fiscal year of the report. A check against filings on EDGAR, made for Version 5, points to the calendar year of filing. Version 5 and V5_final say so in Section 3.3 and describe the lag of the scores accordingly. The earlier models were not changed, so their estimates are the same.

The results come from the pipeline runs of 19 and 23 November 2026 on 16,808 firm-years of 2,774 US non-financial firms, fiscal years 2015 to 2024. The run of 23 November added models and tables and corrected the firm counts and the rounding in the tables. No coefficient, standard error or p value of the first run changed.

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
| 05 | brfv_05_descriptives.py | Descriptive statistics | T05 to T08, T14, T17, F02 |
| 06 | brfv_06_estimate.py | Main regressions | T09 to T12 |
| 07 | brfv_07_robustness.py | Robustness checks | T13, T15, T16 |
| 08 | brfv_08_make_latex_assets.py | Turns the tables into LaTeX and collects every number quoted in the text | F03, and the tables, figures and numbers.tex of the current draft |

Every setting (paths, sample years, thresholds, the name of the current draft) is in 02_code/brfv_00_config.py.

## How to reproduce the results

1. Clone the repository and install the requirements as above.
2. Download the five score files of Giglio, Kuchler, Stroebel and Zeng (2026) from https://www.biodiversityrisk.org/download/ into 01_data/raw/giglio. Their names are listed in 01_data/raw/BRFV_raw_README.md. Step 01 stops if a file differs from the SHA-256 recorded in 02_code/brfv_00_config.py.
3. Pull the Compustat extract with your own WRDS access, as 05_docs/BRFV_wrds_query_spec.md describes, and save it as 01_data/raw/compustat/BRFV_compustat_funda_raw.csv.
4. Run python brfv_99_run_all.py from 02_code.
5. Check three points before reading any regression.
   - The log of step 01 says "comparison with recorded values: match".
   - 03_output/tables/BRFV_T03_year_alignment_test.md ends with the verdict fiscal. This is the result of the count test in step 04 and it matches the setting in the code. Section 3.3 of Version 5 explains why the year is now read as the year of filing.
   - 03_output/tables/BRFV_T04_sample_attrition.md ends with 16,808 firm-years and 2,774 firms.
6. Compare your tables with the tables in the repository. The command git diff 03_output/tables shows every difference.
7. Compile the draft with latexmk -pdf draft_final_v5.tex inside 06_final/draft_final_v5, or upload that folder to Overleaf. Step 08 has already written the tables, the figures and every quoted number into it. 06_final/V5_final holds copies of the same files beside its own source.
8. Tables A3 to A5 and the numbers on filings in Section 3.3 come from a small file of filing dates and sentence counts, collected by hand from public filings on EDGAR on 23 November 2026. The note 01_data/raw/edgar/BRFV_edgar_timing_check_README.md describes how it was made. The file itself is not stored here and is available from the author. Step 08 reads it if it is present. Without it, step 08 leaves these three tables as they are and writes numbers.tex without the numbers that come from the file. In that case compare your numbers.tex with the stored one, then restore the stored one with git checkout before you compile.

A later Compustat extract can give slightly different numbers, because Compustat is revised over time. The extract used here is recorded in 05_docs/BRFV_data_log.csv with its date, size and SHA-256. Other package versions can change the last decimal places.

## Folder map

| Folder | Holds | Rule |
| --- | --- | --- |
| 01_data/raw | Files exactly as their source gave them | Never edited, never renamed (except the Compustat extract, which you name). Empty in the repository apart from two notes |
| 01_data/interim | One cleaned file per source | Rebuilt by code, never edited by hand. Empty in the repository |
| 01_data/processed | The firm-year analysis panel | Rebuilt by code. Empty in the repository |
| 02_code | Pipeline scripts, numbered in run order, and tests | One rule lives in one place: brfv_00_config.py |
| 03_output/tables | Tables T01 to T17 as .csv and .md | Written by code only |
| 03_output/figures | Figures F01 to F03 as .png | Written by code only |
| 03_output/logs | Run logs | One log per run. Not kept in the repository |
| 04_manuscript | Versions 1 to 3 of the draft with their tables, figures and quoted numbers, and the version log | Tables and numbers are written by step 08, never typed |
| 06_final | Versions 4 and 5 and V5_final, with a note on what each one changed | Step 08 writes into draft_final_v5. The other two folders hold copies of its files |
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
- The check of the score year uses a small file of facts collected by hand from public filings on EDGAR. It is described in 01_data/raw/edgar/BRFV_edgar_timing_check_README.md and is not stored here.

Two documents that belong to other parties (the original dissertation plan and a university handbook) sit in the author's working folder and are not part of the repository.

