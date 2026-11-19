"""BRFV step 07: robustness checks for the three biodiversity scores.

Project : Biodiversity Risk Disclosure and Firm Valuation (BRFV)
Input   : 01_data/processed/BRFV_panel_firmyear_analysis.csv
Output  : 03_output/tables/BRFV_T13_robustness.(csv|md)
Checks  : R1 log of Tobin's Q
          R2 industry-adjusted Tobin's Q with year fixed effects
          R3 utilities excluded (GICS 5510)
          R4 fiscal year 2020 excluded
          R5 December fiscal year ends only
          R6 firm-years matched on CUSIP only
          R7 firms that discuss biodiversity at least once, firm and year effects
          R8 standard errors clustered by industry group
          R9 placebo: the score disclosed two fiscal years later, added to the model
             that already holds the three lagged scores
          R10 other timing: the score of the next score year, which would be the latest
             filing if the year in the score file were the filing year
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import brfv_00_config as cfg
import brfv_utils as u
from brfv_05_descriptives import load_panel
from brfv_06_estimate import FE_FIRM_YEAR, FE_INDUSTRY_YEAR, fit_model

log = u.get_logger("brfv_07_robustness")


def add_future_scores(panel: pd.DataFrame) -> pd.DataFrame:
    """Score that the same firm discloses two fiscal years later (placebo regressor)."""
    out = panel.sort_values([cfg.ID_FIRM, cfg.T_FYEAR]).copy()
    future_year = out.groupby(cfg.ID_FIRM)[cfg.T_FYEAR].shift(-2)
    valid = (future_year - out[cfg.T_FYEAR]) == 2
    for score in cfg.SCORES:
        future = out.groupby(cfg.ID_FIRM)[score].shift(-2)
        out[score.replace("_lag", "_lead")] = future.where(valid)
    return out


def variants(panel: pd.DataFrame) -> list[dict]:
    ever = panel.groupby(cfg.ID_FIRM)["bd_count_lag"].transform("max") == 1
    return [
        {"check": "R1 log Tobin's Q", "data": panel, "dep": cfg.DV_LOG, "fe": FE_INDUSTRY_YEAR},
        {"check": "R2 industry-adjusted Q, year effects", "data": panel, "dep": cfg.DV_INDADJ, "fe": cfg.T_FYEAR},
        {"check": "R3 utilities excluded", "data": panel.loc[panel["ind_gics4"] != "5510"], "dep": cfg.DV_MAIN, "fe": FE_INDUSTRY_YEAR},
        {"check": "R4 fiscal year 2020 excluded", "data": panel.loc[panel[cfg.T_FYEAR] != 2020], "dep": cfg.DV_MAIN, "fe": FE_INDUSTRY_YEAR},
        {"check": "R5 December year ends only", "data": panel.loc[panel["t_fye_month"] == 12], "dep": cfg.DV_MAIN, "fe": FE_INDUSTRY_YEAR},
        {"check": "R6 CUSIP matches only", "data": panel.loc[panel["mrg_source"] == "cusip8"], "dep": cfg.DV_MAIN, "fe": FE_INDUSTRY_YEAR},
        {"check": "R7 ever-disclosing firms, firm and year effects", "data": panel.loc[ever], "dep": cfg.DV_MAIN, "fe": FE_FIRM_YEAR},
        {"check": "R8 clustered by industry group", "data": panel, "dep": cfg.DV_MAIN, "fe": FE_INDUSTRY_YEAR, "cluster": "ind_gics4"},
    ]


def main() -> int:
    u.ensure_dirs()
    if not cfg.PROC_PANEL.exists():
        log.error("panel missing: %s. Run step 04 first.", cfg.PROC_PANEL.name)
        return 2
    panel = add_future_scores(load_panel())
    rows = []
    for variant in variants(panel):
        for score in cfg.SCORES:
            data = variant["data"]
            if len(data) < 50 or data[score].nunique() < 2:
                log.warning("%s skipped for %s: too little variation", variant["check"], score)
                continue
            tidy = fit_model(data, variant["check"], variant["dep"], [score] + cfg.CONTROLS, variant["fe"],
                             cluster=variant.get("cluster", cfg.CLUSTER))
            rows.append(tidy.loc[tidy["term"] == score])
    for score in cfg.SCORES:
        lead = score.replace("_lag", "_lead")
        if panel[lead].notna().sum() >= 50 and panel[lead].nunique() > 1:
            tidy = fit_model(panel, "R9 placebo: score two years ahead", cfg.DV_MAIN, [lead] + cfg.SCORES + cfg.CONTROLS, FE_INDUSTRY_YEAR)
            rows.append(tidy.loc[tidy["term"] == lead])
    for score in cfg.SCORES:
        other = score.replace("_lag", "_alt")
        if other in panel.columns and panel[other].notna().sum() >= 50 and panel[other].nunique() > 1:
            tidy = fit_model(panel, "R10 other timing: score of the next score year", cfg.DV_MAIN, [other] + cfg.CONTROLS, FE_INDUSTRY_YEAR)
            rows.append(tidy.loc[tidy["term"] == other])
    table = pd.concat(rows, ignore_index=True)
    table = table.rename(columns={"model": "check"})[["check", "term", "coef", "se", "p", "n_obs", "n_firms",
                                                     "dep_var", "fixed_effects", "cluster"]]
    table["stars"] = table["p"].map(u.stars)
    table[["coef", "se", "p"]] = table[["coef", "se", "p"]].astype(float).round(4)
    u.write_table(table, "BRFV_T13_robustness",
                  note="Each row is one regression with the full set of controls; only the coefficient on the score is shown. "
                       "In R9 the reported term is the future score, which should not explain today's valuation. "
                       "R10 uses the score of the next score year in place of the lagged score.")
    log.info("robustness table written: %d regressions", len(table))
    return 0


if __name__ == "__main__":
    sys.exit(main())
