"""BRFV step 01: import, check and profile the 10-K biodiversity scores.

Project : Biodiversity Risk Disclosure and Firm Valuation (BRFV)
Input   : 01_data/raw/giglio/   (files from https://www.biodiversityrisk.org/download/)
Output  : 01_data/interim/BRFV_scores_firmyear_clean.csv
          01_data/interim/BRFV_industry_exposure_gics4.csv
          03_output/tables/BRFV_T01_scores_by_year.(csv|md)
          03_output/tables/BRFV_T02_score_persistence.(csv|md)
          03_output/figures/BRFV_F01_disclosure_share_by_year.png
Source  : Giglio, Kuchler, Stroebel and Zeng (2026), Review of Finance 30(1), 131-161.

What the raw score file looks like (checked on the file of 18 November 2026):
  * columns ticker, year, cusip, count, negative, regulation; Windows line ends
  * 60,422 rows, years 2000 to 2024, one row per ticker and year
  * 458 rows have no CUSIP and no count or regulation value: they carry no score
  * year 2000 has no positive score and lies before the stated coverage
  * CUSIPs have nine characters up to 2023 and eight characters in 2024
  * the tickers "NA" and "TRUE" exist, so the file must be read as text
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

import brfv_00_config as cfg
import brfv_utils as u

log = u.get_logger("brfv_01_import_scores")

RAW_GIGLIO_FILES = [cfg.RAW_SCORES, cfg.RAW_SURVEY, cfg.RAW_HOLDING, cfg.RAW_CDP, cfg.RAW_CODEBOOK]
SCORE_COLUMNS = ["ticker", "year", "cusip", "count", "negative", "regulation"]
PERSISTENCE_WINDOWS = [(2001, 2023), (2014, 2023), (2015, 2023), (2001, 2024), (2015, 2024)]


# ------------------------------------------------------------- raw files
def unpack_zip_if_needed() -> None:
    """Fill 01_data/raw/giglio from BRFV_giglio_raw_*.zip when files are missing.

    The zip may sit in the project root, in 01_data/raw or in 01_data/raw/giglio.
    Members are matched by file name and written to fixed paths only.
    """
    missing = [p for p in RAW_GIGLIO_FILES if not p.exists()]
    if not missing:
        return
    candidates: list[Path] = []
    for folder in (cfg.PROJECT_ROOT, cfg.DIR_RAW, cfg.DIR_RAW_GIGLIO):
        candidates += sorted(folder.glob(cfg.GIGLIO_ZIP_PATTERN))
    if not candidates:
        return
    archive = candidates[-1]
    with zipfile.ZipFile(archive) as bundle:
        members = {Path(name).name: name for name in bundle.namelist()}
        for target in missing:
            if target.name in members:
                target.write_bytes(bundle.read(members[target.name]))
                log.info("unpacked %s from %s", target.name, archive.name)


def verify_hashes() -> dict[str, str]:
    """Compare each raw file with the SHA-256 recorded on the download day."""
    status: dict[str, str] = {}
    for path in RAW_GIGLIO_FILES:
        if not path.exists():
            status[path.name] = "missing"
            log.warning("raw file missing: %s", path.name)
            continue
        same = u.sha256_of(path) == cfg.EXPECTED_SHA256[path.name]
        status[path.name] = "match" if same else "changed"
        if same:
            log.info("hash check passed: %s", path.name)
        else:
            log.warning("hash differs from the 18 Nov 2026 download: %s. The source file has "
                        "changed, so recheck every number that depends on it.", path.name)
    return status


# ----------------------------------------------------------------- scores
def load_scores_raw() -> pd.DataFrame:
    """Read the firm-level score file exactly as text."""
    raw = u.read_csv_as_text(cfg.RAW_SCORES)
    if list(raw.columns) != SCORE_COLUMNS:
        raise ValueError(f"unexpected columns in {cfg.RAW_SCORES.name}: {list(raw.columns)}")
    for column in raw.columns:
        raw[column] = raw[column].str.strip()
    return raw


def clean_scores(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Apply the cleaning rules and return the clean frame with an audit trail."""
    audit: dict = {"rows_raw": len(raw)}
    frame = raw.copy()
    frame["ticker"] = frame["ticker"].str.upper()
    frame["cusip"] = frame["cusip"].str.upper()

    # Rule 1: rows without a count value carry no score.
    no_score = frame["count"] == ""
    audit["rows_without_score"] = int(no_score.sum())
    audit["rows_without_score_and_cusip"] = int((no_score & (frame["cusip"] == "")).sum())
    frame = frame.loc[~no_score].copy()

    # Rule 2: years before the stated coverage are dropped.
    frame["t_score_year"] = frame["year"].astype(int)
    early = frame["t_score_year"] < cfg.SCORE_YEAR_MIN
    audit["rows_before_coverage"] = int(early.sum())
    audit["positive_scores_before_coverage"] = int((early & (frame["count"] == "1")).sum())
    frame = frame.loc[~early].copy()

    for column in ("count", "negative", "regulation"):
        frame["bd_" + column] = frame[column].astype(int)

    # Rule 3: value checks. A failure here means the source file has changed.
    if not set(frame["bd_count"].unique()) <= {0, 1}:
        raise ValueError("count takes values other than 0 and 1")
    if not set(frame["bd_regulation"].unique()) <= {0, 1}:
        raise ValueError("regulation takes values other than 0 and 1")
    if ((frame["bd_regulation"] == 1) & (frame["bd_count"] == 0)).any():
        raise ValueError("regulation = 1 found where count = 0")

    frame["id_cusip8"] = frame["cusip"].str.slice(0, 8)
    frame["cusip_len"] = frame["cusip"].str.len()
    audit["rows_clean_without_cusip"] = int((frame["id_cusip8"] == "").sum())
    audit["rows_with_8_char_cusip"] = int((frame["cusip_len"] == 8).sum())
    frame["bd_negative_pos"] = (frame["bd_negative"] > 0).astype(int)
    frame = frame.rename(columns={"ticker": "id_ticker", "cusip": "cusip_raw"})

    # Rule 4: one row per ticker-year and per CUSIP-year.
    u.assert_unique(frame, ["id_ticker", "t_score_year"], "scores by ticker and year")
    u.assert_unique(frame.loc[frame["id_cusip8"] != ""], ["id_cusip8", "t_score_year"], "scores by CUSIP and year")

    keep = ["id_ticker", "id_cusip8", "cusip_raw", "cusip_len", "t_score_year",
            "bd_count", "bd_negative", "bd_regulation", "bd_negative_pos"]
    frame = frame[keep].sort_values(["id_ticker", "t_score_year"]).reset_index(drop=True)
    audit["rows_clean"] = len(frame)
    audit["tickers_clean"] = int(frame["id_ticker"].nunique())
    return frame, audit


