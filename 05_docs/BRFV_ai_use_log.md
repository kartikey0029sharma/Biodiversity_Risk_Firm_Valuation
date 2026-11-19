# BRFV: AI-use log

A dated record of what the AI assistant did in this project, so that its use can be disclosed accurately wherever the paper is submitted. Add a row for every session. Tool: Claude (Anthropic).

| Date | What the assistant did | What you still need to check yourself |
| --- | --- | --- |
| 2026-11-18 | Read the original proposal and the NBS8020 handbook. Checked the proposal against the published literature and the data source, and wrote the completion plan (Claude doc) | The corrections and the suggested contribution |
| 2026-11-18 | Downloaded the public score files from biodiversityrisk.org through Chrome and recorded their SHA-256. Counted rows, years and score values in the firm-level file | That the zip is in the project folder and step 01 reports "comparison with recorded values: match" |
| 2026-11-18 | Designed the folder structure and naming convention. Wrote the pipeline (02_code), the tests and the documentation (05_docs) | Read each script once. Run the tests. The WRDS script has not been run against WRDS |
| 2026-11-18 | Wrote manuscript draft v1 (Claude doc): abstract, Sections 1 to 3, the score descriptives and the industry exposure table in Section 4, the list of pending tables, provisional conclusions, references and the variable appendix. Checked every reference against a source record | Every citation against the article itself before submission. All regression results, which do not exist yet |
| 2026-11-18 | Opened the Compustat Fundamentals Annual query form in Chrome at KT's request and read its layout. Did not run the query, because the WRDS terms of use do not allow automated queries on the website. No Compustat data were extracted or seen by the assistant | Run the web query by hand from an account you are entitled to use, or use Route A on WRDS Cloud |
| 2026-11-18 | Checked the Compustat extract that KT pulled by hand and placed in 01_data (pejxebqwplt8cnd9.csv, 171,714 rows). Read on KT's computer: column names and aggregate counts only, no firm-level rows. CSHO is missing, so Tobin's Q cannot be built; the other items, filters and fiscal years are in order | Re-run the same query with CSHO added |
| 2026-11-18 | Rechecked the second extract that KT pulled by hand: all required items are present (popsrc, which is optional, is not). Renamed it to BRFV_compustat_funda_raw.csv, moved it to 01_data/raw/compustat and ran step 03 on KT's computer (157,599 firm-years, 22,448 firms). Column names and aggregate counts only, no firm-level rows | Put the score files in the folder; steps 01 and 04 to 07 wait for them |
| 2026-11-19 | Ran steps 01 and 03 to 08 on the real data on KT's computer after KT placed the score zip in the folder. Step 01 confirmed the hashes and the recorded counts. Read logs and aggregate tables only, no firm-level Compustat rows | The timing test in 03_output/tables/BRFV_T03_year_alignment_test.md and the reasoning in Section 3.3 of the draft |
| 2026-11-19 | Wrote step 08, which turns the pipeline tables into LaTeX tables and into macros for every quoted number. Wrote the complete LaTeX draft draft_complete_v1 (text, two diagrams, reference list) and compiled it | Every sentence that interprets a result in Sections 4 to 6, the reference list against the articles, and the wording of the acknowledgement |
| 2026-11-19 | At KT's request, made draft_complete_v2 from draft_complete_v1 by removing the author name, the date, the acknowledgements and the declaration on the use of generative AI. Nothing else in the text was changed. Pointed step 08 to the new folder and rewrote the README (how to run, how to reproduce) | Where the declaration on AI use and the acknowledgement are to be given at submission, since Version 2 does not carry them |
| 2026-11-19 | At KT's request, created the public GitHub repository kartikey0029sharma/Biodiversity_Risk_Firm_Valuation through KT's signed-in Chrome. GitHub refused the first push, so with KT's approval installed the Claude GitHub app on KT's account for this one repository, and then pushed the code, the documents, the result tables, the figures and both drafts. Before the push, checked that no data file, no third-party document and no private detail was among the files, and compared the files with the folder on KT's computer | That the public page shows what you want others to see. Both drafts are public from this date. The app can be removed in the GitHub settings under Applications |

## Model list fixed before the data

The regressions B0 to B5, F0 to F5, X1 to X3, E1 to E3, EF1 to EF3, ED1 to ED3 and R1 to R9 (R10 was added on 19 November 2026, see below) were written into brfv_06_estimate.py and brfv_07_robustness.py on 18 November 2026, before any Compustat data were merged. Record below any model added or changed after the first real run, with the date and the reason.

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-18 | Exposure models relabelled from H1-H3 to X1-X3. No regression was changed | H1 to H4 are the hypotheses in the manuscript, and one letter should not mean two things |
| 2026-11-18 | Added ED1 to ED3: the event models E1 to E3 without fiscal year 2021 | In fiscal year 2021 firms with a December year end are valued after the Kunming Declaration, but the year counts as pre-period. Added on the day the list was fixed, before any firm-level data were merged |
| 2026-11-19 | Timing test extended: when the entry and exit years disagree, step 04 now checks which boundary row is empty (all scores zero). Added R10, the same model with the score of the next score year | On the real data the first test was not conclusive (entry years pointed to the fiscal year, exit years to the filing year). The rows after a firm's last fiscal year turned out to be empty for all 627 firms, which supports the fiscal year. R10 shows the result under the other reading. Both were added before any regression was run on real data |
| | | |

## Draft wording for a disclosure statement

"The authors used Claude (Anthropic) to check the research design against the literature, to write and test the analysis code, and to prepare a first draft of the text. The authors reviewed and edited all content and take full responsibility for the paper." Adapt it to the policy of the journal or institution.
