# BRFV raw data: what goes where

Raw files are kept exactly as their source gave them. Nothing in this folder is edited.

| Folder | File | Source | How it gets here |
| --- | --- | --- | --- |
| giglio | 10k_biodiversity_scores_2024.csv, survey_biodiversity_scores.csv, holding_biodiversity_scores.csv, cdp_biodiversity_scores.csv, Biodiversity Data Codebook.pdf | https://www.biodiversityrisk.org/download/ | Download the five files from the source page into this folder. A zip named BRFV_giglio_raw_<date>.zip in 01_data/raw works too: step 01 unpacks it. Step 01 checks each SHA-256 |
| compustat | BRFV_compustat_funda_raw.csv | Compustat North America, Fundamentals Annual, through WRDS | Your own login. See 05_docs/BRFV_wrds_query_spec.md. Licensed: never publish |
| climate | BRFV_climate_exposure_raw.csv (optional) | Firm-level climate change exposure of Sautner, van Lent, Vilkov and Zhang (2023) | Download from the authors' data release, save under this name, then set the three column names in CLIMATE_COLUMNS in 02_code/brfv_00_config.py |

Record every new file in 05_docs/BRFV_data_log.csv with its date and SHA-256.