def profile_by_year(raw: pd.DataFrame, clean: pd.DataFrame) -> pd.DataFrame:
    """Counts and shares of the three scores for each score year."""
    raw_years = raw["year"].astype(int)
    raw_counts = raw_years[raw_years >= cfg.SCORE_YEAR_MIN].value_counts().rename("n_rows_raw")
    grouped = clean.groupby("t_score_year").agg(
        n_valid=("bd_count", "size"),
        n_count1=("bd_count", "sum"),
        n_regulation1=("bd_regulation", "sum"),
        n_negative_pos=("bd_negative", lambda s: int((s > 0).sum())),
        n_negative_neg=("bd_negative", lambda s: int((s < 0).sum())),
    )
    table = grouped.join(raw_counts).reset_index()
    table["pct_count1"] = (100 * table["n_count1"] / table["n_valid"]).round(2)
    table["pct_regulation1"] = (100 * table["n_regulation1"] / table["n_valid"]).round(2)
    table["pct_negative_pos"] = (100 * table["n_negative_pos"] / table["n_valid"]).round(2)
    columns = ["t_score_year", "n_rows_raw", "n_valid", "n_count1", "n_regulation1",
               "n_negative_pos", "n_negative_neg", "pct_count1", "pct_regulation1", "pct_negative_pos"]
    return table[columns].astype({"n_rows_raw": int})


def persistence(clean: pd.DataFrame, first_year: int, last_year: int, id_col: str = "id_ticker") -> dict:
    """How stable the count score is within firms over a window of score years."""
    window = clean.loc[clean["t_score_year"].between(first_year, last_year), [id_col, "t_score_year", "bd_count"]]
    window = window.sort_values([id_col, "t_score_year"]).copy()
    per_firm = window.groupby(id_col)["bd_count"].agg(["size", "sum"])
    previous_year = window.groupby(id_col)["t_score_year"].shift(1)
    previous_value = window.groupby(id_col)["bd_count"].shift(1)
    consecutive = (window["t_score_year"] - previous_year) == 1
    pairs = window.loc[consecutive].assign(previous=previous_value[consecutive].astype(int))
    t11 = int(((pairs["previous"] == 1) & (pairs["bd_count"] == 1)).sum())
    t10 = int(((pairs["previous"] == 1) & (pairs["bd_count"] == 0)).sum())
    t01 = int(((pairs["previous"] == 0) & (pairs["bd_count"] == 1)).sum())
    t00 = int(((pairs["previous"] == 0) & (pairs["bd_count"] == 0)).sum())
    return {
        "window": f"{first_year}-{last_year}",
        "n_firms": int(len(per_firm)),
        "n_firm_years": int(per_firm["size"].sum()),
        "n_count1": int(per_firm["sum"].sum()),
        "firms_ever": int((per_firm["sum"] > 0).sum()),
        "firms_always": int((per_firm["sum"] == per_firm["size"]).sum()),
        "firms_switch": int(((per_firm["sum"] > 0) & (per_firm["sum"] < per_firm["size"])).sum()),
        "t11": t11, "t10": t10, "t01": t01, "t00": t00,
        "pct_stay_1": round(100 * t11 / (t11 + t10), 2) if (t11 + t10) else np.nan,
        "pct_enter_1": round(100 * t01 / (t01 + t00), 2) if (t01 + t00) else np.nan,
    }


