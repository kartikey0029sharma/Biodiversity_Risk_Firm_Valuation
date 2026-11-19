"""BRFV step 08: LaTeX tables, key numbers and figures for the manuscript draft.

Project : Biodiversity Risk Disclosure and Firm Valuation (BRFV)
Input   : 03_output/tables/BRFV_T*.csv, 03_output/figures/BRFV_F0*.png,
          01_data/interim/BRFV_industry_exposure_gics4.csv
Output  : in the current draft folder, 04_manuscript/<DRAFT_CURRENT of brfv_00_config.py>
          tables/*.tex   one tabular per table
          numbers.tex    macros for the numbers quoted in the text
          figures/       copies of the figures and the sample flow chart
          03_output/figures/BRFV_F03_coefficients_main.png
Rule    : the draft never types a result by hand. Tables are read with \\input and
          numbers in the text are macros from numbers.tex, so a rerun of the
          pipeline updates the manuscript.
"""
from __future__ import annotations

import re
import shutil
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import brfv_00_config as cfg
import brfv_utils as u

log = u.get_logger("brfv_08_make_latex_assets")

DIR_DRAFT = cfg.DIR_DRAFT
DIR_TEX_TABLES = DIR_DRAFT / "tables"
DIR_TEX_FIGURES = DIR_DRAFT / "figures"

BLUE, ORANGE, INK, QUIET, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e3e2de"

LABELS = {
    "dv_tobin_q_w": "Tobin's Q", "dv_ln_tobin_q_w": "Log of Tobin's Q",
    "bd_count_lag": "Count", "bd_negative_lag": "Negative", "bd_regulation_lag": "Regulation",
    "ix_count_high": r"Count $\times$ High", "ix_negative_high": r"Negative $\times$ High",
    "ix_regulation_high": r"Regulation $\times$ High",
    "ix_count_post": r"Count $\times$ Post", "ix_negative_post": r"Negative $\times$ Post",
    "ix_regulation_post": r"Regulation $\times$ Post",
    "ctl_size_w": "Size", "ctl_leverage_w": "Leverage", "ctl_roa_w": "Profitability",
    "ctl_tangibility_w": "Tangibility", "ctl_sales_growth_w": "Sales growth", "ctl_rd_w": r"R\&D intensity",
    "ctl_capex_w": "Capital expenditure", "ctl_cash_w": "Cash holdings", "ctl_rd_missing": r"R\&D missing",
    "ctl_dividend": "Dividend payer", "ind_bio_survey_avg": "Industry exposure score",
    "ind_bio_high": "High exposure industry",
}
GICS = {
    "1010": "Energy", "1510": "Materials", "2010": "Capital Goods", "2020": "Commercial and Professional Services",
    "2030": "Transportation", "2510": "Automobiles and Components", "2520": "Consumer Durables and Apparel",
    "2530": "Consumer Services", "2550": "Retailing", "3010": "Food and Staples Retailing",
    "3020": "Food, Beverage and Tobacco", "3030": "Household and Personal Products",
    "3510": "Health Care Equipment and Services", "3520": "Pharmaceuticals, Biotechnology and Life Sciences",
    "4010": "Banks", "4020": "Diversified Financials", "4030": "Insurance", "4510": "Software and Services",
    "4520": "Technology Hardware and Equipment", "4530": "Semiconductors and Semiconductor Equipment",
    "5010": "Telecommunication Services", "5020": "Media and Entertainment", "5510": "Utilities", "6010": "Real Estate",
    "6020": "Real Estate Management and Development",
}
CHECKS = {
    "R1": "R1 Log of Tobin's Q", "R2": "R2 Industry-adjusted Q with year effects", "R3": "R3 Utilities excluded",
    "R4": "R4 Fiscal year 2020 excluded", "R5": "R5 December year ends only", "R6": "R6 CUSIP matches only",
    "R7": "R7 Disclosing firms only, firm and year effects", "R8": "R8 Clustered by industry group",
    "R9": "R9 Placebo with the score two years ahead", "R10": "R10 Score of the next score year",
}
NUMBER = re.compile(r"^\(?(-?\d+\.\d+)\)?(\**)$")


