# BRFV manuscript

## Last draft in this folder

draft_complete_v3 is the last draft in this folder. It is draft_complete_v2 with one addition, a column without controls at the start of Tables 8 and 9
(models BN and FN), and the sentences in Sections 3.6 and 4.5 that describe and report it. Step 08 wrote into this folder until 23 November 2026.
DRAFT_CURRENT in 02_code/brfv_00_config.py now names 06_final/draft_final_v5, and 06_final/BRFV_final_README.md describes the later drafts.
The file names were chosen by the author.

| File | What it is |
| --- | --- |
| draft_complete_v3/draft_complete_v3.tex | The manuscript. Prose, the two diagrams and the reference list |
| draft_complete_v3/draft_complete_v3.pdf | The compiled draft, 32 pages |
| draft_complete_v3/numbers.tex | Every number quoted in the text, as a macro. Written by step 08 |
| draft_complete_v3/tables/*.tex | One tabular per table. Written by step 08 |
| draft_complete_v3/figures/ | Copies of the pipeline figures and the sample flow chart. Written by step 08 |

draft_complete_v1 and draft_complete_v2 have the same five parts. The three drafts are kept as they were, and step 08 no longer writes into them.
Each compiles from the files in its own folder, with latexmk -pdf and the name of its .tex file, or after an upload of the folder to Overleaf.

## Versions

| Version | Date | State |
| --- | --- | --- |
| Claude doc draft v1 | 2026-11-18 | Sections 1 to 3 and the score descriptives, written before the Compustat data arrived. No regression result. A private working document, superseded by draft_complete_v1 |
| draft_complete_v1 | 2026-11-19 | Complete draft in LaTeX with all results, 13 tables in the text, 3 in the appendix and 6 figures |
| draft_complete_v2 | 2026-11-19 | The same paper without the author name, the date, the acknowledgements and the declaration on the use of generative AI. The link to the public repository stands before the abstract. No other change to the text, the tables or the figures |
| draft_complete_v3 | 2026-11-23 | draft_complete_v2 with a column without controls at the start of Tables 8 and 9 (models BN and FN). The column was added after the first results at the author's request and is read by rules stated before the run. 32 pages |

Rule: a number enters the manuscript only from a file in 03_output/tables, through tables/*.tex or numbers.tex. Counts from the public score
file that appear in sentences are protected by the comparison in step 01.

## Manuscript numbering and pipeline files (the drafts in this folder, BN and FN from draft_complete_v3 on)

The manuscript numbers tables and figures in order of appearance. The pipeline identifiers (Tnn, Fnn) stay fixed.

| In the manuscript | Content | LaTeX fragment | Pipeline source |
| --- | --- | --- | --- |
| Table 1 | Earlier evidence on biodiversity and firm value | typed in the .tex | the cited papers |
| Table 2 | Biodiversity scores by period | tab_scores_by_period | BRFV_T01_scores_by_year |
| Table 3 | Persistence of the Count score | tab_persistence | BRFV_T02_score_persistence |
| Table 4 | Survey exposure and disclosure by industry group | tab_industry | BRFV_industry_exposure_gics4 (interim) and BRFV_T08_industry_distribution |
| Table 5 | Summary statistics | tab_summary | BRFV_T05_summary_statistics |
| Table 6 | Firm-years with and without a positive Count score | tab_means | BRFV_T06_means_by_disclosure |
| Table 7 | Variation in the scores within the sample | tab_variation | BRFV_T14_identifying_variation |
| Table 8 | Industry-by-year effects (BN, B0 to B4) | tab_baseline | BRFV_T09_baseline_industry_year_fe |
| Table 9 | Firm and year effects (FN, F0 to F4) | tab_firm_effects | BRFV_T10_firm_fe |
| Table 10 | High-exposure industries (X1 to X3) | tab_exposure | BRFV_T11_industry_exposure |
| Table 11 | After the Kunming Declaration (E, EF, ED) | tab_event | BRFV_T12_after_kunming_declaration |
| Table 12 | Robustness checks (R1 to R10) | tab_robustness | BRFV_T13_robustness |
| Table 13 | Hypotheses and outcomes | typed in the .tex with macros | numbers.tex |
| Table A1 | Variable definitions | typed in the .tex | 05_docs/BRFV_data_dictionary.csv |
| Table A2 | Test of the meaning of the score year | tab_alignment | BRFV_T03_year_alignment_test |
| Table A3 | Correlations | tab_correlations | BRFV_T07_correlations |
| Figure 1 | Conceptual framework and hypotheses | TikZ in the .tex | none |
| Figure 2 | Research design | TikZ in the .tex | none |
| Figure 3 | Construction of the sample | figures/fig_sample_flow.tex | BRFV_T04_sample_attrition |
| Figure 4 | Share of firms with a positive score by year | BRFV_F01 png | BRFV_F01_disclosure_share_by_year |
| Figure 5 | Mean Tobin's Q by disclosure status | BRFV_F02 png | BRFV_F02_tobin_q_by_disclosure |
| Figure 6 | Coefficients under the two specifications | BRFV_F03 png | BRFV_F03_coefficients_main (from the T09 and T10 tidy files) |

Hypotheses in the manuscript: H1 negative tone, H2 regulation, H3 high-exposure industries, H4 the period after October 2021.
Model labels are listed in 05_docs/BRFV_naming_convention.md.