def compare_with_expected(by_year: pd.DataFrame, persistence_table: pd.DataFrame) -> str:
    """Check the tables against the values recorded when the file was first read.

    The recorded values came from an independent count of the same bytes on
    18 November 2026. A mismatch on an unchanged file means the code is wrong.
    """
    by_year_path = cfg.DIR_EXPECTED / "BRFV_expected_scores_by_year_20261118.csv"
    persistence_path = cfg.DIR_EXPECTED / "BRFV_expected_score_persistence_20261118.csv"
    if not by_year_path.exists() or not persistence_path.exists():
        return "no expected values on file"
    expected_year = pd.read_csv(by_year_path)
    expected_pers = pd.read_csv(persistence_path)
    count_columns = ["n_rows_raw", "n_valid", "n_count1", "n_regulation1", "n_negative_pos", "n_negative_neg"]
    got_year = by_year.set_index("t_score_year")[count_columns]
    want_year = expected_year.set_index("t_score_year")[count_columns].reindex(got_year.index)
    year_ok = bool((got_year.to_numpy(dtype=float) == want_year.to_numpy(dtype=float)).all())
    pers_columns = ["n_firms", "n_firm_years", "n_count1", "firms_ever", "firms_always",
                    "firms_switch", "t11", "t10", "t01", "t00"]
    want_pers = expected_pers.set_index("window")[pers_columns]
    got_pers = persistence_table.set_index("window")[pers_columns].reindex(want_pers.index)
    pers_ok = bool((got_pers.to_numpy(dtype=float) == want_pers.to_numpy(dtype=float)).all())
    if not (year_ok and pers_ok):
        raise AssertionError("score tables differ from the values recorded on 18 Nov 2026 "
                             "although the raw file is unchanged: check the cleaning rules")
    return "match"


# -------------------------------------------------------------- industry
def load_industry_scores() -> pd.DataFrame:
    """Industry-level exposure scores by GICS industry group (four digits)."""
    def gics(series: pd.Series) -> pd.Series:
        return series.str.strip().str.replace(r"\.0$", "", regex=True)

    survey = u.read_csv_as_text(cfg.RAW_SURVEY)
    frame = pd.DataFrame({
        "ind_gics4": gics(survey["gics4"]),
        "ind_bio_survey_trans": u.to_number(survey["transition"]),
        "ind_bio_survey_phys": u.to_number(survey["physical"]),
        "ind_bio_survey_avg": u.to_number(survey["average"]),
    })
    for path, name in ((cfg.RAW_HOLDING, "ind_bio_holding"), (cfg.RAW_CDP, "ind_bio_cdp")):
        if path.exists():
            other = u.read_csv_as_text(path)
            other = pd.DataFrame({"ind_gics4": gics(other["gics4"]), name: u.to_number(other["score"])})
            frame = frame.merge(other, on="ind_gics4", how="left", validate="one_to_one")
    u.assert_unique(frame, ["ind_gics4"], "industry scores")
    frame["ind_is_financial"] = frame["ind_gics4"].isin(cfg.GICS4_FINANCIAL).astype(int)
    non_financial = frame.loc[frame["ind_is_financial"] == 0, "ind_bio_survey_avg"]
    threshold = non_financial.quantile(cfg.HIGH_EXPOSURE_QUANTILE)
    frame["ind_bio_high"] = (frame["ind_bio_survey_avg"] > threshold).astype(int)
    frame["ind_bio_survey_z"] = (frame["ind_bio_survey_avg"] - non_financial.mean()) / non_financial.std(ddof=0)
    log.info("high-exposure threshold on the survey score: %.4f; %d of %d non-financial groups are high",
             threshold, int(frame.loc[frame["ind_is_financial"] == 0, "ind_bio_high"].sum()), len(non_financial))
    return frame.sort_values("ind_gics4").reset_index(drop=True)


