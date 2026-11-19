"""BRFV tests: run the whole pipeline on a synthetic fixture and check its logic.

Project : Biodiversity Risk Disclosure and Firm Valuation (BRFV)
Run     : from 02_code,  python -m pytest tests -q
Note    : the fixture is INVENTED data in a temporary folder. The last test
          runs on the real score file instead and is skipped until that file
          is in 01_data/raw/giglio.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

CODE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from brfv_make_synthetic_fixture import build_fixture  # noqa: E402


def run_step(script: str, root: Path, extra_env: dict | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ, "BRFV_ROOT": str(root), "BRFV_RUN_ID": "test", "MPLBACKEND": "Agg"}
    env.pop("BRFV_ALLOW_ALIGNMENT_MISMATCH", None)
    env.update(extra_env or {})
    return subprocess.run([sys.executable, str(CODE_DIR / script)], env=env, cwd=CODE_DIR,
                          capture_output=True, text=True)


def read_text(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


@pytest.fixture(scope="module")
def project(tmp_path_factory):
    root = tmp_path_factory.mktemp("brfv_fiscal")
    truth = build_fixture(root, convention="fiscal")
    result = run_step("brfv_99_run_all.py", root)
    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-3000:]
    return root, truth


# ------------------------------------------------------------ step 01
def test_scores_are_cleaned_as_documented(project):
    root, truth = project
    clean = read_text(root / "01_data/interim/BRFV_scores_firmyear_clean.csv")
    years = clean["t_score_year"].astype(int)
    assert years.min() >= 2001, "year 2000 must be dropped"
    assert len(clean) == truth["n_score_rows_raw"] - truth["n_no_score_rows"] - truth["n_year_2000_rows"]
    assert {"NA", "TRUE"} <= set(clean["id_ticker"]), "tickers NA and TRUE must survive as text"
    assert (clean["id_cusip8"].str.len() == 8).all()
    assert clean.loc[years == 2024, "cusip_len"].eq("8").all() and clean.loc[years < 2024, "cusip_len"].eq("9").all()
    assert clean["id_cusip8"].str.startswith("0").any(), "leading zeros in CUSIPs must be kept"
    assert not clean.duplicated(["id_ticker", "t_score_year"]).any()


def test_score_tables_add_up(project):
    root, _ = project
    by_year = pd.read_csv(root / "03_output/tables/BRFV_T01_scores_by_year.csv")
    clean = read_text(root / "01_data/interim/BRFV_scores_firmyear_clean.csv")
    assert by_year["n_valid"].sum() == len(clean)
    assert by_year["n_count1"].sum() == clean["bd_count"].astype(int).sum()
    assert (by_year["n_regulation1"] <= by_year["n_count1"]).all()
    persistence = pd.read_csv(root / "03_output/tables/BRFV_T02_score_persistence.csv").set_index("window")
    row = persistence.loc["2015-2023"]
    assert row["firms_ever"] == row["firms_always"] + row["firms_switch"]
    assert (root / "03_output/figures/BRFV_F01_disclosure_share_by_year.png").stat().st_size > 10_000


# ------------------------------------------------------------ step 03
def test_tobin_q_matches_the_formula(project):
    root, truth = project
    clean = pd.read_csv(root / "01_data/interim/BRFV_compustat_firmyear_clean.csv", dtype={"id_gvkey": str})
    raw = truth["raw_compustat"]
    raw = raw.loc[(raw["indfmt"] == "INDL") & (raw["prcc_f"] != "") & (raw["fyear"] == 2019)]
    raw = raw.drop_duplicates(["gvkey", "fyear"], keep=False).head(25)
    for record in raw.itertuples():
        expected = (record.at - record.ceq + float(record.prcc_f) * record.csho) / record.at
        got = clean.loc[(clean["id_gvkey"] == record.gvkey) & (clean["t_fyear"] == 2019), "dv_tobin_q"].iloc[0]
        assert got == pytest.approx(expected, rel=1e-9)
    assert not clean.duplicated(["id_gvkey", "t_fyear"]).any()


# ------------------------------------------------------------ step 04
def test_score_is_lagged_one_fiscal_year(project):
    root, truth = project
    panel = pd.read_csv(root / "01_data/processed/BRFV_panel_firmyear_analysis.csv", dtype={"id_gvkey": str})
    merged = panel.merge(truth["truth"], on=["id_gvkey", "t_fyear"], how="left", validate="one_to_one")
    assert merged["has_score_row"].all(), "every panel row must come from a real score row"
    assert (merged["bd_count_lag"] == merged["count_lag_true"]).all()
    assert (merged["t_score_year"] == merged["t_fyear"] - 1).all()


def test_sample_filters_and_attrition(project):
    root, _ = project
    panel = pd.read_csv(root / "01_data/processed/BRFV_panel_firmyear_analysis.csv", dtype={"id_gvkey": str, "ind_gics4": str})
    assert panel["t_fyear"].between(2015, 2024).all()
    assert not panel["ind_sic"].between(6000, 6999).any()
    assert (panel["geo_fic"] == "USA").all()
    assert not panel.duplicated(["id_gvkey", "t_fyear"]).any()
    attrition = pd.read_csv(root / "03_output/tables/BRFV_T04_sample_attrition.csv")
    assert attrition["n_firm_years"].is_monotonic_decreasing
    assert attrition["n_firm_years"].iloc[-1] == len(panel)
    assert attrition["dropped_firm_years"].iloc[1:].sum() == attrition["n_firm_years"].iloc[0] - len(panel)


def test_winsorising_clips_at_the_stated_quantiles(project):
    root, _ = project
    panel = pd.read_csv(root / "01_data/processed/BRFV_panel_firmyear_analysis.csv")
    low, high = panel["dv_tobin_q"].quantile([0.01, 0.99])
    assert panel["dv_tobin_q_w"].min() == pytest.approx(low)
    assert panel["dv_tobin_q_w"].max() == pytest.approx(high)
    inside = panel["dv_tobin_q"].between(low, high)
    assert (panel.loc[inside, "dv_tobin_q_w"] == panel.loc[inside, "dv_tobin_q"]).all()


def test_year_alignment_verdict_is_fiscal(project):
    root, _ = project
    table = pd.read_csv(root / "03_output/tables/BRFV_T03_year_alignment_test.csv")
    assert "verdict: fiscal" in table["signal"].iloc[-1]


def test_other_timing_score_is_the_next_score_year(project):
    root, _ = project
    panel = read_text(root / "01_data/processed/BRFV_panel_firmyear_analysis.csv")
    scores = read_text(root / "01_data/interim/BRFV_scores_firmyear_clean.csv")
    rows = panel.loc[(panel["mrg_source"] == "cusip8") & (panel["bd_count_alt"] != "")].head(50)
    assert len(rows) > 0
    lookup = scores.set_index(["id_cusip8", "t_score_year"])["bd_count"]
    for _, row in rows.iterrows():
        expected = lookup.loc[(row["id_cusip8"], str(int(row["t_score_year"]) + 1))]
        assert float(expected) == float(row["bd_count_alt"])


def test_wrong_year_convention_stops_the_pipeline(tmp_path):
    build_fixture(tmp_path, convention="filing")
    assert run_step("brfv_01_import_scores.py", tmp_path).returncode == 0
    assert run_step("brfv_03_build_compustat.py", tmp_path).returncode == 0
    stopped = run_step("brfv_04_build_panel.py", tmp_path)
    assert stopped.returncode == 3, "a filing-year score file must not pass under the fiscal setting"
    assert not (tmp_path / "01_data/processed/BRFV_panel_firmyear_analysis.csv").exists()


# ------------------------------------------------------------ step 06
def test_planted_coefficient_is_recovered(project):
    root, truth = project
    tidy = pd.read_csv(root / "03_output/tables/BRFV_T09_baseline_industry_year_fe_tidy.csv")
    b1 = tidy.loc[(tidy["model"] == "B1") & (tidy["term"] == "bd_count_lag")].iloc[0]
    assert b1["coef"] == pytest.approx(truth["beta_count"], abs=0.07)
    assert b1["p"] < 0.01
    firm = pd.read_csv(root / "03_output/tables/BRFV_T10_firm_fe_tidy.csv")
    f1 = firm.loc[(firm["model"] == "F1") & (firm["term"] == "bd_count_lag")].iloc[0]
    assert f1["coef"] == pytest.approx(truth["beta_count"], abs=0.10)


def test_fixed_effects_match_dummy_variable_ols(project):
    """Independent check of the estimator: explicit dummies and a hand-built cluster-robust variance."""
    root, _ = project
    sys.path.insert(0, str(CODE_DIR))
    os.environ["BRFV_ROOT"] = str(root)
    import brfv_00_config as cfg

    panel = pd.read_csv(root / "01_data/processed/BRFV_panel_firmyear_analysis.csv", dtype={"id_gvkey": str})
    regressors = ["bd_count_lag"] + cfg.CONTROLS
    y = panel["dv_tobin_q_w"].to_numpy(float)
    x = panel[regressors].to_numpy(float)
    dummies = pd.get_dummies(panel["fe_ind_year"]).to_numpy(float)
    design = np.hstack([x, dummies])
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    residual = y - design @ beta
    # Frisch-Waugh: partial the dummies out of X, then the sandwich on the within-transformed X.
    x_within = x - dummies @ np.linalg.lstsq(dummies, x, rcond=None)[0]
    bread = np.linalg.inv(x_within.T @ x_within)
    meat = np.zeros((x.shape[1], x.shape[1]))
    for _, index in panel.groupby("id_gvkey").indices.items():
        score = x_within[index].T @ residual[index]
        meat += np.outer(score, score)
    clusters = panel["id_gvkey"].nunique()
    se_plain = np.sqrt(np.diag(bread @ meat @ bread) * clusters / (clusters - 1))

    tidy = pd.read_csv(root / "03_output/tables/BRFV_T09_baseline_industry_year_fe_tidy.csv")
    b1 = tidy.loc[tidy["model"] == "B1"].set_index("term")
    for position, name in enumerate(regressors):
        assert b1.loc[name, "coef"] == pytest.approx(beta[position], abs=1e-7)
    assert b1.loc["bd_count_lag", "se"] == pytest.approx(se_plain[0], rel=0.03)


def test_every_output_is_written(project):
    root, _ = project
    tables = root / "03_output/tables"
    for number, stem in ((1, "scores_by_year"), (2, "score_persistence"), (3, "year_alignment_test"),
                         (4, "sample_attrition"), (5, "summary_statistics"), (6, "means_by_disclosure"),
                         (7, "correlations"), (8, "industry_distribution"), (9, "baseline_industry_year_fe"),
                         (10, "firm_fe"), (11, "industry_exposure"), (12, "after_kunming_declaration"),
                         (13, "robustness")):
        assert (tables / f"BRFV_T{number:02d}_{stem}.csv").exists(), stem
        assert (tables / f"BRFV_T{number:02d}_{stem}.md").exists(), stem
    robustness = pd.read_csv(tables / "BRFV_T13_robustness.csv")
    assert robustness["check"].str.startswith("R9").any(), "the placebo regression must be present"
    assert (root / "03_output/logs/BRFV_run_manifest_test.json").exists()


# ------------------------------------------------------- real score file
REAL_SCORES = CODE_DIR.parent / "01_data/raw/giglio/10k_biodiversity_scores_2024.csv"
REAL_ZIP = list(CODE_DIR.parent.glob("BRFV_giglio_raw_*.zip")) + list((CODE_DIR.parent / "01_data/raw").glob("**/BRFV_giglio_raw_*.zip"))


@pytest.mark.skipif(not REAL_SCORES.exists() and not REAL_ZIP, reason="real score file not in the project yet")
def test_real_score_file_reproduces_recorded_counts():
    """Step 01 on the real file must reproduce the counts recorded on 18 November 2026."""
    result = run_step("brfv_01_import_scores.py", CODE_DIR.parent, {"BRFV_RUN_ID": "realcheck"})
    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-3000:]
    assert "comparison with recorded values: match" in result.stdout
