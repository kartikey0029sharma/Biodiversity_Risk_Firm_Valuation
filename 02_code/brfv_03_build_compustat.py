"""BRFV step 03: clean the Compustat extract and build Tobin's Q and the controls.

Project : Biodiversity Risk Disclosure and Firm Valuation (BRFV)
Input   : 01_data/raw/compustat/BRFV_compustat_funda_raw.csv
          (from brfv_02_pull_compustat_wrds.py or the WRDS web query in
          05_docs/BRFV_wrds_query_spec.md; licensed data, never published)
Output  : 01_data/interim/BRFV_compustat_firmyear_clean.csv
Rules   : variable definitions are listed in 05_docs/BRFV_data_dictionary.csv.

Tobin's Q = (total assets - book equity + market value of equity) / total assets
          = (AT - CEQ + PRCC_F x CSHO) / AT
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import brfv_00_config as cfg
import brfv_utils as u

log = u.get_logger("brfv_03_build_compustat")

REQUIRED = ["gvkey", "datadate", "fyear", "tic", "cusip", "at", "ceq", "csho", "prcc_f", "dltt", "dlc",
            "oibdp", "ppent", "sale", "xrd", "capx", "che", "dvc", "ggroup"]
NUMERIC = ["fyear", "at", "ceq", "csho", "prcc_f", "dltt", "dlc", "oibdp", "ppent", "sale", "xrd", "capx",
           "che", "dvc", "sich", "sic"]
STANDARD_FORMAT = {"indfmt": "INDL", "datafmt": "STD", "popsrc": "D", "consol": "C"}


def load_raw() -> pd.DataFrame:
    """Read the extract as text and put the column names in lower case."""
    raw = u.read_csv_as_text(cfg.RAW_COMPUSTAT)
    raw.columns = [c.strip().lower() for c in raw.columns]
    missing = [c for c in REQUIRED if c not in raw.columns]
    if missing:
        raise ValueError(f"Compustat extract lacks required columns: {missing}")
    if "sich" not in raw.columns and "sic" not in raw.columns:
        raise ValueError("Compustat extract needs sich or sic to drop financial firms")
    for column in raw.columns:
        raw[column] = raw[column].str.strip()
    return raw


def clean(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """One row per firm and fiscal year, with Tobin's Q and the controls."""
    audit: dict = {"rows_raw": len(raw)}
    frame = raw.copy()

    # Keep the standard Compustat format when the columns are present.
    for column, value in STANDARD_FORMAT.items():
        if column in frame.columns:
            keep = frame[column].str.upper() == value
            audit[f"rows_dropped_{column}_not_{value}"] = int((~keep).sum())
            frame = frame.loc[keep].copy()

    for column in NUMERIC:
        if column in frame.columns:
            frame[column] = u.to_number(frame[column])
    frame = frame.loc[frame["fyear"].notna()].copy()
    frame["t_fyear"] = frame["fyear"].astype(int)
    frame["id_gvkey"] = frame["gvkey"].str.zfill(6)
    frame["id_cusip8"] = frame["cusip"].str.upper().str.slice(0, 8)
    frame["id_ticker"] = frame["tic"].str.upper()
    digits_only = frame["datadate"].str.fullmatch(r"\d{8}").all()
    frame["t_datadate"] = pd.to_datetime(frame["datadate"], format="%Y%m%d" if digits_only else None, errors="coerce")
    frame["t_fye_month"] = frame["t_datadate"].dt.month

    # A change of fiscal year end can leave two rows in one fiscal year: keep the later one.
    frame = frame.sort_values(["id_gvkey", "t_fyear", "t_datadate"])
    duplicated = frame.duplicated(["id_gvkey", "t_fyear"], keep="last")
    audit["rows_dropped_duplicate_gvkey_fyear"] = int(duplicated.sum())
    frame = frame.loc[~duplicated].copy()
    u.assert_unique(frame, ["id_gvkey", "t_fyear"], "Compustat firm-years")

    # Industry codes.
    sich = frame["sich"] if "sich" in frame.columns else pd.Series(np.nan, index=frame.index)
    sic = frame["sic"] if "sic" in frame.columns else pd.Series(np.nan, index=frame.index)
    frame["ind_sic"] = sich.fillna(sic)
    frame["ind_sic2"] = np.floor(frame["ind_sic"] / 100)
    frame["ind_gics4"] = frame["ggroup"].str.replace(r"\.0$", "", regex=True)
    frame["geo_fic"] = frame["fic"].str.upper() if "fic" in frame.columns else ""
    frame["fin_curcd"] = frame["curcd"].str.upper() if "curcd" in frame.columns else ""

    # Raw items kept under the fin_ prefix (USD million, except price in USD).
    for item in ("at", "ceq", "sale"):
        frame[f"fin_{item}"] = frame[item]
    frame["fin_mve"] = frame["prcc_f"] * frame["csho"]

    # Dependent variable.
    frame["dv_tobin_q"] = u.safe_divide(frame["at"] - frame["ceq"] + frame["fin_mve"], frame["at"])
    frame["dv_ln_tobin_q"] = np.log(frame["dv_tobin_q"].where(frame["dv_tobin_q"] > 0))

    # Controls.
    frame["ctl_size"] = np.log(frame["at"].where(frame["at"] > 0))
    debt = frame["dltt"].fillna(0) + frame["dlc"].fillna(0)
    debt = debt.where(frame["dltt"].notna() | frame["dlc"].notna())
    frame["ctl_leverage"] = u.safe_divide(debt, frame["at"])
    frame["ctl_roa"] = u.safe_divide(frame["oibdp"], frame["at"])
    frame["ctl_tangibility"] = u.safe_divide(frame["ppent"], frame["at"])
    frame["ctl_rd_missing"] = frame["xrd"].isna().astype(int)
    frame["ctl_rd"] = u.safe_divide(frame["xrd"].fillna(0), frame["at"])
    frame["ctl_capex"] = u.safe_divide(frame["capx"], frame["at"])
    frame["ctl_cash"] = u.safe_divide(frame["che"], frame["at"])
    frame["ctl_dividend"] = (frame["dvc"].fillna(0) > 0).astype(int)

    # Sales growth needs the previous fiscal year of the same firm.
    previous_year = frame.groupby("id_gvkey")["t_fyear"].shift(1)
    previous_sale = frame.groupby("id_gvkey")["sale"].shift(1)
    consecutive = (frame["t_fyear"] - previous_year) == 1
    growth = frame["sale"] / previous_sale.where(previous_sale > 0) - 1
    frame["ctl_sales_growth"] = growth.where(consecutive).replace([np.inf, -np.inf], np.nan)

    keep = ["id_gvkey", "id_cusip8", "id_ticker", "t_fyear", "t_datadate", "t_fye_month", "geo_fic", "fin_curcd",
            "ind_sic", "ind_sic2", "ind_gics4", "fin_at", "fin_ceq", "fin_sale", "fin_mve",
            "dv_tobin_q", "dv_ln_tobin_q"] + cfg.CONTROLS_RAW + cfg.CONTROLS_BINARY
    if "conm" in frame.columns:
        frame["id_conm"] = frame["conm"]
        keep.insert(3, "id_conm")
    frame = frame[keep].sort_values(["id_gvkey", "t_fyear"]).reset_index(drop=True)
    audit["rows_clean"] = len(frame)
    audit["firms_clean"] = int(frame["id_gvkey"].nunique())
    audit["fyear_min"] = int(frame["t_fyear"].min())
    audit["fyear_max"] = int(frame["t_fyear"].max())
    return frame, audit


def main() -> int:
    u.ensure_dirs()
    if not cfg.RAW_COMPUSTAT.exists():
        log.error("Compustat extract not found: %s. See 05_docs/BRFV_wrds_query_spec.md.", cfg.RAW_COMPUSTAT)
        return 2
    log.info("raw extract sha256: %s", u.sha256_of(cfg.RAW_COMPUSTAT))
    frame, audit = clean(load_raw())
    for key, value in audit.items():
        log.info("compustat audit | %s = %s", key, str(value) if key.startswith("fyear") else f"{value:,}")
    if audit["fyear_min"] > cfg.Q_FYEAR_MIN - 1:
        log.warning("extract starts in %d; sales growth for %d needs fiscal year %d",
                    audit["fyear_min"], cfg.Q_FYEAR_MIN, cfg.Q_FYEAR_MIN - 1)
    frame.to_csv(cfg.INT_COMPUSTAT, index=False)
    log.info("written: %s", cfg.INT_COMPUSTAT.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
