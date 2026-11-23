# BRFV_T16_regulation_after_2021_checks

| check | version | role | term | coef | se | p | n_obs | n_firms | dep_var | fixed_effects | cluster | stars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P0 main estimate | one score | score | bd_regulation_lag | -0.0046 | 0.0803 | 0.9539 | 16,805 | 2,772 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| P0 main estimate | one score | interaction | ix_regulation_post | -0.1748 | 0.0883 | 0.0478 | 16,805 | 2,772 | dv_tobin_q_w | fe_ind_year | id_gvkey | ** |
| P0 main estimate | one score | slope_post | slope_post | -0.1794 | 0.1150 | 0.1189 | 16,805 | 2,772 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| P1 log Tobin's Q | one score | score | bd_regulation_lag | -0.0186 | 0.0318 | 0.5587 | 16,805 | 2,772 | dv_ln_tobin_q_w | fe_ind_year | id_gvkey |  |
| P1 log Tobin's Q | one score | interaction | ix_regulation_post | -0.0835 | 0.0369 | 0.0237 | 16,805 | 2,772 | dv_ln_tobin_q_w | fe_ind_year | id_gvkey | ** |
| P1 log Tobin's Q | one score | slope_post | slope_post | -0.1021 | 0.0390 | 0.0090 | 16,805 | 2,772 | dv_ln_tobin_q_w | fe_ind_year | id_gvkey | *** |
| P2 industry-adjusted Q, year effects | one score | score | bd_regulation_lag | 0.1181 | 0.0872 | 0.1758 | 16,808 | 2,774 | dv_tobin_q_indadj | t_fyear | id_gvkey |  |
| P2 industry-adjusted Q, year effects | one score | interaction | ix_regulation_post | -0.5000 | 0.0939 | 0.0000 | 16,808 | 2,774 | dv_tobin_q_indadj | t_fyear | id_gvkey | *** |
| P2 industry-adjusted Q, year effects | one score | slope_post | slope_post | -0.3819 | 0.1175 | 0.0012 | 16,808 | 2,774 | dv_tobin_q_indadj | t_fyear | id_gvkey | *** |
| P3 utilities excluded | one score | score | bd_regulation_lag | 0.0060 | 0.1059 | 0.9548 | 16,147 | 2,691 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| P3 utilities excluded | one score | interaction | ix_regulation_post | -0.2157 | 0.1092 | 0.0484 | 16,147 | 2,691 | dv_tobin_q_w | fe_ind_year | id_gvkey | ** |
| P3 utilities excluded | one score | slope_post | slope_post | -0.2097 | 0.1424 | 0.1411 | 16,147 | 2,691 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| P4 fiscal year 2020 excluded | one score | score | bd_regulation_lag | -0.0153 | 0.0753 | 0.8388 | 15,189 | 2,764 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| P4 fiscal year 2020 excluded | one score | interaction | ix_regulation_post | -0.1620 | 0.0888 | 0.0682 | 15,189 | 2,764 | dv_tobin_q_w | fe_ind_year | id_gvkey | * |
| P4 fiscal year 2020 excluded | one score | slope_post | slope_post | -0.1773 | 0.1135 | 0.1184 | 15,189 | 2,764 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| P5 December year ends only | one score | score | bd_regulation_lag | -0.0334 | 0.0828 | 0.6871 | 12,494 | 2,142 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| P5 December year ends only | one score | interaction | ix_regulation_post | -0.1275 | 0.0902 | 0.1579 | 12,494 | 2,142 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| P5 December year ends only | one score | slope_post | slope_post | -0.1608 | 0.1241 | 0.1953 | 12,494 | 2,142 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| P6 CUSIP matches only | one score | score | bd_regulation_lag | 0.0108 | 0.0813 | 0.8939 | 16,330 | 2,648 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| P6 CUSIP matches only | one score | interaction | ix_regulation_post | -0.1863 | 0.0922 | 0.0435 | 16,330 | 2,648 | dv_tobin_q_w | fe_ind_year | id_gvkey | ** |
| P6 CUSIP matches only | one score | slope_post | slope_post | -0.1754 | 0.1186 | 0.1393 | 16,330 | 2,648 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| P7 clustered by industry group | one score | score | bd_regulation_lag | -0.0046 | 0.0718 | 0.9491 | 16,805 | 2,772 | dv_tobin_q_w | fe_ind_year | ind_gics4 |  |
| P7 clustered by industry group | one score | interaction | ix_regulation_post | -0.1748 | 0.0889 | 0.0626 | 16,805 | 2,772 | dv_tobin_q_w | fe_ind_year | ind_gics4 | * |
| P7 clustered by industry group | one score | slope_post | slope_post | -0.1794 | 0.1058 | 0.1048 | 16,805 | 2,772 | dv_tobin_q_w | fe_ind_year | ind_gics4 |  |
| P8 other timing: score of the next score year | one score | score | bd_regulation_alt | -0.0170 | 0.0859 | 0.8434 | 14,486 | 2,603 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| P8 other timing: score of the next score year | one score | interaction | ix_regulation_alt_post | -0.2000 | 0.0932 | 0.0319 | 14,486 | 2,603 | dv_tobin_q_w | fe_ind_year | id_gvkey | ** |
| P8 other timing: score of the next score year | one score | slope_post | slope_post | -0.2170 | 0.1264 | 0.0862 | 14,486 | 2,603 | dv_tobin_q_w | fe_ind_year | id_gvkey | * |
| P9 three scores and their interactions together | three scores | score | bd_regulation_lag | 0.0354 | 0.1378 | 0.7971 | 16,805 | 2,772 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |
| P9 three scores and their interactions together | three scores | interaction | ix_regulation_post | -0.3577 | 0.2023 | 0.0771 | 16,805 | 2,772 | dv_tobin_q_w | fe_ind_year | id_gvkey | * |
| P9 three scores and their interactions together | three scores | slope_post | slope_post_regulation | -0.3223 | 0.2252 | 0.1526 | 16,805 | 2,772 | dv_tobin_q_w | fe_ind_year | id_gvkey |  |

Regulation score with industry group by year effects and the full set of controls. Role 'score' is the slope before fiscal year 2022, 'interaction' the change from that year, and 'slope_post' their sum, the slope in the later period. Added on 23 November 2026, after the first results. These checks decide no hypothesis.
