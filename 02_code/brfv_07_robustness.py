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
Added   : 23 November 2026, after the first results and after a review of the draft.
          The checks R1 to R10 are aimed at the comparison across firms. Two results
          of the paper come from other models, so the main checks are repeated on them.
          They are reported for information and decide no hypothesis.
          03_output/tables/BRFV_T15_tone_within_firms_checks.(csv|md)
            W0 to W10: the coefficient on Negative with firm and year effects, once
            with the three scores together (the model that the reading rule names)
            and once alone. W2 replaces the year effects with industry group by year
            effects. W9 adds the Negative score that the firm reports two years later.
            W10 uses the score of the next score year.
          03_output/tables/BRFV_T16_regulation_after_2021_checks.(csv|md)
            P0 to P9: Regulation and its interaction with the period from fiscal year
            2022, with industry group by year effects, and the slope in that period.
            P8 uses the score of the next score year. P9 enters the three scores and
            their three interactions together.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import brfv_00_config as cfg
import brfv_utils as u
from brfv_05_descriptives import load_panel
from brfv_06_estimate import (FE_FIRM_INDUSTRY_YEAR, FE_FIRM_YEAR, FE_INDUSTRY_YEAR, SHORT, SLOPE_POST,
                             fit_model, fit_with_later_slope)

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


NEGATIVE, REGULATION = "bd_negative_lag", "bd_regulation_lag"
KEEP = ["check", "version", "role", "term", "coef", "se", "p", "n_obs", "n_firms", "dep_var", "fixed_effects", "cluster"]


def sample_variants(panel: pd.DataFrame, fixed_effects: str, letter: str) -> list[dict]:
    """The sample and specification checks of R1 and R3 to R8, for a model with the given fixed effects."""
    ever = panel.groupby(cfg.ID_FIRM)["bd_count_lag"].transform("max") == 1
    variants = [
        {"check": "log Tobin's Q", "data": panel, "dep": cfg.DV_LOG},
        {"check": "utilities excluded", "data": panel.loc[panel["ind_gics4"] != "5510"]},
        {"check": "fiscal year 2020 excluded", "data": panel.loc[panel[cfg.T_FYEAR] != 2020]},
        {"check": "December year ends only", "data": panel.loc[panel["t_fye_month"] == 12]},
        {"check": "CUSIP matches only", "data": panel.loc[panel["mrg_source"] == "cusip8"]},
        {"check": "ever-disclosing firms", "data": panel.loc[ever]},
        {"check": "clustered by industry group", "data": panel, "cluster": "ind_gics4"},
    ]
    if letter == "W":   # firm effects: compare each firm with its own industry group in the same year
        variants.insert(1, {"check": "firm effects and industry group by year effects", "data": panel, "fe": FE_FIRM_INDUSTRY_YEAR})
    else:               # industry group by year effects: the industry-adjusted Q of R2 instead
        variants.insert(1, {"check": "industry-adjusted Q, year effects", "data": panel, "dep": cfg.DV_INDADJ, "fe": cfg.T_FYEAR})
        variants = [v for v in variants if v["check"] != "ever-disclosing firms"]
    out = []
    for number, variant in enumerate(variants, start=1):
        out.append({"check": f"{letter}{number} {variant['check']}", "data": variant["data"],
                    "dep": variant.get("dep", cfg.DV_MAIN), "fe": variant.get("fe", fixed_effects),
                    "cluster": variant.get("cluster", cfg.CLUSTER)})
    return out


def pick(tidy: pd.DataFrame, term: str, version: str, role: str) -> pd.DataFrame:
    row = tidy.loc[tidy["term"] == term].copy()
    row["version"], row["role"] = version, role
    return row


def tone_within_firms(panel: pd.DataFrame) -> pd.DataFrame:
    """Family W: the coefficient on Negative with firm and year effects under the main checks."""
    main = {"check": "W0 main estimate", "data": panel, "dep": cfg.DV_MAIN, "fe": FE_FIRM_YEAR, "cluster": cfg.CLUSTER}
    variants = [main] + sample_variants(panel, FE_FIRM_YEAR, "W")
    rows = []
    for variant in variants:
        for version, scores in (("three scores", cfg.SCORES), ("alone", [NEGATIVE])):
            tidy = fit_model(variant["data"], variant["check"], variant["dep"], scores + cfg.CONTROLS, variant["fe"],
                             cluster=variant["cluster"])
            rows.append(pick(tidy, NEGATIVE, version, "negative"))
    lead = NEGATIVE.replace("_lag", "_lead")
    number = len(variants)
    for version, scores in (("three scores", cfg.SCORES), ("alone", [NEGATIVE])):
        tidy = fit_model(panel, f"W{number} lead: Negative two years ahead added", cfg.DV_MAIN, [lead] + scores + cfg.CONTROLS, FE_FIRM_YEAR)
        rows += [pick(tidy, lead, version, "lead"), pick(tidy, NEGATIVE, version, "negative")]
    other = [score.replace("_lag", "_alt") for score in cfg.SCORES]
    if all(column in panel.columns for column in other):
        for version, scores in (("three scores", other), ("alone", [NEGATIVE.replace("_lag", "_alt")])):
            tidy = fit_model(panel, f"W{number + 1} other timing: score of the next score year", cfg.DV_MAIN,
                             scores + cfg.CONTROLS, FE_FIRM_YEAR)
            rows.append(pick(tidy, NEGATIVE.replace("_lag", "_alt"), version, "negative"))
    return pd.concat(rows, ignore_index=True).rename(columns={"model": "check"})[KEEP]


