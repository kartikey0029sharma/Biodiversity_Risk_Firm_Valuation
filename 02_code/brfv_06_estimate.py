"""BRFV step 06: main regressions of Tobin's Q on the 10-K biodiversity scores.

Project : Biodiversity Risk Disclosure and Firm Valuation (BRFV)
Input   : 01_data/processed/BRFV_panel_firmyear_analysis.csv
Output  : 03_output/tables/BRFV_T09_baseline_industry_year_fe.(csv|md)
          03_output/tables/BRFV_T10_firm_fe.(csv|md)
          03_output/tables/BRFV_T11_industry_exposure.(csv|md)
          03_output/tables/BRFV_T12_after_kunming_declaration.(csv|md)
          each with a companion *_tidy.csv holding every coefficient
Method  : OLS with high-dimensional fixed effects (pyfixest.feols), standard
          errors clustered by firm. The list of models below was fixed before
          any firm-level data were merged; add a model only with a dated note
          in 05_docs/BRFV_ai_use_log.md or the change log.
"""
from __future__ import annotations

import sys
import warnings

import pandas as pd

import brfv_00_config as cfg
import brfv_utils as u
from brfv_05_descriptives import load_panel

log = u.get_logger("brfv_06_estimate")

FE_INDUSTRY_YEAR = cfg.FE_IND_YEAR
FE_FIRM_YEAR = f"{cfg.ID_FIRM} + {cfg.T_FYEAR}"
SHORT = {"bd_count_lag": "count", "bd_negative_lag": "negative", "bd_regulation_lag": "regulation"}
FE_LABELS = {FE_INDUSTRY_YEAR: "industry group x year", FE_FIRM_YEAR: "firm, year", cfg.T_FYEAR: "year"}


def fit_model(panel: pd.DataFrame, label: str, dependent: str, regressors: list[str], fixed_effects: str,
              cluster: str = cfg.CLUSTER) -> pd.DataFrame:
    """Estimate one model and return its coefficients in long form."""
    import pyfixest as pf

    used = panel.dropna(subset=[dependent] + regressors)
    formula = f"{dependent} ~ {' + '.join(regressors)} | {fixed_effects}"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fit = pf.feols(formula, data=used, vcov={"CRV1": cluster})
    tidy = fit.tidy().reset_index()
    tidy = tidy.rename(columns={tidy.columns[0]: "term", "Estimate": "coef", "Std. Error": "se",
                                "t value": "t", "Pr(>|t|)": "p"})[["term", "coef", "se", "t", "p"]]
    tidy.insert(0, "model", label)
    tidy["dep_var"] = dependent
    tidy["fixed_effects"] = fixed_effects
    tidy["cluster"] = cluster
    tidy["n_obs"] = int(fit._N)
    tidy["n_firms"] = int(used[cfg.ID_FIRM].nunique())
    tidy["r2"] = float(fit._r2)
    tidy["r2_within"] = float(fit._r2_within)
    return tidy


def paper_table(tidy: pd.DataFrame, show_terms: list[str]) -> pd.DataFrame:
    """Wide table: one column per model, coefficient with stars and the standard error below it."""
    models = list(dict.fromkeys(tidy["model"]))
    rows = []
    for term in show_terms:
        coefficient_row, error_row = {"term": term}, {"term": ""}
        for model in models:
            hit = tidy.loc[(tidy["model"] == model) & (tidy["term"] == term)]
            if hit.empty:
                coefficient_row[model], error_row[model] = "", ""
            else:
                record = hit.iloc[0]
                coefficient_row[model] = f"{record['coef']:.4f}{u.stars(record['p'])}"
                error_row[model] = f"({record['se']:.4f})"
        rows += [coefficient_row, error_row]
    first = tidy.groupby("model", sort=False).first()
    control_terms = set(cfg.CONTROLS)
    footer = [
        ("Controls", {m: "yes" if control_terms & set(tidy.loc[tidy["model"] == m, "term"]) else "no" for m in models}),
        ("Fixed effects", {m: FE_LABELS.get(first.loc[m, "fixed_effects"], first.loc[m, "fixed_effects"]) for m in models}),
        ("Firm-years", {m: f"{int(first.loc[m, 'n_obs']):,}" for m in models}),
        ("Firms", {m: f"{int(first.loc[m, 'n_firms']):,}" for m in models}),
        ("R-squared", {m: f"{first.loc[m, 'r2']:.3f}" for m in models}),
        ("Within R-squared", {m: f"{first.loc[m, 'r2_within']:.3f}" for m in models}),
    ]
    for name, values in footer:
        rows.append({"term": name, **values})
    return pd.DataFrame(rows, columns=["term"] + models)


def write_models(tidy: pd.DataFrame, stem: str, show_terms: list[str], note: str) -> None:
    tidy.to_csv(cfg.DIR_TABLES / f"{stem}_tidy.csv", index=False)
    u.write_table(paper_table(tidy, show_terms), stem,
                  note=note + " Standard errors clustered by firm in parentheses. * p<0.10, ** p<0.05, *** p<0.01.")


