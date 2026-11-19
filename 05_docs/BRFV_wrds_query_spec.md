# BRFV: how to pull the Compustat extract

The pipeline needs one file: 01_data/raw/compustat/BRFV_compustat_funda_raw.csv. There are two ways to make it. Both need your own WRDS account with Compustat North America. The data are licensed, so the file stays on your machine.

Before you start, check that your WRDS login still works and that your subscriber's terms allow this use.

Run the web query by hand, from an account that is your own. The WRDS terms of use (https://wrds-www.wharton.upenn.edu/users/tou/, read on 18 November 2026) do not allow scripted or automated queries on the website, and they treat the sharing of account credentials as grounds for closing the account. Automation is allowed on the WRDS Cloud server, which is what Route A uses. For this reason the AI assistant does not operate the web query form.

## Route A: script (WRDS Cloud)

```
pip install wrds
cd 02_code
python brfv_02_pull_compustat_wrds.py
```

The script asks for your WRDS user name and password, pulls the two tables below, joins them and writes the extract with a note of the query beside it. It was written from the standard WRDS names and has not been run in this project yet, so read its first run with care.

## Route B: WRDS web query, run by hand

1. WRDS, then Compustat - Capital IQ, then North America, then Fundamentals Annual.
2. Date variable: Fiscal Year. Range: 2013 to 2025.
3. Company codes: search the entire database.
4. Screening: Consolidation Level C, Industry Format INDL, Data Format STD, Population Source D, Currency USD. Company status: active and inactive.
5. Variables, by their Compustat names:

| Group | Names |
| --- | --- |
| Identifiers | gvkey, datadate, fyear, fyr, tic, cusip, conm, curcd, exchg, costat, fic |
| Format flags | indfmt, datafmt, popsrc, consol |
| Industry | sich, sic, gsector, ggroup, gind, gsubind |
| Balance sheet | at, ceq, seq, lt, dltt, dlc, ppent, che |
| Income and cash flow | sale, oibdp, ib, xrd, capx, dvc |
| Market | csho, prcc_f |

6. Output: comma-delimited text (.csv), no compression, date format YYYYMMDD.
7. Save the file as BRFV_compustat_funda_raw.csv in 01_data/raw/compustat.

## After either route

1. Add the file to 05_docs/BRFV_data_log.csv with the date, the size and the SHA-256 (step 03 prints the hash).
2. Run python brfv_99_run_all.py from 02_code.
3. Read 03_output/tables/BRFV_T03_year_alignment_test.md first. If the run stops there, the score file's year means something else than the setting says: change SCORE_YEAR_CONVENTION in brfv_00_config.py and rerun.
4. Read BRFV_T04_sample_attrition.md and the match rate in the log before looking at any regression.

## What the code needs at the least

gvkey, datadate, fyear, tic, cusip, at, ceq, csho, prcc_f, dltt, dlc, oibdp, ppent, sale, xrd, capx, che, dvc, ggroup, and one of sich or sic. The filters on country (fic = USA) and currency (curcd = USD) are applied only if those columns are present.
