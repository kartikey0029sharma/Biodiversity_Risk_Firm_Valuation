"""BRFV step 04: merge scores and financials into the firm-year analysis panel.

Project : Biodiversity Risk Disclosure and Firm Valuation (BRFV)
Input   : 01_data/interim/BRFV_scores_firmyear_clean.csv
          01_data/interim/BRFV_compustat_firmyear_clean.csv
          01_data/interim/BRFV_industry_exposure_gics4.csv
          01_data/raw/climate/BRFV_climate_exposure_raw.csv   (optional)
Output  : 01_data/processed/BRFV_panel_firmyear_analysis.csv
          03_output/tables/BRFV_T03_year_alignment_test.(csv|md)
          03_output/tables/BRFV_T04_sample_attrition.(csv|md)

Timing  : the score attached to fiscal year t is the latest one that was public
          before Tobin's Q is measured. Under the "fiscal" convention this is
          the score labelled t-1; under "filing" it is the score labelled t.
          The convention is set in brfv_00_config.py and tested here.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

import brfv_00_config as cfg
import brfv_utils as u

log = u.get_logger("brfv_04_build_panel")

SCORE_COLUMNS = ["bd_count", "bd_negative", "bd_regulation", "bd_negative_pos"]
BASE_SCORES = ["bd_count", "bd_negative", "bd_regulation"]
COMPUSTAT_TEXT = ["id_gvkey", "id_cusip8", "id_ticker", "id_conm", "t_datadate", "geo_fic", "fin_curcd", "ind_gics4"]
SCORE_TEXT = ["id_ticker", "id_cusip8", "cusip_raw"]


# ------------------------------------------------------------- alignment
def year_alignment_test(compustat: pd.DataFrame, scores: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Infer what the score file's year means from firms that enter or leave.

    Only December year-end firms are used, so that fiscal and calendar years
    coincide. Two one-sided signals:
      entry: first score year equal to the first fiscal year with a share price
             can only happen if the score year is the fiscal year of the 10-K;
      exit : last score year one above the last fiscal year in Compustat can
             only happen if the score year is the filing year.
    """
    december = compustat.loc[(compustat["t_fye_month"] == 12) & (compustat["fin_mve"] > 0) & (compustat["id_cusip8"] != "")]
    extract_first, extract_last = int(compustat["t_fyear"].min()), int(compustat["t_fyear"].max())
    firm_span = december.groupby("id_gvkey").agg(first_fyear=("t_fyear", "min"), last_fyear=("t_fyear", "max"),
                                                 id_cusip8=("id_cusip8", "last"))
    score_span = scores.loc[scores["id_cusip8"] != ""].groupby("id_cusip8")["t_score_year"].agg(
        first_score_year="min", last_score_year="max").reset_index()
    both = firm_span.reset_index().merge(score_span, on="id_cusip8", how="inner")

    entrants = both.loc[(both["first_fyear"] >= extract_first + 2) & (both["first_score_year"] > cfg.SCORE_YEAR_MIN)]
    entry_gap = (entrants["first_score_year"] - entrants["first_fyear"]).value_counts()
    leavers = both.loc[(both["last_fyear"] <= extract_last - 2) & (both["last_score_year"] < cfg.SCORE_YEAR_MAX_MAIN)]
    exit_gap = (leavers["last_score_year"] - leavers["last_fyear"]).value_counts()

    entry0, entry1 = int(entry_gap.get(0, 0)), int(entry_gap.get(1, 0))
    exit0, exit1 = int(exit_gap.get(0, 0)), int(exit_gap.get(1, 0))
    share_entry0 = entry0 / (entry0 + entry1) if (entry0 + entry1) else np.nan
    share_exit1 = exit1 / (exit0 + exit1) if (exit0 + exit1) else np.nan
    enough = (entry0 + entry1) >= cfg.ALIGNMENT_MIN_FIRMS and (exit0 + exit1) >= cfg.ALIGNMENT_MIN_FIRMS
    if not enough:
        verdict = "undetermined"
    elif share_entry0 >= 0.5 and share_exit1 <= 0.2:
        verdict = "fiscal"
    elif share_exit1 >= 0.5 and share_entry0 <= 0.2:
        verdict = "filing"
    else:
        verdict = "undetermined"
    basis = "entry and exit years"
    # Second look, used only when the first is not conclusive. A row with no filing behind it has
    # all scores at zero. If the year is the fiscal year, the empty row is the one after the last
    # fiscal year. If the year is the filing year, the empty row is the first one.
    lookup = scores.loc[scores["id_cusip8"] != ""].set_index(["id_cusip8", "t_score_year"])[BASE_SCORES]

    def filled(frame: pd.DataFrame, year_column: str, shift: int = 0) -> tuple[int, int]:
        index = pd.MultiIndex.from_arrays([frame["id_cusip8"], frame[year_column] + shift])
        rows = lookup.reindex(index)
        present = rows["bd_count"].notna()
        return int(present.sum()), int(((rows.fillna(0) != 0).any(axis=1) & present).sum())

    first_rows = entrants.loc[(entrants["first_score_year"] - entrants["first_fyear"]) == 0]
    trailing = leavers.loc[(leavers["last_score_year"] - leavers["last_fyear"]) == 1]
    n_first, filled_first = filled(first_rows, "first_score_year")
    n_first_next, filled_first_next = filled(first_rows, "first_score_year", 1)
    n_trailing, filled_trailing = filled(trailing, "last_score_year")
    n_trailing_before, filled_trailing_before = filled(trailing, "last_score_year", -1)
    if verdict == "undetermined" and min(n_first, n_trailing) >= cfg.ALIGNMENT_MIN_FIRMS:
        share_first, share_trailing = filled_first / n_first, filled_trailing / n_trailing
        if share_trailing <= cfg.ALIGNMENT_EMPTY_SHARE and share_first >= cfg.ALIGNMENT_FILLED_SHARE:
            verdict, basis = "fiscal", "the rows after the last fiscal year are empty"
        elif share_first <= cfg.ALIGNMENT_EMPTY_SHARE and share_trailing >= cfg.ALIGNMENT_FILLED_SHARE:
            verdict, basis = "filing", "the rows of the first fiscal year are empty"
    table = pd.DataFrame([
        {"signal": "entry: first score year minus first priced fiscal year = 0", "n_firms": entry0},
        {"signal": "entry: first score year minus first priced fiscal year = 1", "n_firms": entry1},
        {"signal": "exit: last score year minus last fiscal year = 0", "n_firms": exit0},
        {"signal": "exit: last score year minus last fiscal year = 1", "n_firms": exit1},
        {"signal": "first row in the first priced fiscal year: rows", "n_firms": n_first},
        {"signal": "first row in the first priced fiscal year: rows with a score other than zero", "n_firms": filled_first},
        {"signal": "the same firms one year later: rows", "n_firms": n_first_next},
        {"signal": "the same firms one year later: rows with a score other than zero", "n_firms": filled_first_next},
        {"signal": "row one year after the last priced fiscal year: rows", "n_firms": n_trailing},
        {"signal": "row one year after the last priced fiscal year: rows with a score other than zero", "n_firms": filled_trailing},
        {"signal": "the same firms one year earlier: rows", "n_firms": n_trailing_before},
        {"signal": "the same firms one year earlier: rows with a score other than zero", "n_firms": filled_trailing_before},
        {"signal": f"verdict: {verdict} (basis: {basis}); configured: {cfg.SCORE_YEAR_CONVENTION}", "n_firms": entry0 + entry1 + exit0 + exit1},
    ])
    return table, verdict