def baseline(panel: pd.DataFrame, fixed_effects: str, prefix: str) -> pd.DataFrame:
    """Each score alone, then the three together, with the full set of controls."""
    models = [fit_model(panel, f"{prefix}0", cfg.DV_MAIN, cfg.CONTROLS, fixed_effects)]
    for number, score in enumerate(cfg.SCORES, start=1):
        models.append(fit_model(panel, f"{prefix}{number}", cfg.DV_MAIN, [score] + cfg.CONTROLS, fixed_effects))
    models.append(fit_model(panel, f"{prefix}4", cfg.DV_MAIN, cfg.SCORES + cfg.CONTROLS, fixed_effects))
    if cfg.CLIMATE_VAR in panel.columns and panel[cfg.CLIMATE_VAR].notna().mean() >= 0.5:
        models.append(fit_model(panel, f"{prefix}5", cfg.DV_MAIN, cfg.SCORES + [cfg.CLIMATE_VAR] + cfg.CONTROLS, fixed_effects))
    return pd.concat(models, ignore_index=True)


def interactions(panel: pd.DataFrame, suffix: str, fixed_effects: str, prefix: str) -> pd.DataFrame:
    """Each score with its interaction term (industry exposure or the period after October 2021)."""
    models = []
    for number, score in enumerate(cfg.SCORES, start=1):
        interaction = f"ix_{SHORT[score]}_{suffix}"
        models.append(fit_model(panel, f"{prefix}{number}", cfg.DV_MAIN, [score, interaction] + cfg.CONTROLS, fixed_effects))
    return pd.concat(models, ignore_index=True)


def main() -> int:
    u.ensure_dirs()
    if not cfg.PROC_PANEL.exists():
        log.error("panel missing: %s. Run step 04 first.", cfg.PROC_PANEL.name)
        return 2
    panel = load_panel()
    log.info("estimating on %s firm-years and %s firms", f"{len(panel):,}", f"{panel[cfg.ID_FIRM].nunique():,}")
    extra = [cfg.CLIMATE_VAR] if cfg.CLIMATE_VAR in panel.columns else []

    t09 = baseline(panel, FE_INDUSTRY_YEAR, "B")
    write_models(t09, "BRFV_T09_baseline_industry_year_fe", cfg.SCORES + extra + cfg.CONTROLS,
                 "Dependent variable: Tobin's Q, winsorised. Industry group by year fixed effects.")

    t10 = baseline(panel, FE_FIRM_YEAR, "F")
    write_models(t10, "BRFV_T10_firm_fe", cfg.SCORES + extra + cfg.CONTROLS,
                 "Dependent variable: Tobin's Q, winsorised. Firm and year fixed effects.")

    exposed = panel.dropna(subset=["ind_bio_high"])
    t11 = interactions(exposed, "high", FE_INDUSTRY_YEAR, "X")  # X = exposure; H1 to H4 are the hypotheses
    high_terms = [x for s in cfg.SCORES for x in (s, f"ix_{SHORT[s]}_high")]
    write_models(t11, "BRFV_T11_industry_exposure", high_terms,
                 "Dependent variable: Tobin's Q, winsorised. ix_*_high is the score times the high-exposure industry flag; "
                 "the flag itself is absorbed by the industry group by year fixed effects.")

    no_transition = panel.loc[panel[cfg.T_FYEAR] != cfg.EVENT_TRANSITION_FYEAR]
    t12 = pd.concat([interactions(panel, "post", FE_INDUSTRY_YEAR, "E"),
                     interactions(panel, "post", FE_FIRM_YEAR, "EF"),
                     interactions(no_transition, "post", FE_INDUSTRY_YEAR, "ED")], ignore_index=True)
    post_terms = [x for s in cfg.SCORES for x in (s, f"ix_{SHORT[s]}_post")]
    write_models(t12, "BRFV_T12_after_kunming_declaration", post_terms,
                 f"Dependent variable: Tobin's Q, winsorised. ix_*_post is the score times an indicator for fiscal years "
                 f"from {cfg.EVENT_FIRST_FYEAR}; the indicator itself is absorbed by the year effects. "
                 "Models E use industry group by year effects, models EF firm and year effects. "
                 f"Models ED repeat models E without fiscal year {cfg.EVENT_TRANSITION_FYEAR}, in which firms with a "
                 "December year end are valued after the declaration although the year counts as before it.")

    headline = t09.loc[(t09["model"] == "B1") & (t09["term"] == "bd_count_lag")].iloc[0]
    log.info("B1 coefficient on bd_count_lag: %.4f (se %.4f, p %.4f, n %s)", headline["coef"], headline["se"],
             headline["p"], f"{int(headline['n_obs']):,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