# ---------------------------------------------------------------- helpers
def read(stem: str) -> pd.DataFrame:
    return pd.read_csv(cfg.DIR_TABLES / f"{stem}.csv", dtype=str, keep_default_na=False)


def escape(text: str) -> str:
    return text.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_").replace("#", r"\#")


def minus(value: str) -> str:
    return "$-$" + value[1:] if value.startswith("-") else value


def num(value, digits: int = 3) -> str:
    return minus(f"{float(value):.{digits}f}")


def whole(value) -> str:
    return f"{int(round(float(str(value).replace(',', '')))):,}"


def stars(p: float) -> str:
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""


def write(name: str, lines: list[str]) -> None:
    (DIR_TEX_TABLES / f"{name}.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def tabular(spec: str, head: list[str], body: list[str], foot: list[str] | None = None) -> list[str]:
    lines = [rf"\begin{{tabular}}{{{spec}}}", r"\toprule"] + head + [r"\midrule"] + body
    if foot:
        lines += [r"\midrule"] + foot
    return lines + [r"\bottomrule", r"\end{tabular}"]


# ------------------------------------------------------ regression tables
def regression_cell(text: str) -> str:
    text = text.strip()
    match = NUMBER.match(text)
    if not match:
        return escape(text)
    value = num(match.group(1))
    if text.startswith("("):
        return f"({value})"
    return value + (f"$^{{{match.group(2)}}}$" if match.group(2) else "")


def regression_table(stem: str, name: str) -> None:
    table = read(stem)
    models = [c for c in table.columns if c != "term"]
    body, foot = [], []
    for _, row in table.iterrows():
        term, cells = row["term"], [row[m] for m in models]
        if term == "Fixed effects":
            foot.append(r"Industry group $\times$ year effects & " + " & ".join("Yes" if "industry" in c else "No" for c in cells) + r" \\")
            foot.append("Firm and year effects & " + " & ".join("Yes" if "firm" in c else "No" for c in cells) + r" \\")
        elif term == "Controls":
            foot.append("Controls & " + " & ".join("Yes" if c == "yes" else "No" for c in cells) + r" \\")
        elif term in ("Firm-years", "Firms"):
            foot.append(f"{term} & " + " & ".join(cells) + r" \\")
        elif term in ("R-squared", "Within R-squared"):
            foot.append(term.replace("R-squared", "$R^2$") + " & " + " & ".join(cells) + r" \\")
        else:
            label = LABELS.get(term, escape(term)) if term else ""
            body.append(f"{label} & " + " & ".join(regression_cell(c) for c in cells) + r" \\")
    head = [" & " + " & ".join(f"({i})" for i in range(1, len(models) + 1)) + r" \\",
            "Model & " + " & ".join(models) + r" \\"]
    write(name, tabular("l" + "c" * len(models), head, body, foot))


def robustness_table() -> None:
    table = read("BRFV_T13_robustness")
    table["code"] = table["check"].str.split().str[0]
    table["score"] = table["term"].map(lambda t: "Count" if "count" in t else "Negative" if "negative" in t else "Regulation")
    body = []
    for code in list(dict.fromkeys(table["code"])):
        part = table.loc[table["code"] == code].set_index("score")
        coefs, errors = [], []
        for score in ("Count", "Negative", "Regulation"):
            if score in part.index:
                row = part.loc[score]
                coefs.append(num(row["coef"]) + (f"$^{{{stars(float(row['p']))}}}$" if stars(float(row["p"])) else ""))
                errors.append(f"({num(row['se'])})")
            else:
                coefs.append(""), errors.append("")
        first = part.iloc[0]
        body.append(f"{escape(CHECKS.get(code, code))} & " + " & ".join(coefs) + f" & {whole(first['n_obs'])} & {whole(first['n_firms'])}" + r" \\")
        body.append(" & " + " & ".join(errors) + r" & & \\")
    head = [r"Check & Count & Negative & Regulation & Firm-years & Firms \\"]
    write("tab_robustness", tabular("lccccc", head, body))


# ------------------------------------------------------ descriptive tables
def scores_by_period() -> None:
    table = read("BRFV_T01_scores_by_year").apply(pd.to_numeric, errors="coerce")
    body = []
    for label, first, last in (("2001 to 2007", 2001, 2007), ("2008 to 2014", 2008, 2014), ("2015 to 2023", 2015, 2023),
                               ("2024", 2024, 2024), ("2001 to 2024", 2001, 2024)):
        part = table.loc[table["t_score_year"].between(first, last)]
        n, count, regulation = part["n_valid"].sum(), part["n_count1"].sum(), part["n_regulation1"].sum()
        body.append(f"{label} & {whole(n)} & {whole(count)} & {100 * count / n:.2f} & {whole(regulation)} & {100 * regulation / n:.2f} & "
                    f"{whole(part['n_negative_pos'].sum())} & {whole(part['n_negative_neg'].sum())}" + r" \\")
    body.insert(4, r"\midrule")
    head = [r"Score years & Firm-years & Count $=1$ & Share (\%) & Regulation $=1$ & Share (\%) & Negative $>0$ & Negative $<0$ \\"]
    write("tab_scores_by_period", tabular("lrrrrrrr", head, body))


def persistence() -> None:
    table = read("BRFV_T02_score_persistence")
    body = []
    for _, row in table.iterrows():
        if row["window"] in ("2001-2023", "2014-2023", "2015-2023"):
            body.append(f"{row['window'].replace('-', ' to ')} & {whole(row['n_firms'])} & {whole(row['n_firm_years'])} & {whole(row['firms_ever'])} & "
                        f"{whole(row['firms_always'])} & {whole(row['firms_switch'])} & {float(row['pct_stay_1']):.1f} & {float(row['pct_enter_1']):.2f}" + r" \\")
    head = [r"Score years & Firms & Firm-years & Ever $=1$ & Always $=1$ & Changing & Stay at 1 (\%) & Move 0 to 1 (\%) \\"]
    write("tab_persistence", tabular("lrrrrrrr", head, body))


def industry() -> None:
    survey = pd.read_csv(cfg.INT_INDUSTRY, dtype=str, keep_default_na=False)
    sample = read("BRFV_T08_industry_distribution").set_index("ind_gics4")
    survey["avg"] = pd.to_numeric(survey["ind_bio_survey_avg"])
    body = []
    for _, row in survey.sort_values("avg", ascending=False, kind="stable").iterrows():
        code = row["ind_gics4"]
        group = "Financial" if row["ind_is_financial"] == "1" else "High" if row["ind_bio_high"] == "1" else "Other"
        if code in sample.index:
            s = sample.loc[code]
            tail = f"{whole(s['n_firm_years'])} & {float(s['pct_count1']):.1f} & {float(s['mean_tobin_q']):.2f}"
        else:
            tail = " &  & "
        body.append(f"{code} & {escape(GICS.get(code, code))} & {float(row['ind_bio_survey_trans']):.3f} & {float(row['ind_bio_survey_phys']):.3f} & "
                    f"{row['avg']:.3f} & {group} & {tail}" + r" \\")
    for code in [c for c in sample.index if c not in set(survey["ind_gics4"])]:
        row = sample.loc[code]
        body.append(f"{code} & {escape(GICS.get(code, code))} &  &  &  & No score & {whole(row['n_firm_years'])} & "
                    f"{float(row['pct_count1']):.1f} & {float(row['mean_tobin_q']):.2f}" + r" \\")
    head = [r" & & \multicolumn{3}{c}{Survey exposure score} & & \multicolumn{3}{c}{Regression sample} \\",
            r"\cmidrule(lr){3-5}\cmidrule(lr){7-9}",
            r"GICS & Industry group & Transition & Physical & Average & Group & Firm-years & Count $=1$ (\%) & Mean Q \\"]
    write("tab_industry", tabular("llrrrlrrr", head, body))


def attrition() -> pd.DataFrame:
    table = read("BRFV_T04_sample_attrition")
    names = ["Compustat firm-years for fiscal years 2015 to 2024", "Incorporated in the United States", "Reporting in US dollars",
             "Non-financial firms", "Total assets, book equity and market value available", "GICS industry group available",
             "Matched to a 10-K biodiversity score of the previous year", "All control variables available"]
    assert len(table) == len(names), "the attrition table has changed: update the step names"
    table["label"] = names
    body = [f"{r['label']} & {whole(r['n_firm_years'])} & {whole(r['n_firms'])} & {whole(r['dropped_firm_years']) if int(r['dropped_firm_years']) else ''}" + r" \\"
            for _, r in table.iterrows()]
    write("tab_attrition", tabular("lrrr", [r"Step & Firm-years & Firms & Firm-years removed \\"], body))
    return table


def summary() -> None:
    table = read("BRFV_T05_summary_statistics")
    body = [f"{LABELS.get(r['variable'], escape(r['variable']))} & {whole(r['n'])} & " + " & ".join(num(r[c]) for c in ("mean", "sd", "min", "p25", "median", "p75", "max")) + r" \\"
            for _, r in table.iterrows()]
    write("tab_summary", tabular("lrrrrrrrr", [r"Variable & N & Mean & SD & Min & P25 & Median & P75 & Max \\"], body))


def means() -> None:
    table = read("BRFV_T06_means_by_disclosure")
    body = [f"{LABELS.get(r['variable'], escape(r['variable']))} & {num(r['mean_count1'])} & {num(r['mean_count0'])} & {num(r['difference'])} & {num(r['t_unadjusted'], 2)}" + r" \\"
            for _, r in table.iterrows()]
    first = table.iloc[0]
    foot = [f"Firm-years & {whole(first['n_count1'])} & {whole(first['n_count0'])} & & " + r"\\"]
    write("tab_means", tabular("lrrrr", [r"Variable & Count $=1$ & Count $=0$ & Difference & $t$ \\"], body, foot))


def variation() -> None:
    table = read("BRFV_T14_identifying_variation")
    body = [f"{LABELS.get(r['score'], r['score'])} & {whole(r['n_firm_years_not_zero'])} & {whole(r['n_firms_ever_not_zero'])} & {whole(r['n_firms_changing'])}" + r" \\"
            for _, r in table.iterrows()]
    write("tab_variation", tabular("lrrr", [r"Score & Firm-years with a score other than zero & Firms with such a firm-year & Firms whose score changes \\"], body))


def alignment() -> None:
    table = read("BRFV_T03_year_alignment_test")
    names = ["First score year equals the first priced fiscal year", "First score year is one year later",
             "Last score year equals the last priced fiscal year", "Last score year is one year later",
             "First row in the first priced fiscal year", "of which rows with a score other than zero",
             "The same firms one year later", "of which rows with a score other than zero",
             "Row one year after the last priced fiscal year", "of which rows with a score other than zero",
             "The same firms one year earlier", "of which rows with a score other than zero"]
    assert len(table) == len(names) + 1, "the timing table has changed: update the row names"
    body = [(r"\quad " if n.startswith("of which") else "") + f"{n} & {whole(v)}" + r" \\" for n, v in zip(names, table["n_firms"])]
    body.insert(4, r"\midrule")
    write("tab_alignment", tabular("lr", [r"Pattern among firms with a December year end & Firms \\"], body))


def correlations() -> None:
    table = read("BRFV_T07_correlations")
    variables = list(table["variable"])
    body = []
    for i, (_, row) in enumerate(table.iterrows(), start=1):
        cells = [num(row[v], 2) if j <= i else "" for j, v in enumerate(variables, start=1)]
        body.append(f"({i}) {LABELS.get(row['variable'], escape(row['variable']))} & " + " & ".join(cells) + r" \\")
    head = [" & " + " & ".join(f"({i})" for i in range(1, len(variables) + 1)) + r" \\"]
    write("tab_correlations", tabular("l" + "r" * len(variables), head, body))


# ---------------------------------------------------------------- figures
def coefficient_figure() -> None:
    rows = []
    for stem, model, name in (("BRFV_T09_baseline_industry_year_fe_tidy", "B4", "Industry group by year effects"),
                              ("BRFV_T10_firm_fe_tidy", "F4", "Firm and year effects")):
        tidy = pd.read_csv(cfg.DIR_TABLES / f"{stem}.csv")
        part = tidy.loc[(tidy["model"] == model) & tidy["term"].isin(cfg.SCORES)].assign(series=name)
        rows.append(part)
    data = pd.concat(rows)
    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=200)
    order = list(reversed(cfg.SCORES))
    for offset, (name, colour) in zip((0.14, -0.14), (("Industry group by year effects", BLUE), ("Firm and year effects", ORANGE))):
        part = data.loc[data["series"] == name].set_index("term").loc[order]
        ys = [i + offset for i in range(len(order))]
        ax.errorbar(part["coef"], ys, xerr=1.96 * part["se"], fmt="o", color=colour, ecolor=colour, elinewidth=2,
                    capsize=0, markersize=6, label=name)
        for y, (_, r) in zip(ys, part.iterrows()):
            ax.text(r["coef"] + 1.96 * r["se"] + 0.012, y, f"{r['coef']:.3f}", va="center", ha="left", fontsize=8.5, color=INK)
    ax.axvline(0, color=QUIET, linewidth=1)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([LABELS[s] for s in order], color=INK)
    ax.set_xlabel("Change in Tobin's Q for a one-unit change in the score, with 95 per cent confidence interval", color=QUIET, fontsize=8.5)
    ax.tick_params(axis="x", colors=QUIET, labelsize=8.5)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.set_ylim(-0.6, len(order) - 0.4)
    ax.legend(frameon=False, fontsize=8.5, loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=2)
    fig.tight_layout()
    fig.savefig(cfg.DIR_FIGURES / "BRFV_F03_coefficients_main.png", facecolor="white")
    plt.close(fig)