# ----------------------------------------------------------------- figure
def make_figure(by_year: pd.DataFrame) -> Path:
    """Share of firms whose 10-K discusses biodiversity, by score year."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink, quiet, grid = "#0b0b0b", "#52514e", "#e3e2de"
    blue, orange = "#2a78d6", "#eb6834"  # validated pair: categorical slots 1 and 2
    years = by_year["t_score_year"].to_numpy()
    fig, ax = plt.subplots(figsize=(7.2, 3.9), dpi=200)
    for column, colour, label in (("pct_count1", blue, "Biodiversity discussed (Count = 1)"),
                                  ("pct_regulation1", orange, "Regulation mentioned (Regulation = 1)")):
        values = by_year[column].to_numpy()
        ax.plot(years, values, color=colour, linewidth=2, solid_capstyle="round", solid_joinstyle="round", label=label)
        ax.plot(years[-1], values[-1], "o", color=colour, markersize=5, markeredgecolor="white", markeredgewidth=1.5)
        ax.annotate(f"{values[-1]:.1f}%", (years[-1], values[-1]), xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=8.5, color=ink)
    ax.set_ylim(0, max(6.0, float(by_year["pct_count1"].max()) * 1.15))
    ax.set_xlim(years.min() - 0.5, years.max() + 1.6)
    ax.set_xticks([y for y in years if y % 4 == 1 or y == years.max()])
    ax.yaxis.set_major_formatter(lambda value, _: f"{value:.0f}%")
    ax.set_ylabel("Share of firms in the score file", fontsize=9, color=quiet)
    ax.set_xlabel("Score year", fontsize=9, color=quiet)
    ax.grid(axis="y", color=grid, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(grid)
    ax.tick_params(colors=quiet, labelsize=8.5, length=0)
    if cfg.SCORE_YEAR_MAX_ALL in years and cfg.SCORE_YEAR_MAX_MAIN in years:
        ax.axvline(cfg.SCORE_YEAR_MAX_MAIN + 0.5, color=grid, linewidth=0.8)
        ax.annotate("2024 added later,\nwider set of firms", (cfg.SCORE_YEAR_MAX_MAIN + 0.5, ax.get_ylim()[1]),
                    xytext=(-4, -4), textcoords="offset points", ha="right", va="top", fontsize=7.5, color=quiet)
    ax.legend(loc="upper left", frameon=False, fontsize=8.5, labelcolor=ink)
    fig.tight_layout()
    path = cfg.DIR_FIGURES / "BRFV_F01_disclosure_share_by_year.png"
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    return path


# ------------------------------------------------------------------- main
def main() -> int:
    u.ensure_dirs()
    unpack_zip_if_needed()
    if not cfg.RAW_SCORES.exists():
        log.error("score file not found: %s. Put BRFV_giglio_raw_*.zip in the project folder, or download "
                  "the files from https://www.biodiversityrisk.org/download/ into 01_data/raw/giglio/.", cfg.RAW_SCORES)
        return 2
    hashes = verify_hashes()

    raw = load_scores_raw()
    clean, audit = clean_scores(raw)
    clean.to_csv(cfg.INT_SCORES, index=False)
    for key, value in audit.items():
        log.info("score audit | %s = %s", key, f"{value:,}")

    by_year = profile_by_year(raw, clean)
    u.write_table(by_year, "BRFV_T01_scores_by_year",
                  note="Source: 10k_biodiversity_scores_2024.csv (Giglio et al., 2026). n_valid excludes rows without "
                       "a score. Percentages are of n_valid. Score year 2024 covers a wider set of firms.")
    persistence_table = pd.DataFrame([persistence(clean, a, b) for a, b in PERSISTENCE_WINDOWS])
    u.write_table(persistence_table, "BRFV_T02_score_persistence",
                  note="Firms are identified by ticker. t11 counts firm-years with Count = 1 in two consecutive years, "
                       "t10 a move from 1 to 0, t01 a move from 0 to 1. Windows ending in 2024 are affected by the "
                       "change of ticker snapshot in the 2024 rows and are shown for completeness only.")

    if hashes.get(cfg.RAW_SCORES.name) == "match":
        log.info("comparison with recorded values: %s", compare_with_expected(by_year, persistence_table))
    else:
        log.warning("recorded values not compared because the raw score file differs from the recorded one")

    figure = make_figure(by_year)
    log.info("figure written: %s", figure.name)

    if cfg.RAW_SURVEY.exists():
        industry = load_industry_scores()
        industry.to_csv(cfg.INT_INDUSTRY, index=False)
        log.info("industry exposure written: %d GICS groups", len(industry))
    else:
        log.warning("survey file missing: industry exposure not built")

    main_window = clean["t_score_year"].between(2015, cfg.SCORE_YEAR_MAX_MAIN)
    log.info("score years 2015-%d: %s firm-years, %.2f%% with Count = 1", cfg.SCORE_YEAR_MAX_MAIN,
             f"{int(main_window.sum()):,}", 100 * clean.loc[main_window, "bd_count"].mean())
    return 0


if __name__ == "__main__":
    sys.exit(main())
