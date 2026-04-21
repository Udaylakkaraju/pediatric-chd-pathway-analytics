# Segment deep dive
_Synthetic cohort; descriptive segments only._

## insurance_type
| segment | n | diagnosis_rate | mean_delay | median_delay |
|---|---:|---:|---:|---:|
| private | 2484 | 0.223 | 894.3 | 540.0 |
| medicaid | 1728 | 0.193 | 832.7 | 470.5 |
| uninsured | 508 | 0.217 | 867.0 | 486.5 |
| other | 249 | 0.173 | 868.9 | 479.0 |

## chd_severity
| segment | n | diagnosis_rate | mean_delay | median_delay |
|---|---:|---:|---:|---:|
| Complex | 2959 | 0.117 | 799.8 | 463.0 |
| Simple | 1520 | 0.458 | 1031.4 | 654.8 |
| Moderate | 490 | 0.000 | 780.9 | 449.5 |

## age_band
| segment | n | diagnosis_rate | mean_delay | median_delay |
|---|---:|---:|---:|---:|
| 0-2 | 2583 | 0.210 | 883.5 | 506.0 |
| 3-5 | 1249 | 0.218 | 884.8 | 533.5 |
| 6-12 | 926 | 0.195 | 834.6 | 493.8 |
| 13+ | 211 | 0.218 | 743.9 | 446.5 |

## cohort_era
| segment | n | diagnosis_rate | mean_delay | median_delay |
|---|---:|---:|---:|---:|
| 2021+ | 2585 | 0.205 | 424.0 | 235.0 |
| 2017-2020 | 2384 | 0.215 | 1351.1 | 1213.0 |

## svi_tertile
| segment | n | diagnosis_rate | mean_delay | median_delay |
|---|---:|---:|---:|---:|
| T3_highest_SVI | 1657 | 0.220 | 844.7 | 479.0 |
| T1_lowest_SVI | 1656 | 0.203 | 894.6 | 528.6 |
| T2_mid_SVI | 1656 | 0.207 | 867.1 | 522.0 |

## insurance_x_severity
| segment | n | diagnosis_rate | mean_delay | median_delay |
|---|---:|---:|---:|---:|
| private | Complex | 1466 | 0.126 | 827.3 | 487.2 |
| medicaid | Complex | 1028 | 0.098 | 784.6 | 434.6 |
| private | Simple | 783 | 0.474 | 1045.0 | 676.0 |
| medicaid | Simple | 522 | 0.446 | 981.0 | 568.0 |
| uninsured | Complex | 319 | 0.138 | 779.1 | 448.0 |
| private | Moderate | 235 | 0.000 | 809.6 | 453.0 |
| medicaid | Moderate | 178 | 0.000 | 676.3 | 420.0 |
| other | Complex | 146 | 0.116 | 676.7 | 359.5 |
| uninsured | Simple | 137 | 0.482 | 1063.9 | 586.0 |
| other | Simple | 78 | 0.333 | 1175.4 | 821.4 |
| uninsured | Moderate | 52 | 0.000 | 887.4 | 477.0 |
| other | Moderate | 25 | 0.000 | 1035.2 | 581.0 |

### Callout (insurance × severity, n≥80, highest mean delay)

- **uninsured | Simple**: n=137, diagnosis_rate=0.482, mean_delay=1063.9
