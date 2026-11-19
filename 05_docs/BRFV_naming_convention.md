# BRFV naming convention

One convention for folders, files, variables, tables and versions. Follow it for every new item, so that a name tells what the thing is and where it sits in the flow.

## Project code

BRFV = Biodiversity Risk Disclosure and Firm Valuation. Every file made inside the project starts with it, except raw files, which keep the name their source gave them.

## Folders

Two digits, an underscore, then a lower-case noun. The number is the order of the flow.

| Folder | Meaning |
| --- | --- |
| 01_data/raw | as received |
| 01_data/interim | cleaned, one file per source |
| 01_data/processed | merged analysis panel |
| 02_code | scripts and tests |
| 03_output/tables, figures, logs | everything the code writes for the paper |
| 04_manuscript | drafts and exports |
| 05_docs | documentation |

## Files

| Kind | Pattern | Example |
| --- | --- | --- |
| Script | brfv_NN_verb_object.py, NN = run order | brfv_04_build_panel.py |
| Shared code | brfv_00_config.py, brfv_utils.py | |
| Test | test_brfv_*.py | test_brfv_pipeline.py |
| Raw data | source name, unchanged | 10k_biodiversity_scores_2024.csv |
| Raw data you name | BRFV_source_content_raw.csv | BRFV_compustat_funda_raw.csv |
| Interim and processed data | BRFV_content_level_state.csv | BRFV_scores_firmyear_clean.csv |
| Table | BRFV_Tnn_content.csv and .md | BRFV_T09_baseline_industry_year_fe.csv |
| Long-form coefficients | table name + _tidy.csv | BRFV_T09_baseline_industry_year_fe_tidy.csv |
| Figure | BRFV_Fnn_content.png | BRFV_F01_disclosure_share_by_year.png |
| Log | BRFV_run_runid.log | BRFV_run_20261118_221500.log |
| Run manifest | BRFV_run_manifest_runid.json | |
| Document | BRFV_content.md or .csv | BRFV_data_dictionary.csv |
| Dated snapshot | BRFV_content_vNN_YYYYMMDD.ext | BRFV_manuscript_v01_20261118.docx |
| Manuscript draft | name given by the author, in its own folder under 04_manuscript. The current draft is named in DRAFT_CURRENT of brfv_00_config.py, and earlier drafts are kept as they were | draft_complete_v2/draft_complete_v2.tex |
| LaTeX table fragment | tab_content.tex, written by step 08 | tab_baseline.tex |

Rules: lower case with underscores for code and data; no spaces; dates as YYYYMMDD; versions as v01, v02. The numbers in Tnn and Fnn are pipeline identifiers: they follow the order in which the code writes the files, they stay fixed, and they are never reused. The manuscript numbers its tables and figures in order of appearance, which can change with every revision. The link between the two is kept in 04_manuscript/BRFV_manuscript_README.md.

## Variables

snake_case, with a prefix that says what kind of variable it is and a suffix that says what was done to it.

| Prefix | Kind | Examples |
| --- | --- | --- |
| id_ | identifier | id_gvkey, id_cusip8, id_ticker |
| t_ | time | t_fyear, t_score_year, t_fye_month |
| dv_ | dependent variable | dv_tobin_q |
| bd_ | biodiversity score, firm level | bd_count, bd_negative, bd_regulation |
| ctl_ | control | ctl_size, ctl_leverage |
| fin_ | raw financial item | fin_at, fin_mve |
| ind_ | industry code or industry-level measure | ind_gics4, ind_bio_high |
| geo_ | geography | geo_fic |
| ev_ | event indicator | ev_post |
| cc_ | climate exposure | cc_exposure_lag |
| ix_ | interaction term | ix_count_high |
| fe_ | fixed-effect key | fe_ind_year |
| mrg_ | merge bookkeeping | mrg_source |

| Suffix | Meaning |
| --- | --- |
| _lag | the value known before Tobin's Q is measured |
| _lead | the value disclosed two fiscal years later (placebo only) |
| _alt | the score of the next score year, used only in robustness check R10 (the other reading of the score year) |
| _w | winsorised at the 1st and 99th percentiles |
| _pos | indicator that the base variable is above zero |
| _z | standardised |
| _indadj | minus the industry-year median |

Suffixes stack in the order transform then timing then winsorising, for example bd_negative_pos_lag.

## Models

| Label | Family |
| --- | --- |
| B0 to B5 | baseline, industry group by year fixed effects (Table T09) |
| F0 to F5 | firm and year fixed effects (Table T10) |
| X1 to X3 | score times high-exposure industry (Table T11) |
| E1 to E3, EF1 to EF3, ED1 to ED3 | score times the period after October 2021 (Table T12). EF = firm and year effects. ED = models E without the transition fiscal year 2021 |
| R1 to R10 | robustness checks (Table T13) |

Within a family, 1 = count, 2 = negative, 3 = regulation, 4 = all three, 5 = all three plus climate exposure.

The letter H is not used for models. H1 to H4 are the hypotheses in the manuscript: H1 negative tone, H2 regulation, H3 high-exposure industries, H4 the period after October 2021.

## Changing a rule

Sample rules, years and thresholds live only in 02_code/brfv_00_config.py. Change them there, rerun brfv_99_run_all.py, and note the change with its date in 05_docs/BRFV_ai_use_log.md or a change log.
