# BRFV_T15_tone_within_firms_checks

| check | version | role | term | coef | se | p | n_obs | n_firms | dep_var | fixed_effects | cluster | stars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| W0 main estimate | three scores | negative | bd_negative_lag | -0.0629 | 0.0295 | 0.0329 | 16,498 | 2,464 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey | ** |
| W0 main estimate | alone | negative | bd_negative_lag | -0.0533 | 0.0282 | 0.0587 | 16,498 | 2,464 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey | * |
| W1 log Tobin's Q | three scores | negative | bd_negative_lag | -0.0277 | 0.0122 | 0.0229 | 16,498 | 2,464 | dv_ln_tobin_q_w | id_gvkey + t_fyear | id_gvkey | ** |
| W1 log Tobin's Q | alone | negative | bd_negative_lag | -0.0250 | 0.0121 | 0.0385 | 16,498 | 2,464 | dv_ln_tobin_q_w | id_gvkey + t_fyear | id_gvkey | ** |
| W2 firm effects and industry group by year effects | three scores | negative | bd_negative_lag | -0.0199 | 0.0274 | 0.4689 | 16,496 | 2,463 | dv_tobin_q_w | id_gvkey + fe_ind_year | id_gvkey |  |
| W2 firm effects and industry group by year effects | alone | negative | bd_negative_lag | -0.0103 | 0.0271 | 0.7035 | 16,496 | 2,463 | dv_tobin_q_w | id_gvkey + fe_ind_year | id_gvkey |  |
| W3 utilities excluded | three scores | negative | bd_negative_lag | -0.0607 | 0.0337 | 0.0721 | 15,844 | 2,387 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey | * |
| W3 utilities excluded | alone | negative | bd_negative_lag | -0.0512 | 0.0318 | 0.1074 | 15,844 | 2,387 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey |  |
| W4 fiscal year 2020 excluded | three scores | negative | bd_negative_lag | -0.0693 | 0.0332 | 0.0370 | 14,868 | 2,442 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey | ** |
| W4 fiscal year 2020 excluded | alone | negative | bd_negative_lag | -0.0635 | 0.0322 | 0.0487 | 14,868 | 2,442 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey | ** |
| W5 December year ends only | three scores | negative | bd_negative_lag | -0.0754 | 0.0300 | 0.0119 | 12,240 | 1,887 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey | ** |
| W5 December year ends only | alone | negative | bd_negative_lag | -0.0642 | 0.0281 | 0.0224 | 12,240 | 1,887 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey | ** |
| W6 CUSIP matches only | three scores | negative | bd_negative_lag | -0.0651 | 0.0298 | 0.0289 | 16,046 | 2,363 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey | ** |
| W6 CUSIP matches only | alone | negative | bd_negative_lag | -0.0556 | 0.0285 | 0.0514 | 16,046 | 2,363 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey | * |
| W7 ever-disclosing firms | three scores | negative | bd_negative_lag | -0.0829 | 0.0246 | 0.0009 | 1,691 | 224 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey | *** |
| W7 ever-disclosing firms | alone | negative | bd_negative_lag | -0.0775 | 0.0227 | 0.0007 | 1,691 | 224 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey | *** |
| W8 clustered by industry group | three scores | negative | bd_negative_lag | -0.0629 | 0.0190 | 0.0032 | 16,498 | 2,464 | dv_tobin_q_w | id_gvkey + t_fyear | ind_gics4 | *** |
| W8 clustered by industry group | alone | negative | bd_negative_lag | -0.0533 | 0.0139 | 0.0009 | 16,498 | 2,464 | dv_tobin_q_w | id_gvkey + t_fyear | ind_gics4 | *** |
| W9 lead: Negative two years ahead added | three scores | lead | bd_negative_lead | 0.0247 | 0.0342 | 0.4704 | 10,924 | 1,791 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey |  |
| W9 lead: Negative two years ahead added | three scores | negative | bd_negative_lag | -0.0873 | 0.0410 | 0.0332 | 10,924 | 1,791 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey | ** |
| W9 lead: Negative two years ahead added | alone | lead | bd_negative_lead | 0.0264 | 0.0342 | 0.4408 | 10,924 | 1,791 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey |  |
| W9 lead: Negative two years ahead added | alone | negative | bd_negative_lag | -0.0652 | 0.0376 | 0.0829 | 10,924 | 1,791 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey | * |
| W10 other timing: score of the next score year | three scores | negative | bd_negative_alt | 0.0061 | 0.0324 | 0.8493 | 14,165 | 2,281 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey |  |
| W10 other timing: score of the next score year | alone | negative | bd_negative_alt | 0.0152 | 0.0319 | 0.6352 | 14,165 | 2,281 | dv_tobin_q_w | id_gvkey + t_fyear | id_gvkey |  |

Coefficient on the Negative score with firm fixed effects and the full set of controls. Version 'three scores' enters Count, Negative and Regulation together, version 'alone' enters Negative only. In W9 the role 'lead' is the Negative score that the firm reports two years later, added to the model. Added on 23 November 2026, after the first results. These checks decide no hypothesis.