# ------------------------------------------------------------------ merge
def attach_scores(compustat: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    """Attach the pre-determined score to each Compustat firm-year.

    First on the eight-character CUSIP and score year, then on ticker and score
    year for rows still unmatched. A score row is never used twice.
    """
    frame = compustat.copy()
    lag = 1 if cfg.SCORE_YEAR_CONVENTION == "fiscal" else 0
    frame["t_score_year"] = frame["t_fyear"] - lag

    by_cusip = scores.loc[scores["id_cusip8"] != "", ["id_cusip8", "t_score_year", "id_ticker"] + SCORE_COLUMNS]
    by_cusip = by_cusip.rename(columns={"id_ticker": "score_ticker"})
    merged = frame.merge(by_cusip, on=["id_cusip8", "t_score_year"], how="left", validate="many_to_one")
    matched = merged["bd_count"].notna()
    # Two Compustat firms sharing one CUSIP in a year would both take the score: keep the first only.
    shared = matched & merged.duplicated(["id_cusip8", "t_score_year"], keep="first")
    if shared.any():
        log.warning("%d firm-years share a CUSIP and year with another firm; their match is removed", int(shared.sum()))
        merged.loc[shared, SCORE_COLUMNS + ["score_ticker"]] = np.nan
        matched = merged["bd_count"].notna()
    merged["mrg_source"] = np.where(matched, "cusip8", "none")

    used = merged.loc[matched, ["score_ticker", "t_score_year"]].rename(columns={"score_ticker": "id_ticker"})
    used = used.assign(used=1).drop_duplicates()
    free = scores.merge(used, on=["id_ticker", "t_score_year"], how="left")
    free = free.loc[free["used"].isna(), ["id_ticker", "t_score_year"] + SCORE_COLUMNS]
    open_rows = merged.loc[~matched].drop(columns=SCORE_COLUMNS + ["score_ticker"])
    by_ticker = open_rows.merge(free, on=["id_ticker", "t_score_year"], how="left", validate="many_to_one")
    hit = by_ticker["bd_count"].notna() & ~by_ticker.duplicated(["id_ticker", "t_score_year"], keep="first")
    by_ticker.loc[~hit, SCORE_COLUMNS] = np.nan
    by_ticker["mrg_source"] = np.where(hit, "ticker", "none")

    result = pd.concat([merged.loc[matched].drop(columns=["score_ticker"]), by_ticker], ignore_index=True)
    result = result.rename(columns={c: c + "_lag" for c in SCORE_COLUMNS})
    u.assert_unique(result, ["id_gvkey", "t_fyear"], "panel after the score merge")
    return result.sort_values(["id_gvkey", "t_fyear"]).reset_index(drop=True)


def attach_other_timing(panel: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    """Scores under the other reading of the score year, for robustness check R10.

    With the fiscal setting the main regressor is the score of year t-1. The other
    reading (filing year) would make the score of year t the latest filing, so that
    row is attached here with the suffix _alt, through the same identifier that gave
    the main match. Score years after SCORE_YEAR_MAX_MAIN are left out.
    """
    step = 1 if cfg.SCORE_YEAR_CONVENTION == "fiscal" else -1
    out = panel.copy()
    out["t_score_year_alt"] = out["t_score_year"] + step
    by_cusip = scores.loc[scores["id_cusip8"] != "", ["id_cusip8", "t_score_year"] + BASE_SCORES].rename(
        columns={"t_score_year": "t_score_year_alt", **{c: c + "_alt" for c in BASE_SCORES}})
    by_ticker = scores[["id_ticker", "t_score_year"] + BASE_SCORES].rename(
        columns={"t_score_year": "t_score_year_alt", **{c: c + "_alt_ticker" for c in BASE_SCORES}})
    out = out.merge(by_cusip, on=["id_cusip8", "t_score_year_alt"], how="left", validate="many_to_one")
    out = out.merge(by_ticker, on=["id_ticker", "t_score_year_alt"], how="left", validate="many_to_one")
    outside = ~out["t_score_year_alt"].between(cfg.SCORE_YEAR_MIN, cfg.SCORE_YEAR_MAX_MAIN) | (out["mrg_source"] == "none")
    for column in BASE_SCORES:
        value = np.where(out["mrg_source"] == "ticker", out[column + "_alt_ticker"], out[column + "_alt"])
        out[column + "_alt"] = pd.Series(value, index=out.index, dtype=float).mask(outside)
    out = out.drop(columns=[c + "_alt_ticker" for c in BASE_SCORES])
    u.assert_unique(out, ["id_gvkey", "t_fyear"], "panel after the other-timing merge")
    return out


def attach_climate(panel: pd.DataFrame) -> pd.DataFrame:
    """Optional: firm-level climate exposure for the same year as the score."""
    if not cfg.RAW_CLIMATE.exists():
        log.info("no climate file: the climate control is left out")
        return panel
    names = cfg.CLIMATE_COLUMNS
    raw = u.read_csv_as_text(cfg.RAW_CLIMATE)
    raw.columns = [c.strip().lower() for c in raw.columns]
    missing = [v for v in names.values() if v not in raw.columns]
    if missing:
        raise ValueError(f"climate file lacks columns {missing}; edit CLIMATE_COLUMNS in brfv_00_config.py")
    climate = pd.DataFrame({
        "id_gvkey": raw[names["firm"]].str.strip().str.replace(r"\.0$", "", regex=True).str.zfill(6),
        "t_score_year": u.to_number(raw[names["year"]]),
        cfg.CLIMATE_VAR: u.to_number(raw[names["exposure"]]),
    }).dropna(subset=["t_score_year"])
    climate["t_score_year"] = climate["t_score_year"].astype(int)
    climate = climate.groupby(["id_gvkey", "t_score_year"], as_index=False)[cfg.CLIMATE_VAR].mean()
    out = panel.merge(climate, on=["id_gvkey", "t_score_year"], how="left", validate="many_to_one")
    log.info("climate exposure attached to %.1f%% of firm-years", 100 * out[cfg.CLIMATE_VAR].notna().mean())
    return out


# ----------------------------------------------------------------- sample
def build_sample(merged: pd.DataFrame, industry: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apply the sample filters in a fixed order and record the attrition."""
    attrition = u.Attrition("id_gvkey")
    panel = merged.loc[merged["t_fyear"].between(cfg.Q_FYEAR_MIN, cfg.Q_FYEAR_MAX)].copy()
    attrition.add(f"Compustat firm-years, fiscal years {cfg.Q_FYEAR_MIN}-{cfg.Q_FYEAR_MAX}", panel)
    if (panel["geo_fic"] != "").any():
        panel = panel.loc[panel["geo_fic"] == "USA"]
        attrition.add("incorporated in the United States", panel)
    if (panel["fin_curcd"] != "").any():
        panel = panel.loc[panel["fin_curcd"] == "USD"]
        attrition.add("reporting in US dollars", panel)
    panel = panel.loc[panel["ind_sic"].notna() & ~panel["ind_sic"].between(*cfg.SIC_FINANCIAL)]
    attrition.add("non-financial (SIC outside 6000-6999)", panel)
    panel = panel.loc[(panel["fin_at"] > 0) & (panel["fin_mve"] > 0) & panel["fin_ceq"].notna() & (panel["dv_tobin_q"] > 0)]
    attrition.add("total assets, book equity and market value available", panel)
    panel = panel.loc[panel["ind_gics4"] != ""]
    attrition.add("GICS industry group available", panel)
    panel = panel.loc[panel["mrg_source"] != "none"]
    attrition.add("matched to a 10-K biodiversity score", panel)
    panel = panel.dropna(subset=cfg.CONTROLS_RAW)
    attrition.add("all control variables available", panel)
    panel = panel.copy()

    panel = panel.merge(industry.drop(columns=["ind_is_financial"]), on="ind_gics4", how="left", validate="many_to_one")
    panel["ev_post"] = (panel["t_fyear"] >= cfg.EVENT_FIRST_FYEAR).astype(int)
    for column in cfg.CONTINUOUS_TO_WINSORISE:
        panel[column + "_w"] = u.winsorise(panel[column])
    median = panel.groupby(["ind_gics4", "t_fyear"])["dv_tobin_q_w"].transform("median")
    panel[cfg.DV_INDADJ] = panel["dv_tobin_q_w"] - median
    panel[cfg.FE_IND_YEAR] = panel["ind_gics4"] + "_" + panel["t_fyear"].astype(str)
    for score in cfg.SCORES:
        short = score.replace("bd_", "").replace("_lag", "")
        panel[f"ix_{short}_high"] = panel[score] * panel["ind_bio_high"]
        panel[f"ix_{short}_post"] = panel[score] * panel["ev_post"]
    return panel.sort_values(["id_gvkey", "t_fyear"]).reset_index(drop=True), attrition.table()


def check_panel(panel: pd.DataFrame) -> None:
    """Final checks before the panel is written."""
    u.assert_unique(panel, ["id_gvkey", "t_fyear"], "analysis panel")
    numeric = panel.select_dtypes(include=[np.number])
    if np.isinf(numeric.to_numpy(dtype=float)).any():
        raise ValueError("infinite values in the analysis panel")
    if not set(panel["bd_count_lag"].dropna().unique()) <= {0, 1}:
        raise ValueError("bd_count_lag is not binary")
    if panel[[cfg.DV_MAIN] + cfg.CONTROLS].isna().any().any():
        raise ValueError("missing values in the dependent variable or the controls")


# ------------------------------------------------------------------- main
def main() -> int:
    u.ensure_dirs()
    for needed in (cfg.INT_SCORES, cfg.INT_COMPUSTAT, cfg.INT_INDUSTRY):
        if not needed.exists():
            log.error("input missing: %s. Run the earlier steps first.", needed.name)
            return 2
    scores = u.read_pipeline_csv(cfg.INT_SCORES, SCORE_TEXT)
    scores["t_score_year"] = scores["t_score_year"].astype(int)
    compustat = u.read_pipeline_csv(cfg.INT_COMPUSTAT, COMPUSTAT_TEXT)
    compustat["t_fyear"] = compustat["t_fyear"].astype(int)
    industry = u.read_pipeline_csv(cfg.INT_INDUSTRY, ["ind_gics4"])
    main_scores = scores.loc[scores["t_score_year"] <= cfg.SCORE_YEAR_MAX_ALL]

    alignment, verdict = year_alignment_test(compustat, main_scores)
    u.write_table(alignment, "BRFV_T03_year_alignment_test",
                  note="December year-end firms only. The first four rows count firms by the gap between score years and "
                       "priced fiscal years. The next eight rows count how many boundary rows carry any score: a row with "
                       "no filing behind it has all scores at zero. See the docstring of brfv_04_build_panel.py.")
    log.info("year alignment verdict: %s (configured: %s)", verdict, cfg.SCORE_YEAR_CONVENTION)
    if verdict not in ("undetermined", cfg.SCORE_YEAR_CONVENTION):
        message = (f"the data point to the '{verdict}' convention but brfv_00_config.py says "
                   f"'{cfg.SCORE_YEAR_CONVENTION}'. Change SCORE_YEAR_CONVENTION, or set "
                   "BRFV_ALLOW_ALIGNMENT_MISMATCH=1 to continue on purpose.")
        if os.environ.get("BRFV_ALLOW_ALIGNMENT_MISMATCH") != "1":
            log.error(message)
            return 3
        log.warning(message)
    elif verdict == "undetermined":
        log.warning("the year convention could not be confirmed from the data; check a few firms by hand")

    merged = attach_scores(compustat, main_scores)
    merged = attach_other_timing(merged, main_scores)
    in_window = merged["t_fyear"].between(cfg.Q_FYEAR_MIN, cfg.Q_FYEAR_MAX)
    rates = merged.loc[in_window, "mrg_source"].value_counts(normalize=True).mul(100).round(2)
    log.info("match rate in the sample window | %s", ", ".join(f"{k}: {v}%" for k, v in rates.items()))
    used_scores = main_scores.loc[main_scores["t_score_year"].between(cfg.Q_FYEAR_MIN - 1, cfg.Q_FYEAR_MAX)]
    log.info("score rows in the matching years: %s", f"{len(used_scores):,}")

    merged = attach_climate(merged)
    panel, attrition = build_sample(merged, industry)
    check_panel(panel)
    u.write_table(attrition, "BRFV_T04_sample_attrition",
                  note="Each row applies one more filter to the rows that survived the row above.")
    panel.to_csv(cfg.PROC_PANEL, index=False)
    log.info("panel written: %s firm-years, %s firms, %.2f%% with Count = 1", f"{len(panel):,}",
             f"{panel['id_gvkey'].nunique():,}", 100 * panel["bd_count_lag"].mean())
    switchers = panel.groupby("id_gvkey")["bd_count_lag"].agg(["min", "max"])
    log.info("firms whose Count score changes inside the panel: %s", f"{int((switchers['min'] != switchers['max']).sum()):,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
