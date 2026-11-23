"""BRFV step 05: descriptive tables and figure for the analysis panel.

Project : Biodiversity Risk Disclosure and Firm Valuation (BRFV)
Input   : 01_data/processed/BRFV_panel_firmyear_analysis.csv
Output  : 03_output/tables/BRFV_T05_summary_statistics.(csv|md)
          03_output/tables/BRFV_T06_means_by_disclosure.(csv|md)
          03_output/tables/BRFV_T07_correlations.(csv|md)
          03_output/tables/BRFV_T08_industry_distribution.(csv|md)
          03_output/tables/BRFV_T14_identifying_variation.(csv|md)
          03_output/tables/BRFV_T17_score_correlations.(csv|md)
          03_output/figures/BRFV_F02_tobin_q_by_disclosure.png
Note    : the CSV files hold the values as computed. They are rounded once, where
          they are shown (four decimals in the Markdown copy, fewer in the draft),
          so a figure is never rounded twice.
"""
from __future__ import annotations

import math
import sys

import numpy as np
import pandas as pd

import brfv_00_config as cfg
import brfv_utils as u

log = u.get_logger("brfv_05_descriptives")

PANEL_TEXT = ["id_gvkey", "id_cusip8", "id_ticker", "id_conm", "t_datadate", "geo_fic", "fin_curcd",
              "ind_gics4", "mrg_source", cfg.FE_IND_YEAR]


def load_panel() -> pd.DataFrame:
    panel = u.read_pipeline_csv(cfg.PROC_PANEL, PANEL_TEXT)
    panel["t_fyear"] = panel["t_fyear"].astype(int)
    return panel


def variables(panel: pd.DataFrame) -> list[str]:
    extra = [c for c in ("ind_bio_survey_avg", "ind_bio_high", cfg.CLIMATE_VAR) if c in panel.columns]
    return [cfg.DV_MAIN, cfg.DV_LOG] + cfg.SCORES + cfg.CONTROLS + extra