def regulation_after_2021(panel: pd.DataFrame) -> pd.DataFrame:
    """Family P: Regulation, its interaction with the later period and the slope in that period."""
    interaction = f"ix_{SHORT[REGULATION]}_post"
    main = {"check": "P0 main estimate", "data": panel, "dep": cfg.DV_MAIN, "fe": FE_INDUSTRY_YEAR, "cluster": cfg.CLUSTER}
    variants = [main] + sample_variants(panel, FE_INDUSTRY_YEAR, "P")

    def three_rows(tidy: pd.DataFrame, score: str, product: str, slope: str, version: str) -> list[pd.DataFrame]:
        return [pick(tidy, score, version, "score"), pick(tidy, product, version, "interaction"),
                pick(tidy, slope, version, SLOPE_POST)]

    rows = []
    for variant in variants:
        tidy = fit_with_later_slope(variant["data"], variant["check"], variant["dep"], [(REGULATION, interaction)],
                                    cfg.CONTROLS, variant["fe"], cluster=variant["cluster"])
        rows += three_rows(tidy, REGULATION, interaction, SLOPE_POST, "one score")
    number = len(variants)
    other = REGULATION.replace("_lag", "_alt")
    if other in panel.columns:
        work = panel.copy()
        work["ix_regulation_alt_post"] = work[other] * work["ev_post"]
        tidy = fit_with_later_slope(work, f"P{number} other timing: score of the next score year", cfg.DV_MAIN,
                                    [(other, "ix_regulation_alt_post")], cfg.CONTROLS, FE_INDUSTRY_YEAR)
        rows += three_rows(tidy, other, "ix_regulation_alt_post", SLOPE_POST, "one score")
        number += 1
    pairs = [(score, f"ix_{SHORT[score]}_post") for score in cfg.SCORES]
    tidy = fit_with_later_slope(panel, f"P{number} three scores and their interactions together", cfg.DV_MAIN, pairs,
                                cfg.CONTROLS, FE_INDUSTRY_YEAR)
    rows += three_rows(tidy, REGULATION, interaction, f"{SLOPE_POST}_{SHORT[REGULATION]}", "three scores")
    return pd.concat(rows, ignore_index=True).rename(columns={"model": "check"})[KEEP]


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
    table[["coef", "se", "p"]] = table[["coef", "se", "p"]].astype(float)  # full precision; rounding is left to the reader of the file
    u.write_table(table, "BRFV_T13_robustness",
                  note="Each row is one regression with the full set of controls; only the coefficient on the score is shown. "
                       "In R9 the reported term is the future score, which should not explain today's valuation. "
                       "R10 uses the score of the next score year in place of the lagged score.")
    log.info("robustness table written: %d regressions", len(table))

    tone = tone_within_firms(panel)
    tone["stars"] = tone["p"].map(u.stars)
    u.write_table(tone, "BRFV_T15_tone_within_firms_checks",
                  note="Coefficient on the Negative score with firm fixed effects and the full set of controls. Version 'three scores' "
                       "enters Count, Negative and Regulation together, version 'alone' enters Negative only. In W9 the role 'lead' is "
                       "the Negative score that the firm reports two years later, added to the model. Added on 23 November 2026, "
                       "after the first results. These checks decide no hypothesis.")
    later = regulation_after_2021(panel)
    later["stars"] = later["p"].map(u.stars)
    u.write_table(later, "BRFV_T16_regulation_after_2021_checks",
                  note="Regulation score with industry group by year effects and the full set of controls. Role 'score' is the slope "
                       f"before fiscal year {cfg.EVENT_FIRST_FYEAR}, 'interaction' the change from that year, and '{SLOPE_POST}' their sum, "
                       "the slope in the later period. Added on 23 November 2026, after the first results. These checks decide no hypothesis.")
    log.info("checks on the two findings written: %d and %d rows", len(tone), len(later))
    return 0


if __name__ == "__main__":
    sys.exit(main())
