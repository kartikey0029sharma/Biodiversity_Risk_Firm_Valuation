"""BRFV step 99: run the whole pipeline in order and record what was run.

Project : Biodiversity Risk Disclosure and Firm Valuation (BRFV)
Usage   : python brfv_99_run_all.py
Output  : every table and figure, plus 03_output/logs/BRFV_run_manifest_<id>.json
Notes   : step 02 (the WRDS pull) is not part of this run; it needs your login.
          The run stops at the first step whose input is missing and says why.
"""
from __future__ import annotations

import importlib
import json
import platform
import sys
from datetime import datetime

import brfv_00_config as cfg
import brfv_utils as u

log = u.get_logger("brfv_99_run_all")

STEPS = [
    "brfv_01_import_scores",
    "brfv_03_build_compustat",
    "brfv_04_build_panel",
    "brfv_05_descriptives",
    "brfv_06_estimate",
    "brfv_07_robustness",
    "brfv_08_make_latex_assets",
]
RETURN_CODES = {0: "done", 2: "stopped: an input file is missing", 3: "stopped: year convention disagrees with the data"}


def package_versions() -> dict:
    versions = {"python": platform.python_version()}
    for name in ("pandas", "numpy", "matplotlib", "pyfixest"):
        try:
            versions[name] = importlib.import_module(name).__version__
        except Exception:  # noqa: BLE001 - a missing package is reported, not fatal here
            versions[name] = "not installed"
    return versions


def input_hashes() -> dict:
    files = [cfg.RAW_SCORES, cfg.RAW_SURVEY, cfg.RAW_HOLDING, cfg.RAW_CDP, cfg.RAW_COMPUSTAT, cfg.RAW_CLIMATE]
    return {p.name: (u.sha256_of(p) if p.exists() else "missing") for p in files}


def main() -> int:
    u.ensure_dirs()
    started = datetime.now()
    results: dict[str, str] = {}
    code = 0
    for name in STEPS:
        log.info("---- %s ----", name)
        code = importlib.import_module(name).main()
        results[name] = RETURN_CODES.get(code, f"stopped with code {code}")
        if code != 0:
            log.warning("%s %s. Later steps were not run.", name, results[name])
            break
    manifest = {
        "run_id": u.RUN_ID,
        "started": started.isoformat(timespec="seconds"),
        "finished": datetime.now().isoformat(timespec="seconds"),
        "project_root": str(cfg.PROJECT_ROOT),
        "steps": results,
        "packages": package_versions(),
        "input_sha256": input_hashes(),
        "settings": {
            "score_year_convention": cfg.SCORE_YEAR_CONVENTION,
            "q_fiscal_years": [cfg.Q_FYEAR_MIN, cfg.Q_FYEAR_MAX],
            "winsor_limits": list(cfg.WINSOR_LIMITS),
            "event_first_fiscal_year": cfg.EVENT_FIRST_FYEAR,
            "high_exposure_quantile": cfg.HIGH_EXPOSURE_QUANTILE,
        },
    }
    path = cfg.DIR_LOGS / f"BRFV_run_manifest_{u.RUN_ID}.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    log.info("manifest written: %s", path.name)
    return code


if __name__ == "__main__":
    sys.exit(main())
