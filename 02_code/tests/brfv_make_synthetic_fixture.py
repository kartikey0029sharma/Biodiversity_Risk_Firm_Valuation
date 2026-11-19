"""BRFV test fixture: an INVENTED data set with the same layout as the real files.

Project : Biodiversity Risk Disclosure and Firm Valuation (BRFV)
Purpose : let the tests run the whole pipeline and check that it recovers a
          coefficient that was planted on purpose.

EVERY VALUE WRITTEN BY THIS SCRIPT IS SYNTHETIC. Nothing it produces may be
used for a table, a figure or a sentence in the manuscript. The fixture is
written to a folder chosen by the caller (the tests use a temporary folder)
and never into the project's own 01_data.

It copies the quirks of the real score file: Windows line ends, rows without a
score, an all-zero year 2000, eight-character CUSIPs in 2024, CUSIPs with
leading zeros and the tickers "NA" and "TRUE".
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

BETA_COUNT = -0.25          # planted effect of the lagged count score on Tobin's Q
GICS_NON_FINANCIAL = ["1010", "1510", "2010", "2020", "2030", "2510", "2520", "2530", "2550", "3010",
                      "3020", "3030", "3510", "3520", "4510", "4520", "4530", "5010", "5020", "5510"]
GICS_FINANCIAL = ["4010", "4020", "4030", "6010"]
GICS_EXPOSED = {"1010", "1510", "3020", "3520"}
EXTRACT_FIRST, EXTRACT_LAST = 2012, 2024


def _ticker(index: int) -> str:
    letters = ""
    index += 26 * 26
    while index:
        index, remainder = divmod(index, 26)
        letters = chr(65 + remainder) + letters
    return "S" + letters


def build_fixture(root: Path, seed: int = 20261118, convention: str = "fiscal", n_firms: int = 700) -> dict:
    """Write a complete synthetic project under root and return what the tests need to know."""
    rng = np.random.default_rng(seed)
    giglio = root / "01_data" / "raw" / "giglio"
    compustat_dir = root / "01_data" / "raw" / "compustat"
    climate_dir = root / "01_data" / "raw" / "climate"
    for folder in (giglio, compustat_dir, climate_dir):
        folder.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------ industry files
    all_gics = GICS_NON_FINANCIAL + GICS_FINANCIAL
    transition = {g: round(float(rng.uniform(0.03, 0.30)), 7) for g in all_gics}
    physical = {g: round(float(rng.uniform(0.02, 0.30)), 7) for g in all_gics}
    for g in GICS_EXPOSED:
        transition[g] += 0.3
        physical[g] += 0.3
    survey = pd.DataFrame({"transition": transition, "physical": physical})
    survey["average"] = (survey["transition"] + survey["physical"]) / 2
    survey["gics4"] = survey.index
    survey.to_csv(giglio / "survey_biodiversity_scores.csv", index=False, lineterminator="\r\n")
    for name in ("holding_biodiversity_scores.csv", "cdp_biodiversity_scores.csv"):
        pd.DataFrame({"gics4": all_gics, "score": rng.uniform(-1, 1, len(all_gics)).round(6)}).to_csv(
            giglio / name, index=False, lineterminator="\r\n")
    (giglio / "Biodiversity Data Codebook.pdf").write_bytes(b"%PDF-1.4 synthetic placeholder for tests\n")

    # ---------------------------------------------------------- firms
    industry_year = {(g, y): float(rng.normal(0, 0.15)) for g in all_gics for y in range(EXTRACT_FIRST, EXTRACT_LAST + 1)}
    score_rows, compustat_rows, climate_rows, truth_rows = [], [], [], []
    used_cusips: set[str] = set()
    for i in range(n_firms):
        gvkey = f"{1000 + i:06d}"
        ticker = "NA" if i == 0 else "TRUE" if i == 1 else _ticker(i)
        financial = rng.random() < 0.08
        gics = str(rng.choice(GICS_FINANCIAL if financial else GICS_NON_FINANCIAL))
        sic = int(rng.integers(6000, 7000)) if financial else int(rng.integers(2000, 6000))
        while True:
            cusip = f"{int(rng.integers(0, 10**6)):06d}{chr(65 + int(rng.integers(0, 26)))}{int(rng.integers(0, 10))}1"
            if cusip[:8] not in used_cusips:
                used_cusips.add(cusip[:8])
                break
        start, end = EXTRACT_FIRST, EXTRACT_LAST
        kind = rng.random()
        if kind < 0.15:
            start = int(rng.integers(2016, 2022))
        elif kind < 0.27:
            end = int(rng.integers(2016, 2022))
        fye_month = 12 if rng.random() < 0.8 else int(rng.choice([3, 6, 9]))
        fic = "USA" if rng.random() < 0.95 else "CAN"
        firm_effect = float(rng.normal(0, 0.25))
        reports_rd = rng.random() < 0.6
        pays_dividend = rng.random() < 0.4

        # 10-K scores by fiscal year. Established firms have a history before the extract.
        history_start = 2005 if start == EXTRACT_FIRST else start
        p_enter = 0.012 * (4 if gics in GICS_EXPOSED else 1)
        count_by_year: dict[int, int] = {}
        state = int(rng.random() < p_enter / (p_enter + 0.18))
        for year in range(history_start, end + 1):
            state = int(rng.random() < (0.82 if state else p_enter))
            count_by_year[year] = state
            regulation = int(state and rng.random() < 0.75)
            negative = int(rng.choice([-1, 0, 0, 0, 1, 1, 2, 3])) if state else int(rng.choice([0] * 97 + [1, 1, -1]))
            label = year if convention == "fiscal" else year + 1
            if label > 2024:
                continue
            cusip_text = cusip[:8] if label == 2024 else cusip
            score_rows.append((ticker, label, cusip_text, str(state), str(negative), str(regulation)))
        if start == EXTRACT_FIRST and i % 20 == 0:
            score_rows.append((ticker, 2000, cusip, "0", "0", "0"))

        # Compustat rows, with one or two unpriced years before a new listing.
        assets = float(np.exp(rng.normal(6.5, 1.5)))
        sales = assets * float(rng.uniform(0.5, 1.2))
        first_row_year = start - (2 if start > EXTRACT_FIRST else 0)
        for year in range(first_row_year, end + 1):
            assets *= 1 + float(rng.normal(0.05, 0.08))
            sales *= 1 + float(rng.normal(0.06, 0.15))
            assets, sales = max(assets, 5.0), max(sales, 1.0)
            book_equity = assets * float(rng.uniform(0.40, 0.60))
            roa = float(rng.normal(0.10, 0.08))
            lagged_count = count_by_year.get(year - 1, 0)
            q_true = (1.7 + industry_year.get((gics, year), 0.0) + firm_effect + BETA_COUNT * lagged_count
                      + 1.5 * roa + float(rng.normal(0, 0.35)))
            q_true = max(q_true, 0.7)
            market_value = assets * (q_true - 1) + book_equity
            shares = assets / 25
            priced = year >= start
            datadate = f"{year + (1 if fye_month <= 5 else 0)}{fye_month:02d}28"
            compustat_rows.append({
                "gvkey": gvkey, "datadate": datadate, "fyear": year, "fyr": fye_month, "indfmt": "INDL",
                "consol": "C", "popsrc": "D", "datafmt": "STD", "tic": ticker, "cusip": cusip,
                "conm": f"SYNTHETIC FIRM {i}", "curcd": "USD", "at": round(assets, 3), "ceq": round(book_equity, 3),
                "csho": round(shares, 4), "prcc_f": round(market_value / shares, 4) if priced else "",
                "dltt": round(assets * float(rng.uniform(0.05, 0.35)), 3),
                "dlc": round(assets * float(rng.uniform(0.0, 0.05)), 3) if rng.random() < 0.9 else "",
                "oibdp": round(roa * assets, 3), "ppent": round(assets * float(rng.uniform(0.05, 0.6)), 3),
                "sale": round(sales, 3), "xrd": round(assets * float(rng.uniform(0, 0.1)), 3) if reports_rd else "",
                "capx": round(assets * float(rng.uniform(0.01, 0.1)), 3), "che": round(assets * float(rng.uniform(0.02, 0.3)), 3),
                "dvc": round(assets * 0.01, 3) if pays_dividend else 0, "sich": sic, "sic": sic, "ggroup": gics,
                "gsector": gics[:2], "fic": fic,
            })
            if priced and rng.random() < 0.8:
                climate_rows.append({"gvkey": gvkey, "year": year, "cc_expo_ew": round(float(abs(rng.normal(0.001, 0.001))), 6)})
            if priced:
                truth_rows.append({"id_gvkey": gvkey, "t_fyear": year, "count_lag_true": lagged_count,
                                   "has_score_row": (year - 1) in count_by_year, "q_true": q_true})

    # Rows without a score, as in the real file: no CUSIP, no count, no regulation.
    no_score = [(f"ZNOSC{k}", year, "", "", "0", "") for k in range(6) for year in range(2001, 2006)]
    score_rows += no_score
    scores = pd.DataFrame(score_rows, columns=["ticker", "year", "cusip", "count", "negative", "regulation"])
    scores = scores.sort_values(["ticker", "year"])
    scores.to_csv(giglio / "10k_biodiversity_scores_2024.csv", index=False, lineterminator="\r\n")

    compustat = pd.DataFrame(compustat_rows)
    format_noise = compustat.sample(20, random_state=1).assign(indfmt="FS")
    duplicates = compustat.loc[compustat["fyear"] == 2018].sample(3, random_state=2).copy()
    duplicates["datadate"] = duplicates["datadate"].str.slice(0, 4) + "0131"
    compustat = pd.concat([compustat, format_noise, duplicates], ignore_index=True)
    compustat.to_csv(compustat_dir / "BRFV_compustat_funda_raw.csv", index=False)
    pd.DataFrame(climate_rows).to_csv(climate_dir / "BRFV_climate_exposure_raw.csv", index=False)

    return {
        "beta_count": BETA_COUNT,
        "n_score_rows_raw": len(scores),
        "n_no_score_rows": len(no_score),
        "n_year_2000_rows": int((scores["year"] == 2000).sum()),
        "truth": pd.DataFrame(truth_rows),
        "raw_compustat": compustat,
    }


if __name__ == "__main__":
    import sys
    import tempfile

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.mkdtemp(prefix="brfv_fixture_"))
    info = build_fixture(target)
    print(f"SYNTHETIC fixture written to {target} ({info['n_score_rows_raw']:,} score rows)")