def sample_flow(table: pd.DataFrame) -> None:
    lines = [r"\begin{tikzpicture}[node distance=5.5mm, every node/.style={font=\small},",
             r"  stage/.style={draw=black!55, fill=blue!6, rounded corners=2pt, text width=9.6cm, align=left, inner sep=5pt, execute at begin node={\hyphenpenalty=10000\exhyphenpenalty=10000}},",
             r"  removed/.style={text width=3.9cm, align=left, text=black!70, font=\footnotesize},",
             r"  flow/.style={-{Latex[length=2.2mm]}, draw=black!60}]"]
    for i, (_, r) in enumerate(table.iterrows()):
        position = "" if i == 0 else f"[below=of s{i - 1}]"
        lines.append(rf"\node[stage] (s{i}) {position} {{{r['label']}\\ \textbf{{{whole(r['n_firm_years'])}}} firm-years, {whole(r['n_firms'])} firms}};")
        if i > 0:
            lines.append(rf"\draw[flow] (s{i - 1}) -- (s{i});")
            lines.append(rf"\node[removed, right=4mm of s{i}] {{{whole(r['dropped_firm_years'])} firm-years removed}};")
    lines.append(r"\end{tikzpicture}")
    (DIR_TEX_FIGURES / "fig_sample_flow.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- numbers
def numbers(table_attrition: pd.DataFrame) -> None:
    macros: dict[str, str] = {}

    def put(name: str, value: str) -> None:
        assert name.isalpha(), name
        macros[name] = value

    def coefficient(prefix: str, tidy: pd.DataFrame, model: str, term: str) -> None:
        row = tidy.loc[(tidy["model"] == model) & (tidy["term"] == term)].iloc[0]
        put("coef" + prefix, rf"\ensuremath{{{float(row['coef']):.3f}}}")
        put("se" + prefix, f"{float(row['se']):.3f}")
        put("pval" + prefix, f"{float(row['p']):.3f}")

    a = table_attrition
    for name, i in (("nStart", 0), ("nUS", 1), ("nNonFin", 3), ("nValued", 4), ("nGics", 5), ("nMatched", 6), ("nFinal", 7)):
        put(name, whole(a.iloc[i]["n_firm_years"]))
    put("nFirmsMatched", whole(a.iloc[6]["n_firms"]))
    put("nFirmsFinal", whole(a.iloc[7]["n_firms"]))
    s = read("BRFV_T05_summary_statistics").set_index("variable")
    put("meanQ", f"{float(s.loc['dv_tobin_q_w', 'mean']):.2f}")
    put("medianQ", f"{float(s.loc['dv_tobin_q_w', 'median']):.2f}")
    put("sdQ", f"{float(s.loc['dv_tobin_q_w', 'sd']):.2f}")
    put("maxQ", f"{float(s.loc['dv_tobin_q_w', 'max']):.2f}")
    put("pctCount", f"{100 * float(s.loc['bd_count_lag', 'mean']):.1f}")
    put("pctReg", f"{100 * float(s.loc['bd_regulation_lag', 'mean']):.1f}")
    put("pctHigh", f"{100 * float(s.loc['ind_bio_high', 'mean']):.1f}")
    m = read("BRFV_T06_means_by_disclosure").set_index("variable")
    put("meanQOne", f"{float(m.loc['dv_tobin_q_w', 'mean_count1']):.2f}")
    put("meanQZero", f"{float(m.loc['dv_tobin_q_w', 'mean_count0']):.2f}")
    put("nCountOne", whole(m.loc["dv_tobin_q_w", "n_count1"]))
    put("nCountZero", whole(m.loc["dv_tobin_q_w", "n_count0"]))
    put("tangOne", f"{float(m.loc['ctl_tangibility_w', 'mean_count1']):.2f}")
    put("tangZero", f"{float(m.loc['ctl_tangibility_w', 'mean_count0']):.2f}")
    v = read("BRFV_T14_identifying_variation").set_index("score")
    for prefix, score in (("Count", "bd_count_lag"), ("Neg", "bd_negative_lag"), ("Reg", "bd_regulation_lag")):
        put("nNonzero" + prefix, whole(v.loc[score, "n_firm_years_not_zero"]))
        put("nEver" + prefix, whole(v.loc[score, "n_firms_ever_not_zero"]))
        put("nChange" + prefix, whole(v.loc[score, "n_firms_changing"]))
    b = pd.read_csv(cfg.DIR_TABLES / "BRFV_T09_baseline_industry_year_fe_tidy.csv")
    f = pd.read_csv(cfg.DIR_TABLES / "BRFV_T10_firm_fe_tidy.csv")
    x = pd.read_csv(cfg.DIR_TABLES / "BRFV_T11_industry_exposure_tidy.csv")
    e = pd.read_csv(cfg.DIR_TABLES / "BRFV_T12_after_kunming_declaration_tidy.csv")
    for prefix, score in (("Count", "bd_count_lag"), ("Neg", "bd_negative_lag"), ("Reg", "bd_regulation_lag")):
        number = {"Count": 1, "Neg": 2, "Reg": 3}[prefix]
        short = {"Count": "count", "Neg": "negative", "Reg": "regulation"}[prefix]
        coefficient("B" + prefix, b, f"B{number}", score)
        coefficient("BAll" + prefix, b, "B4", score)
        coefficient("F" + prefix, f, f"F{number}", score)
        coefficient("FAll" + prefix, f, "F4", score)
        coefficient("X" + prefix, x, f"X{number}", f"ix_{short}_high")
        coefficient("E" + prefix, e, f"E{number}", f"ix_{short}_post")
        coefficient("EF" + prefix, e, f"EF{number}", f"ix_{short}_post")
        coefficient("ED" + prefix, e, f"ED{number}", f"ix_{short}_post")
    put("nObsB", whole(b.loc[b["model"] == "B4", "n_obs"].iloc[0]))
    put("nObsF", whole(f.loc[f["model"] == "F4", "n_obs"].iloc[0]))
    put("rsqB", f"{float(b.loc[b['model'] == 'B4', 'r2'].iloc[0]):.3f}")
    put("rsqF", f"{float(f.loc[f['model'] == 'F4', 'r2'].iloc[0]):.3f}")
    r = read("BRFV_T13_robustness")
    r["code"] = r["check"].str.split().str[0]
    words = {"R7": "Seven", "R9": "Nine", "R10": "Ten", "R1": "One"}
    for code, word in words.items():
        for prefix, key in (("Count", "count"), ("Neg", "negative"), ("Reg", "regulation")):
            row = r.loc[(r["code"] == code) & r["term"].str.contains(key)]
            if len(row):
                put(f"coefR{word}{prefix}", rf"\ensuremath{{{float(row.iloc[0]['coef']):.3f}}}")
                put(f"seR{word}{prefix}", f"{float(row.iloc[0]['se']):.3f}")
                put(f"pvalR{word}{prefix}", f"{float(row.iloc[0]['p']):.3f}")
    seven = r.loc[r["code"] == "R7"].iloc[0]
    put("nObsRSeven", whole(seven["n_obs"]))
    put("nFirmsRSeven", whole(seven["n_firms"]))
    six, five = r.loc[r["code"] == "R6"].iloc[0], r.loc[r["code"] == "R5"].iloc[0]
    n_main = float(b.loc[b["model"] == "B4", "n_obs"].iloc[0])
    put("pctCusip", f"{100 * float(six['n_obs']) / n_main:.0f}")
    put("pctDecember", f"{100 * float(five['n_obs']) / n_main:.0f}")
    put("nObsED", whole(e.loc[e["model"] == "ED3", "n_obs"].iloc[0]))
    effect = abs(float(f.loc[(f["model"] == "F4") & (f["term"] == "bd_negative_lag"), "coef"].iloc[0]))
    put("effNegMean", f"{100 * effect / float(s.loc['dv_tobin_q_w', 'mean']):.1f}")
    put("effNegDisc", f"{100 * effect / float(m.loc['dv_tobin_q_w', 'mean_count1']):.1f}")
    d = read("BRFV_T08_industry_distribution")
    d["n"] = pd.to_numeric(d["n_firm_years"])
    d["k"] = (pd.to_numeric(d["pct_count1"]) * d["n"] / 100).round()
    total = d["k"].sum()
    put("pctCountHigh", f"{100 * d.loc[d['high_exposure'].isin(['1.0', '1']), 'k'].sum() / total:.0f}")
    for name, code in (("pctEnergy", "1010"), ("pctUtilities", "5510"), ("pctMaterials", "1510")):
        put(name, f"{float(d.loc[d['ind_gics4'] == code, 'pct_count1'].iloc[0]):.1f}")
    put("pctTopThree", f"{100 * d.loc[d['ind_gics4'].isin(['1010', '5510', '1510']), 'k'].sum() / total:.0f}")
    put("pctMatched", f"{100 * float(a.iloc[6]['n_firm_years']) / float(a.iloc[5]['n_firm_years']):.0f}")
    t = read("BRFV_T03_year_alignment_test")["n_firms"].tolist()
    for name, i in (("entryZero", 0), ("entryOne", 1), ("exitZero", 2), ("exitOne", 3), ("nFirstRows", 4), ("nFirstFilled", 5),
                    ("nFirstNext", 6), ("nFirstNextFilled", 7), ("nTrailRows", 8), ("nTrailFilled", 9), ("nTrailBefore", 10),
                    ("nTrailBeforeFilled", 11)):
        put(name, whole(t[i]))
    lines = ["% Written by 02_code/brfv_08_make_latex_assets.py. Do not edit by hand."]
    lines += [rf"\newcommand{{\{name}}}{{{value}}}" for name, value in macros.items()]
    (DIR_DRAFT / "numbers.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    log.info("numbers.tex written: %d macros", len(macros))


# ------------------------------------------------------------------- main
def main() -> int:
    u.ensure_dirs()
    needed = cfg.DIR_TABLES / "BRFV_T13_robustness.csv"
    if not needed.exists():
        log.error("tables missing: run steps 01 to 07 first")
        return 2
    DIR_TEX_TABLES.mkdir(parents=True, exist_ok=True)
    DIR_TEX_FIGURES.mkdir(parents=True, exist_ok=True)
    scores_by_period(); persistence(); industry()
    table_attrition = attrition()
    summary(); means(); variation(); alignment(); correlations()
    regression_table("BRFV_T09_baseline_industry_year_fe", "tab_baseline")
    regression_table("BRFV_T10_firm_fe", "tab_firm_effects")
    regression_table("BRFV_T11_industry_exposure", "tab_exposure")
    regression_table("BRFV_T12_after_kunming_declaration", "tab_event")
    robustness_table()
    coefficient_figure()
    sample_flow(table_attrition)
    numbers(table_attrition)
    for figure in sorted(cfg.DIR_FIGURES.glob("BRFV_F0*.png")):
        shutil.copy2(figure, DIR_TEX_FIGURES / figure.name)
    log.info("LaTeX tables and figures written to %s", DIR_DRAFT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
