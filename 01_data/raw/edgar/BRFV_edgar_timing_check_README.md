# BRFV: check of the score year against filings on EDGAR

File: `BRFV_edgar_timing_check_20261123.csv`. Collected on 23 November 2026 from the public pages of the SEC (EDGAR), through the browser. No licensed data are involved. Step 08 reads the file and writes Tables A3 to A5 of the draft and the numbers quoted in Section 3.3.

## Question

The score file of Giglio et al. has a column `year`. The codebook does not say whether it is the fiscal year that a 10-K reports on or the calendar year in which the 10-K was filed. For a firm with a December year end the two differ by one.

## Sources on EDGAR

- Ticker to registrant: `https://www.sec.gov/files/company_tickers.json` (current tickers only).
- Filing dates and report dates of each Form 10-K: `https://data.sec.gov/submissions/CIK##########.json`, with the older batches listed in that file.
- Text of a filing: the primary document of the Form 10-K, at `https://www.sec.gov/Archives/edgar/data/<cik>/<accession number without dashes>/<primary document>`.

## Panels in the file

`switch`. Firms in the score file with three years in which all three scores are zero, followed by two years with Count = 1 (first of these years between 2015 and 2022, same CUSIP in all five years). The rule gives 41 tickers. Of these, 34 are in the current ticker list of the SEC and 26 of those report for a December year end. For each of the 26, the file holds the dates of the three Forms 10-K filed in the year before the first year with Count = 1, in that year and in the year after (`filed_1` to `filed_3`), and the number of sentences with a biodiversity word in each (`n_1` to `n_3`). `ref_year` is the first year with Count = 1.

`history`. Four of these firms, with the count for every Form 10-K filed from 2015 to 2024. `ref_year` is the year of filing and `n_1` the count.

`leaver`. Ten tickers whose last year in the score file lies between 2015 and 2021, with Count = 1 in the year before and Count = 0 in the last year. There are 29 such tickers. The ten are those whose registrant could be identified on EDGAR with certainty. `filed_1` is the date of the Form 10-K filed in the last year (`ref_year`).

`entrant`. Tickers whose first year in the score file lies between 2015 and 2022 and has Count = 1. There are 36. `status` says what EDGAR shows for each: the first Form 10-K of the registrant was filed in that first year, the registrant had filed in earlier years, the ticker is used by another company today, or the ticker is no longer listed. `filed_1` is the date of the first Form 10-K.

## How sentences were counted

The primary document was read as HTML. The inline XBRL header, scripts and styles were removed, and white space was collapsed. The text was split after a full stop, semicolon, exclamation mark or question mark that is followed by white space and a capital letter, an opening bracket or an opening quotation mark. A sentence was counted if it matched this pattern, without regard to case:

```
\b(biodiversity|ecosystems?|ecology|ecological|habitats?|species|rainforests?|forests?|deforestation|fauna|flora|marine|tropical|freshwater|wetlands?|wildlife|corals?|aquatic|desertification|carbon sinks?|ecosphere|biosphere)\b
```

The count is a simple measure of how much a filing says about nature. It is not the classification of Giglio et al., who use a language model on top of a dictionary. It is used here only to see in which filing the text changes.

## Rule for reading the `switch` panel

Fixed before the filings were read. A firm is informative if `n_3 - n_1` is 2 or more. It then supports the filing year if `n_2` is at least the mean of `n_1` and `n_3`, because the new text is already in the 10-K filed in the first year with Count = 1. Otherwise it supports the fiscal year, because the new text comes only with the 10-K filed one year later, which reports on that year. The function `edgar_reading` in step 08 applies the rule.

## Limits

The firms are large, still listed and have a December year end. The word count is a proxy. The check was done once, by one tool, on one day. A confirmation by the authors of the scores would settle the question.
