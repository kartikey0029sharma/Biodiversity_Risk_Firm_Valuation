"""BRFV step 02 (run by hand): pull the Compustat extract from WRDS.

Project : Biodiversity Risk Disclosure and Firm Valuation (BRFV)
Output  : 01_data/raw/compustat/BRFV_compustat_funda_raw.csv
          01_data/raw/compustat/BRFV_compustat_funda_raw_query.txt
Needs   : your own WRDS account with Compustat North America access, and
          `pip install wrds`. The script asks for the user name and password;
          nothing is stored in this project.
Status  : written from the standard WRDS table and column names. It has NOT
          been run inside this project, because no WRDS login was available
          when it was written. If a column is refused, compare the name with
          the WRDS variable list and correct the query below.
Licence : Compustat data are licensed to your institution. Keep the extract
          on your own machine and never publish it (see .gitignore).

The same extract can be made with the WRDS web query form; the steps are in
05_docs/BRFV_wrds_query_spec.md.
"""
from __future__ import annotations

import sys
from datetime import datetime

import brfv_00_config as cfg
import brfv_utils as u

log = u.get_logger("brfv_02_pull_compustat_wrds")

# Two years before the first Tobin's Q year (for sales growth and the listing
# test) and one year after the last.
FIRST_FYEAR = cfg.Q_FYEAR_MIN - 2
LAST_FYEAR = cfg.Q_FYEAR_MAX + 1

SQL_FUNDA = f"""
select gvkey, datadate, fyear, fyr, tic, cusip, conm, curcd, exchg, costat,
       indfmt, datafmt, popsrc, consol,
       at, ceq, seq, lt, csho, prcc_f, dltt, dlc, oibdp, ib, ppent, sale,
       xrd, capx, che, dvc, sich
from comp.funda
where indfmt = 'INDL' and datafmt = 'STD' and popsrc = 'D' and consol = 'C'
  and fyear between {FIRST_FYEAR} and {LAST_FYEAR}
"""

SQL_COMPANY = """
select gvkey, sic, gsector, ggroup, gind, gsubind, fic, loc, ipodate
from comp.company
"""


def main() -> int:
    try:
        import wrds
    except ImportError:
        log.error("the wrds package is not installed: pip install wrds")
        return 2
    u.ensure_dirs()
    connection = wrds.Connection()
    try:
        funda = connection.raw_sql(SQL_FUNDA, date_cols=["datadate"])
        company = connection.raw_sql(SQL_COMPANY)
    finally:
        connection.close()
    extract = funda.merge(company, on="gvkey", how="left", validate="many_to_one")
    extract.to_csv(cfg.RAW_COMPUSTAT, index=False)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query_note = (f"Pulled from WRDS on {stamp}\nRows: {len(extract):,}\nFirms: {extract['gvkey'].nunique():,}\n"
                  f"\n-- comp.funda\n{SQL_FUNDA}\n-- comp.company\n{SQL_COMPANY}")
    cfg.RAW_COMPUSTAT.with_name("BRFV_compustat_funda_raw_query.txt").write_text(query_note, encoding="utf-8")
    log.info("extract written: %s rows, %s firms, sha256 %s", f"{len(extract):,}",
             f"{extract['gvkey'].nunique():,}", u.sha256_of(cfg.RAW_COMPUSTAT))
    log.info("add this file and its hash to 05_docs/BRFV_data_log.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
