# Segment deep dive
_Synthetic cohort; descriptive segments only._

## insurance_type
| segment | n | diagnosis_rate | mean_delay | median_delay |
|---|---:|---:|---:|---:|
| medicaid | 2245 | 0.205 | 15.1 | 9.3 |
| private | 1995 | 0.212 | 13.4 | 8.7 |
| uninsured | 476 | 0.223 | 16.3 | 10.5 |
| other | 253 | 0.206 | 13.7 | 8.3 |

## chd_severity
| segment | n | diagnosis_rate | mean_delay | median_delay |
|---|---:|---:|---:|---:|
| Simple | 2687 | 0.125 | 18.4 | 12.2 |
| Complex | 1997 | 0.327 | 9.4 | 6.5 |
| Moderate | 285 | 0.179 | 13.1 | 8.0 |

## age_band
| segment | n | diagnosis_rate | mean_delay | median_delay |
|---|---:|---:|---:|---:|
| 0-2 | 2583 | 0.208 | 14.5 | 9.2 |
| 3-5 | 1249 | 0.207 | 15.0 | 9.5 |
| 6-12 | 926 | 0.216 | 13.2 | 8.5 |
| 13+ | 211 | 0.227 | 16.6 | 8.5 |

## cohort_era
| segment | n | diagnosis_rate | mean_delay | median_delay |
|---|---:|---:|---:|---:|
| 2017-2020 | 2723 | 0.209 | 14.5 | 9.0 |
| 2021+ | 2246 | 0.210 | 14.5 | 9.2 |

## svi_tertile
| segment | n | diagnosis_rate | mean_delay | median_delay |
|---|---:|---:|---:|---:|
| T1_lowest_SVI | 1657 | 0.264 | 15.3 | 9.7 |
| T2_mid_SVI | 1656 | 0.197 | 14.3 | 9.1 |
| T3_highest_SVI | 1656 | 0.168 | 13.9 | 8.5 |

## insurance_x_severity
| segment | n | diagnosis_rate | mean_delay | median_delay |
|---|---:|---:|---:|---:|
| medicaid | Simple | 1233 | 0.122 | 18.9 | 12.2 |
| private | Simple | 1072 | 0.132 | 17.5 | 12.0 |
| medicaid | Complex | 873 | 0.329 | 10.2 | 6.6 |
| private | Complex | 812 | 0.318 | 8.1 | 6.0 |
| uninsured | Simple | 245 | 0.114 | 20.4 | 14.2 |
| uninsured | Complex | 207 | 0.362 | 11.8 | 8.6 |
| medicaid | Moderate | 139 | 0.165 | 12.9 | 6.8 |
| other | Simple | 137 | 0.117 | 16.8 | 10.8 |
| private | Moderate | 111 | 0.207 | 12.8 | 8.8 |
| other | Complex | 105 | 0.324 | 9.1 | 5.8 |
| uninsured | Moderate | 24 | 0.125 | 13.3 | 7.3 |
| other | Moderate | 11 | 0.182 | 17.9 | 12.9 |

### Callout (insurance × severity, n≥80, highest mean delay)

- **uninsured | Simple**: n=245, diagnosis_rate=0.114, mean_delay=20.4