def summary_statistics(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name in variables(panel):
        s = panel[name].dropna()
        rows.append({"variable": name, "n": len(s), "mean": s.mean(), "sd": s.std(), "min": s.min(),
                     "p25": s.quantile(0.25), "median": s.median(), "p75": s.quantile(0.75), "max": s.max()})
    return pd.DataFrame(rows)


def means_by_disclosure(panel: pd.DataFrame) -> pd.DataFrame:
    """Means for firm-years with and without a biodiversity discussion, with an unadjusted Welch test."""
    yes, no = panel.loc[panel["bd_count_lag"] == 1], panel.loc[panel["bd_count_lag"] == 0]
    rows = []
    for name in [cfg.DV_MAIN, cfg.DV_LOG] + cfg.CONTROLS:
        a, b = yes[name].dropna(), no[name].dropna()
        if len(a) < 2 or len(b) < 2:
            continue
        standard_error = math.sqrt(a.var() / len(a) + b.var() / len(b))
        t_value = (a.mean() - b.mean()) / standard_error if standard_error > 0 else np.nan
        p_value = math.erfc(abs(t_value) / math.sqrt(2)) if not np.isnan(t_value) else np.nan
        rows.append({"variable": name, "mean_count1": a.mean(), "mean_count0": b.mean(),
                     "difference": a.mean() - b.mean(), "t_unadjusted": t_value, "p_normal": p_value,
                     "n_count1": len(a), "n_count0": len(b)})
    return pd.DataFrame(rows)


def correlations(panel: pd.DataFrame) -> pd.DataFrame:
    names = [cfg.DV_MAIN] + cfg.SCORES + cfg.CONTROLS
    matrix = panel[names].corr()
    return matrix.reset_index().rename(columns={"index": "variable"})


def score_correlations(panel: pd.DataFrame) -> pd.DataFrame:
    """Correlations among the three scores, pooled and within firms.

    The within-firm figure removes the mean of each firm and of each fiscal year
    from every score, which is the variation that a model with firm and year
    effects uses. Firms with one firm-year have no such variation and are left out.
    """
    several = panel.groupby(cfg.ID_FIRM)[cfg.ID_FIRM].transform("size") > 1
    kept = panel.loc[several, [cfg.ID_FIRM, cfg.T_FYEAR] + cfg.SCORES]
    within = kept[cfg.SCORES].astype(float)
    for _ in range(500):
        before = within.to_numpy().copy()
        within = within - within.groupby(kept[cfg.ID_FIRM]).transform("mean")
        within = within - within.groupby(kept[cfg.T_FYEAR]).transform("mean")
        if np.abs(within.to_numpy() - before).max() < 1e-12:
            break
    pooled, inside = panel[cfg.SCORES].corr(), within.corr()
    rows = []
    for i, first in enumerate(cfg.SCORES):
        for second in cfg.SCORES[i + 1:]:
            rows.append({"score_a": first, "score_b": second, "corr_pooled": pooled.loc[first, second],
                         "corr_within_firm_and_year": inside.loc[first, second],
                         "n_pooled": len(panel), "n_within": len(kept)})
    return pd.DataFrame(rows)


def industry_distribution(panel: pd.DataFrame) -> pd.DataFrame:
    table = panel.groupby("ind_gics4").agg(
        n_firm_years=("id_gvkey", "size"), n_firms=("id_gvkey", "nunique"),
        pct_count1=("bd_count_lag", lambda s: 100 * s.mean()),
        pct_regulation1=("bd_regulation_lag", lambda s: 100 * s.mean()),
        mean_tobin_q=(cfg.DV_MAIN, "mean"),
        survey_score=("ind_bio_survey_avg", "first"), high_exposure=("ind_bio_high", "first"),
    ).reset_index()
    return table.sort_values("survey_score", ascending=False)


def make_figure(panel: pd.DataFrame):
    """Mean Tobin's Q by fiscal year, firms with and without a biodiversity discussion."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink, quiet, grid = "#0b0b0b", "#52514e", "#e3e2de"
    blue, orange = "#2a78d6", "#eb6834"  # validated pair: categorical slots 1 and 2
    means = panel.groupby(["t_fyear", "bd_count_lag"])[cfg.DV_MAIN].mean().unstack("bd_count_lag")
    fig, ax = plt.subplots(figsize=(7.2, 3.9), dpi=200)
    for value, colour, label in ((0, blue, "No biodiversity discussion (Count = 0)"),
                                 (1, orange, "Biodiversity discussed (Count = 1)")):
        if value not in means.columns:
            continue
        series = means[value].dropna()
        ax.plot(series.index, series.to_numpy(), color=colour, linewidth=2, solid_capstyle="round", label=label)
        ax.plot(series.index[-1], series.iloc[-1], "o", color=colour, markersize=5, markeredgecolor="white", markeredgewidth=1.5)
        ax.annotate(f"{series.iloc[-1]:.2f}", (series.index[-1], series.iloc[-1]), xytext=(6, 0),
                    textcoords="offset points", va="center", fontsize=8.5, color=ink)
    ax.set_xlim(means.index.min() - 0.3, means.index.max() + 0.9)
    ax.set_xticks(list(means.index))
    ax.set_ylabel("Mean Tobin's Q (winsorised)", fontsize=9, color=quiet)
    ax.set_xlabel("Fiscal year", fontsize=9, color=quiet)
    ax.grid(axis="y", color=grid, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(grid)
    ax.tick_params(colors=quiet, labelsize=8.5, length=0)
    ax.legend(loc="best", frameon=False, fontsize=8.5, labelcolor=ink)
    fig.tight_layout()
    path = cfg.DIR_FIGURES / "BRFV_F02_tobin_q_by_disclosure.png"
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    return path


def identifying_variation(panel: pd.DataFrame) -> pd.DataFrame:
    """Firm-years and firms that carry each score, and firms whose score changes over time."""
    rows = []
    for score in cfg.SCORES:
        by_firm = panel.groupby(cfg.ID_FIRM)[score].agg(["min", "max"])
        rows.append({"score": score,
                     "n_firm_years_not_zero": int((panel[score] != 0).sum()),
                     "n_firms_ever_not_zero": int(((by_firm["min"] != 0) | (by_firm["max"] != 0)).sum()),
                     "n_firms_changing": int((by_firm["min"] != by_firm["max"]).sum())})
    return pd.DataFrame(rows)


def main() -> int:
    u.ensure_dirs()
    if not cfg.PROC_PANEL.exists():
        log.error("panel missing: %s. Run step 04 first.", cfg.PROC_PANEL.name)
        return 2
    panel = load_panel()
    u.write_table(summary_statistics(panel), "BRFV_T05_summary_statistics",
                  note="Variables ending in _w are winsorised at the 1st and 99th percentiles.")
    u.write_table(means_by_disclosure(panel), "BRFV_T06_means_by_disclosure",
                  note="Welch t statistic with a normal p-value. Firm-years are not independent, so read it as a description only.")
    u.write_table(correlations(panel), "BRFV_T07_correlations", note="Pearson correlations.")
    u.write_table(score_correlations(panel), "BRFV_T17_score_correlations",
                  note="Pearson correlations among the three scores. The within figure removes firm and fiscal-year means, "
                       "on firms with at least two firm-years.")
    u.write_table(identifying_variation(panel), "BRFV_T14_identifying_variation",
                  note="Only a firm whose score changes over time identifies an estimate with firm fixed effects.")
    u.write_table(industry_distribution(panel), "BRFV_T08_industry_distribution",
                  note="GICS industry groups, sorted by the survey-based biodiversity exposure score.")
    log.info("figure written: %s", make_figure(panel).name)
    log.info("descriptive tables written for %s firm-years", f"{len(panel):,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
