"""BRFV configuration: paths, file names, sample rules and model settings.

Project : Biodiversity Risk Disclosure and Firm Valuation (BRFV)
Role    : single place for every rule. Steps import this module and never
          hard-code a path, a year or a threshold of their own.
Naming  : see 05_docs/BRFV_naming_convention.md
"""
from __future__ import annotations

import os
from pathlib import Path

# --------------------------------------------------------------------- paths
# The project root holds 01_data, 02_code, 03_output. Tests point the whole
# pipeline at a temporary copy through the BRFV_ROOT environment variable.
PROJECT_ROOT = Path(os.environ.get("BRFV_ROOT", Path(__file__).resolve().parents[1]))

DIR_RAW = PROJECT_ROOT / "01_data" / "raw"
DIR_RAW_GIGLIO = DIR_RAW / "giglio"
DIR_RAW_COMPUSTAT = DIR_RAW / "compustat"
DIR_RAW_CLIMATE = DIR_RAW / "climate"
DIR_RAW_EDGAR = DIR_RAW / "edgar"
DIR_INTERIM = PROJECT_ROOT / "01_data" / "interim"
DIR_PROCESSED = PROJECT_ROOT / "01_data" / "processed"
DIR_TABLES = PROJECT_ROOT / "03_output" / "tables"
DIR_FIGURES = PROJECT_ROOT / "03_output" / "figures"
DIR_LOGS = PROJECT_ROOT / "03_output" / "logs"
DIR_EXPECTED = Path(__file__).resolve().parent / "tests" / "expected"

# The draft that step 08 writes its tables, figures and quoted numbers into.
# Earlier drafts in 04_manuscript and 06_final are kept as they were and are not rewritten.
DRAFT_CURRENT = "draft_final_v5"
DIR_DRAFT = PROJECT_ROOT / "06_final" / DRAFT_CURRENT

ALL_DIRS = [
    DIR_RAW_GIGLIO, DIR_RAW_COMPUSTAT, DIR_RAW_CLIMATE, DIR_INTERIM,
    DIR_PROCESSED, DIR_TABLES, DIR_FIGURES, DIR_LOGS,
]

# ----------------------------------------------------------------- raw files
# Raw files keep the names their source gave them and are never edited.
RAW_SCORES = DIR_RAW_GIGLIO / "10k_biodiversity_scores_2024.csv"
RAW_SURVEY = DIR_RAW_GIGLIO / "survey_biodiversity_scores.csv"
RAW_HOLDING = DIR_RAW_GIGLIO / "holding_biodiversity_scores.csv"
RAW_CDP = DIR_RAW_GIGLIO / "cdp_biodiversity_scores.csv"
RAW_CODEBOOK = DIR_RAW_GIGLIO / "Biodiversity Data Codebook.pdf"
GIGLIO_ZIP_PATTERN = "BRFV_giglio_raw_*.zip"

# Compustat is licensed. The extract is supplied by the user (see
# 05_docs/BRFV_wrds_query_spec.md) and must never be published.
RAW_COMPUSTAT = DIR_RAW_COMPUSTAT / "BRFV_compustat_funda_raw.csv"
# Optional: firm-level climate change exposure (Sautner et al., 2023).
RAW_CLIMATE = DIR_RAW_CLIMATE / "BRFV_climate_exposure_raw.csv"
# Filing dates and counts of sentences with a biodiversity word, read from EDGAR (public) on
# 23 November 2026 to check what the year in the score file means. See the README beside the file.
RAW_EDGAR_CHECK = DIR_RAW_EDGAR / "BRFV_edgar_timing_check_20261123.csv"

# SHA-256 of the files as downloaded from https://www.biodiversityrisk.org/download/
# on 18 November 2026. A different hash means the authors have updated the file:
# the pipeline warns, and every number in the manuscript must then be rechecked.
EXPECTED_SHA256 = {
    "10k_biodiversity_scores_2024.csv": "35f65f792d818cc34a4e18ffe1501e53ccd1366604185959fabea3e4d9e7f6a5",
    "survey_biodiversity_scores.csv": "50468423d0178a54a8e0a6c5108bdf4fe654832f6009a689f77176ee21513bc5",
    "holding_biodiversity_scores.csv": "792ac6accac15b835393a4be9c2e8c73c9842bdeec85cd9b3815743020eee647",
    "cdp_biodiversity_scores.csv": "9939fc1b7f127191cb52a084d2aaad942ddb5e1f592ff075d9a31e99c3d8d78f",
    "Biodiversity Data Codebook.pdf": "070be50b09e05a1aa04723bf04a5e87d6b210006cb02eb3acd6db4ff0f26ab62",
}

