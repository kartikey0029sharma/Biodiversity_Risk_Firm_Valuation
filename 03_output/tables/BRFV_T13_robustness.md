# BRFV_T13_robustness

| check | term | coef | se | p | n_obs | n_firms | dep_var | fixed_effects | cluster | stars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R1 log Tobin's Q | bd_count_lag | -0.0358 | 0.0261 | 0.1696 | 16,805 | 2,774 | dv_ln_tobin_q_w | fe_ind_year | id_gvkey |  |
| R1 log Tobin's Q | bd_negative_lag | -0.0067 | 0.0138 | 0.6272 | 16,805 | 2,774 | dv_ln_tobin_q_w | fe_ind_year | id_gvkey |  |
| R1 log Tobin's Q | bd_regulation_lag | -0.0453 | 0.0296 | 0.1263 | 16,805 | 2,774 | dv_ln_tobin_q_w | fe_ind_year | id_gvkey |  |
| R2 industry-adjusted Q, year effects | bd_count_lag | -0.0398 | 0.0746 | 0.5941 | 16,808 | 2,774 | dv_tobin_q_indadj | t_fyear | id_gvkey |  |
| R2 industry-adjusted Q, year effects | bd_negative_lag | 0.0127 | 0.0363 | 0.7256 | 16,808 | 2,774 | dv_tobin_q_indadj | t_fyear | id_gvkey |  |
| R2 industry-adjusted Q, year effects | bd_regulation_lag | -0.0410 | 0.0881 | 0.6413 | 16,808 | 2,774 | dv_tobin_q_indadj | t_fyear | id_gvkey |  |
| R3 utilities excluded | bd_count_lag | -0.0410 | 0.0915 | 0.6539 | 16,147 | 2,693 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| R3 utilities excluded | bd_negative_lag | 0.0032 | 0.0371 | 0.9316 | 16,147 | 2,693 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| R3 utilities excluded | bd_regulation_lag | -0.0670 | 0.1079 | 0.5348 | 16,147 | 2,693 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| R4 fiscal year 2020 excluded | bd_count_lag | -0.0485 | 0.0727 | 0.5047 | 15,189 | 2,766 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| R4 fiscal year 2020 excluded | bd_negative_lag | 0.0154 | 0.0353 | 0.6629 | 15,189 | 2,766 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| R4 fiscal year 2020 excluded | bd_regulation_lag | -0.0724 | 0.0802 | 0.3665 | 15,189 | 2,766 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| R5 December year ends only | bd_count_lag | -0.0340 | 0.0815 | 0.6765 | 12,494 | 2,144 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| R5 December year ends only | bd_negative_lag | 0.0140 | 0.0325 | 0.6661 | 12,494 | 2,144 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| R5 December year ends only | bd_regulation_lag | -0.0737 | 0.0883 | 0.4041 | 12,494 | 2,144 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| R6 CUSIP matches only | bd_count_lag | -0.0230 | 0.0746 | 0.7581 | 16,330 | 2,650 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| R6 CUSIP matches only | bd_negative_lag | 0.0094 | 0.0326 | 0.7738 | 16,330 | 2,650 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| R6 CUSIP matches only | bd_regulation_lag | -0.0479 | 0.0844 | 0.5704 | 16,330 | 2,650 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| R7 ever-disclosing firms, firm and year effects | bd_count_lag | -0.0261 | 0.0404 | 0.5187 | 1,691 | 247 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey |  |
| R7 ever-disclosing firms, firm and year effects | bd_negative_lag | -0.0775 | 0.0227 | 0.0007 | 1,691 | 247 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey | *** |
| R7 ever-disclosing firms, firm and year effects | bd_regulation_lag | -0.0128 | 0.0340 | 0.7063 | 1,691 | 247 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey |  |
| R8 clustered by industry group | bd_count_lag | -0.0441 | 0.0605 | 0.4737 | 16,805 | 2,774 | dv_tobin_q_w | fe_ind_year | ind_gics4 |  |
| R8 clustered by industry group | bd_negative_lag | 0.0121 | 0.0235 | 0.6100 | 16,805 | 2,774 | dv_tobin_q_w | fe_ind_year | ind_gics4 |  |
| R8 clustered by industry group | bd_regulation_lag | -0.0605 | 0.0754 | 0.4313 | 16,805 | 2,774 | dv_tobin_q_w | fe_ind_year | ind_gics4 |  |
| R9 placebo: score two years ahead | bd_count_lead | 0.0148 | 0.0769 | 0.8470 | 11,257 | 2,124 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| R9 placebo: score two years ahead | bd_negative_lead | 0.0072 | 0.0427 | 0.8655 | 11,257 | 2,124 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| R9 placebo: score two years ahead | bd_regulation_lead | -0.0732 | 0.0834 | 0.3807 | 11,257 | 2,124 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| R10 other timing: score of the next score year | bd_count_alt | -0.0212 | 0.0801 | 0.7914 | 14,486 | 2,605 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| R10 other timing: score of the next score year | bd_negative_alt | 0.0151 | 0.0338 | 0.6549 | 14,486 | 2,605 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| R10 other timing: score of the next score year | bd_regulation_alt | -0.0680 | 0.0892 | 0.4459 | 14,486 | 2,605 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |

Each row is one regression with the full set of controls; only the coefficient on the score is shown. In R9 the reported term is the future score, which should not explain today's valuation. R10 uses the score of the next score year in place of the lagged score.
