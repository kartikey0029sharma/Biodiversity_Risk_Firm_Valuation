"""BRFV shared helpers: logging, hashing, safe CSV reading, winsorising, tables.

Project : Biodiversity Risk Disclosure and Firm Valuation (BRFV)
Role    : functions used by more than one step. No rule lives here; rules are
          in brfv_00_config.py.
"""
from __future__ import annotations

import hashlib
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

import brfv_00_config as cfg

RUN_ID = os.environ.get("BRFV_RUN_ID") or datetime.now().strftime("%Y%m%d_%H%M%S")


# ------------------------------------------------------------------ logging
def ensure_dirs() -> None:
    """Create every project folder that the pipeline writes to."""
    for d in cfg.ALL_DIRS:
        d.mkdir(parents=True, exist_ok=True)


def get_logger(step: str) -> logging.Logger:
    """Logger that writes to the console and to 03_output/logs/BRFV_run_<id>.log."""
    ensure_dirs()
    logger = logging.getLogger(step)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S")
    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(fmt)
    logger.addHandler(stream)
    file_handler = logging.FileHandler(cfg.DIR_LOGS / f"BRFV_run_{RUN_ID}.log", encoding="utf-8")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger


# ------------------------------------------------------------------- files
def sha256_of(path: Path) -> str:
    """SHA-256 of a file, read in blocks."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv_as_text(path: Path, **kwargs) -> pd.DataFrame:
    """Read a CSV with every column as text and no automatic missing values.

    Two traps this avoids. First, pandas would turn the tickers "NA" and
    "TRUE" (both real tickers in the score file) into a missing value and a
    boolean. Second, a CUSIP such as 00846U101 would lose its leading zeros if
    it were read as a number.
    """
    return pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[], **kwargs)


def to_number(series: pd.Series) -> pd.Series:
    """Text to float; empty or non-numeric text becomes NaN."""
    return pd.to_numeric(series.astype(str).str.strip().replace("", np.nan), errors="coerce")


def read_pipeline_csv(path: Path, text_columns: list[str]) -> pd.DataFrame:
    """Read a file the pipeline wrote: named columns stay text, the rest become numbers."""
    frame = read_csv_as_text(path)
    for column in frame.columns:
        if column not in text_columns:
            frame[column] = to_number(frame[column])
    return frame


def assert_unique(frame: pd.DataFrame, keys: list[str], what: str) -> None:
    """Stop if the key columns do not identify one row each."""
    duplicated = int(frame.duplicated(keys).sum())
    if duplicated:
        raise ValueError(f"{what}: {duplicated} duplicated rows on {keys}")


# ------------------------------------------------------------- transforms
def winsorise(series: pd.Series, limits: tuple[float, float] = cfg.WINSOR_LIMITS) -> pd.Series:
    """Clip a series at its own lower and upper quantile; NaN stays NaN."""
    lower, upper = series.quantile(limits[0]), series.quantile(limits[1])
    return series.clip(lower=lower, upper=upper)


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Division that returns NaN where the denominator is zero, negative or missing."""
    result = numerator / denominator.where(denominator > 0)
    return result.replace([np.inf, -np.inf], np.nan)


# ------------------------------------------------------------------ tables
def stars(p_value: float) -> str:
    """Significance stars at 10, 5 and 1 per cent."""
    if pd.isna(p_value):
        return ""
    return "***" if p_value < 0.01 else "**" if p_value < 0.05 else "*" if p_value < 0.10 else ""


def _format_cell(value) -> str:
    if isinstance(value, (bool, np.bool_)):
        return "yes" if value else "no"
    if isinstance(value, (int, np.integer)):
        return f"{int(value):,}"
    if isinstance(value, (float, np.floating)):
        if pd.isna(value):
            return ""
        if float(value).is_integer() and abs(value) >= 1000:
            return f"{int(value):,}"
        return f"{value:.4f}" if abs(value) < 1000 else f"{value:,.1f}"
    return "" if value is None else str(value)


def to_markdown(frame: pd.DataFrame) -> str:
    """Plain pipe table, written without extra packages."""
    header = "| " + " | ".join(str(c) for c in frame.columns) + " |"
    divider = "| " + " | ".join("---" for _ in frame.columns) + " |"
    rows = ["| " + " | ".join(_format_cell(v) for v in row) + " |" for row in frame.itertuples(index=False)]
    return "\n".join([header, divider] + rows) + "\n"


def write_table(frame: pd.DataFrame, stem: str, note: str = "") -> Path:
    """Write a table twice: CSV for machines, Markdown for reading.

    stem is the file name without extension, for example BRFV_T01_scores_by_year.
    """
    ensure_dirs()
    csv_path = cfg.DIR_TABLES / f"{stem}.csv"
    frame.to_csv(csv_path, index=False)
    text = f"# {stem}\n\n{to_markdown(frame)}"
    if note:
        text += f"\n{note}\n"
    (cfg.DIR_TABLES / f"{stem}.md").write_text(text, encoding="utf-8")
    return csv_path


class Attrition:
    """Records how many rows and firms survive each sample filter."""

    def __init__(self, firm_col: str):
        self.firm_col = firm_col
        self.rows: list[dict] = []

    def add(self, step: str, frame: pd.DataFrame) -> None:
        previous = self.rows[-1]["n_firm_years"] if self.rows else len(frame)
        self.rows.append({
            "step": step,
            "n_firm_years": len(frame),
            "n_firms": frame[self.firm_col].nunique(),
            "dropped_firm_years": previous - len(frame),
        })

    def table(self) -> pd.DataFrame:
        return pd.DataFrame(self.rows)
