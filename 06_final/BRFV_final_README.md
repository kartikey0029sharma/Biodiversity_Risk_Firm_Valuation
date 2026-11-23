# BRFV final drafts, versions 4 and 5

V5_final is the current draft. It is version 5 after one more complete reading. All drafts here follow the pattern of the MSc dissertation handbook in the project folder. They were made on 23 November 2026 for publication on a website and carry no university cover page.

| File | What it is |
| --- | --- |
| V5_final/V5_final.tex | The LaTeX source of V5_final, the current draft |
| V5_final/V5_final.pdf | The compiled draft, 37 pages |
| V5_final/numbers.tex, tables, figures | Copies of the files that step 08 wrote for draft_final_v5. They are the same byte for byte |
| draft_final_v5/draft_final_v5.tex | The LaTeX source of version 5 as first delivered, kept as it was |
| draft_final_v5/draft_final_v5.pdf | Its compiled draft, 37 pages |
| draft_final_v5/numbers.tex, tables, figures | Written by step 08 of the pipeline |
| draft_final_v4/ | Version 4, kept as it was. Its numbers.tex, tables and figures are copies of the files that step 08 wrote for draft_complete_v3 |

## What V5_final changes

The review list came a second time, with twelve of its fourteen points. Each of the twelve was checked against draft_final_v5 and was already in it. The whole draft was then read once more, and five small corrections were made. No code, table or number changed.

| Place | Before | Now |
| --- | --- | --- |
| Conclusions, on fiscal year 2022 | the first fiscal years that end after the Kunming Declaration | the first fiscal year in which every year end falls after the Kunming Declaration. Fiscal year 2021 also holds year ends after the declaration |
| Conclusions, third practical point | The last year of a firm in the file carries no score although a report was filed in that year | The last row of a firm that leaves the file can be empty although a report was filed in that year. In the score file some last rows do carry a score |
| Note of the table of industry groups | a few firms with a financial GICS code remain | some firms. The table shows 230 such firm-years |
| Note of the table on the period after the declaration | The last row is the sum of the two coefficients | computed before rounding, since the rounded entries can add up to a figure that differs by 0.001 |
| Note of Table A9 | The third column is the sum of the first two | computed before rounding |

The word count is 11,969 and the abstract has 299 words. Sections, tables and page breaks are as in draft_final_v5. The timing section and its tables are kept.

## What version 5 changes

Version 5 answers a review of version 4. The writing style is the same.

| Review point | What was done |
| --- | --- |
| Firm counts in the tables with firm effects | Firms are counted on the firm-years that enter the estimate: 2,464 with firm effects, 2,772 with industry-by-year effects |
| Text and tables differed by 0.001 | Every figure is rounded once, from the value as computed. Text and tables are built from the same numbers |
| High-exposure share 39.8 or 39.7 | 39.7. Two financial groups above the cut-off count as high exposure, and the table of industry groups now says so |
| Row counts of the score file | 48 rows without a score lie in the year 2000, so the two rules remove 3,153 rows |
| Conclusion on fiscal year 2022 | Reworded: the first fiscal years that end after the Kunming Declaration. Made exact in V5_final |
| Table of correlations not cited | Cited in Section 4.5 |
| Transportation missing in the text | Named in Sections 4.3 and 4.6 |
| References | The letter in Pástor is a real glyph, item names are upright in formulas, three DOIs added after checking them, the conference paper of He (2024) is named as such |
| The headline result depends on the column | The rule of 18 November names the model with the three scores together. By the same rules a result in one specification only is weak evidence, and the draft says so |
| Robustness aimed at the null results | Checks W0 to W10 on tone within firms and P0 to P9 on Regulation times Post, Tables A8 and A9 |
| Placebo | The old test is described as a test across firms. A lead term in the model with firm effects is check W9 |
| H4 | The slope from fiscal year 2022 is reported with its standard error in Table 11 |
| Timing | Checked against filings on EDGAR, Tables A3 to A5. See below |
| Climate control | Not added. The data are public, and a download needs the author's permission. The limitation is stated plainly |

## What the checks found

- No earlier coefficient, standard error or p value changed.
- The year in the score file appears to be the year of filing, not the fiscal year. Section 3.3 of versions 1 to 4 concluded the opposite. The models were not changed: the main regressor is the score of year t-1, now described as the 10-K filed in the previous calendar year. The score of year t is used in checks R10, W10 and P8.
- Tone within firms: -0.063 with the three scores together (p 0.033), -0.053 alone (p 0.059), -0.020 with industry-by-year effects added, 0.006 with the score of the same year.
- Regulation times Post: -0.175 (p 0.048), -0.200 with the score of the same year (p 0.032). The slope after 2021 is -0.179 (p 0.119).

## How version 5 follows the handbook

| Handbook | In this draft |
| --- | --- |
| Not more than 12,000 words, without the reference list, the appendices and the contents page, with the count on the title page | 11,962 words, stated on the first page. V5_final has 11,969 |
| Clear font, size 12, one and a half line spacing | Times, 12 point, one and a half line spacing |
| Abstract of not more than 300 words on one page, single spacing allowed | 299 words on the first page, single spaced |
| Table of contents | Page 2 |
| Introduction, literature review, methodology and data, empirical results and discussion, conclusions | Sections 1 to 5 in this order |
| Contribution of AI tools acknowledged | Not in this draft, as in version 4 |
| Title page with name, university number and degree programme | Left out. A cover page was not wanted |

The table of the ten robustness checks is Table A7 in the appendix in version 5. It was Table 12 in version 4. This keeps the count within the limit.

## Rebuild

Step 08 writes numbers.tex, tables and figures into 06_final/draft_final_v5 (DRAFT_CURRENT in brfv_00_config.py). Compile with latexmk -pdf draft_final_v5.tex. If the text changes, count the words again and update the number in the preamble (the macro wordcount). Version 4 is not rewritten by the pipeline, and neither is V5_final. If the pipeline is run again and any number changes, copy numbers.tex, tables and figures from draft_final_v5 into V5_final and compile V5_final.tex.