# ------------------------------------------------------------ interim files
INT_SCORES = DIR_INTERIM / "BRFV_scores_firmyear_clean.csv"
INT_INDUSTRY = DIR_INTERIM / "BRFV_industry_exposure_gics4.csv"
INT_COMPUSTAT = DIR_INTERIM / "BRFV_compustat_firmyear_clean.csv"
PROC_PANEL = DIR_PROCESSED / "BRFV_panel_firmyear_analysis.csv"

# ------------------------------------------------------------- sample rules
# Score years. The file starts in 2000, but 2000 carries no positive score and
# lies before the coverage the authors state (2001 onwards), so it is dropped.
SCORE_YEAR_MIN = 2001
# 2024 was added by the authors after publication, on a wider set of firms and
# with a different identifier snapshot. The main sample stops at score year 2023.
SCORE_YEAR_MAX_MAIN = 2023
SCORE_YEAR_MAX_ALL = 2024

# What the "year" column of the score file means. The codebook does not say.
#   "fiscal": year = fiscal year the 10-K reports on. The score for year t-1 is
#             attached to Tobin's Q measured at the end of fiscal year t.
#   "filing": year = calendar year the 10-K was filed. The score for year t is
#             attached to Tobin's Q measured at the end of fiscal year t.
# Step 04 tests this on newly listed firms and stops if the data disagree.
#
# Note of 23 November 2026. A check of filings on EDGAR (01_data/raw/edgar) indicates that the
# year is the calendar year of filing. The test in step 04 reads an empty row in the last year
# of a firm as a year without a filing, and the check shows that such a row can be empty although
# a 10-K was filed, so the paper no longer relies on its verdict. The setting is kept as it was,
# because it fixes which score the models use and no estimate should move: the score labelled
# t-1 is attached to Tobin's Q at the end of fiscal year t. Read by filing year, this is the 10-K
# filed in the previous calendar year. The score labelled t (suffix _alt in the panel) is then the
# latest filing for a firm with a December year end, and it is used in checks R10, W10 and P8.
SCORE_YEAR_CONVENTION = "fiscal"

# Fiscal years in which Tobin's Q is measured.
Q_FYEAR_MIN = 2015
Q_FYEAR_MAX = 2024

# Financial firms (SIC 6000-6999) are excluded.
SIC_FINANCIAL = (6000, 6999)
# GICS industry groups that are financial or real estate, flagged in the
# industry file so that exposure terciles are formed on non-financial groups.
GICS4_FINANCIAL = ("4010", "4020", "4030", "6010", "6020")

# Continuous variables are winsorised at these pooled quantiles.
WINSOR_LIMITS = (0.01, 0.99)

# First fiscal year treated as after the Kunming Declaration (October 2021).
EVENT_FIRST_FYEAR = 2022
EVENT_TRANSITION_FYEAR = 2021  # fiscal years ending June 2021 to May 2022 straddle October 2021

# An industry group counts as highly exposed when its survey-based score lies
# above this quantile of the non-financial groups.
HIGH_EXPOSURE_QUANTILE = 2.0 / 3.0

# ----------------------------------------------------------------- variables
ID_FIRM = "id_gvkey"
T_FYEAR = "t_fyear"
FE_IND_YEAR = "fe_ind_year"
IND_KEY = "ind_gics4"

DV_MAIN = "dv_tobin_q_w"
DV_LOG = "dv_ln_tobin_q_w"
DV_INDADJ = "dv_tobin_q_indadj"

SCORES = ["bd_count_lag", "bd_negative_lag", "bd_regulation_lag"]

CONTROLS_RAW = [
    "ctl_size", "ctl_leverage", "ctl_roa", "ctl_tangibility",
    "ctl_sales_growth", "ctl_rd", "ctl_capex", "ctl_cash",
]
CONTROLS_BINARY = ["ctl_rd_missing", "ctl_dividend"]
CONTROLS = [c + "_w" for c in CONTROLS_RAW] + CONTROLS_BINARY
CONTINUOUS_TO_WINSORISE = ["dv_tobin_q", "dv_ln_tobin_q"] + CONTROLS_RAW

# Optional climate control: the column names used in the raw climate file.
# Set these to the names in the file you download; the control is the exposure
# measured in the same year as the biodiversity score.
CLIMATE_COLUMNS = {"firm": "gvkey", "year": "year", "exposure": "cc_expo_ew"}
CLIMATE_VAR = "cc_exposure_lag"

# The year-alignment test needs at least this many newly listed or delisted
# firms before it gives a verdict.
ALIGNMENT_MIN_FIRMS = 30
ALIGNMENT_EMPTY_SHARE = 0.005   # a boundary row counts as empty if at most this share of firms has any score
ALIGNMENT_FILLED_SHARE = 0.01   # and as filled if at least this share has one

# Standard errors are clustered by firm.
CLUSTER = ID_FIRM
