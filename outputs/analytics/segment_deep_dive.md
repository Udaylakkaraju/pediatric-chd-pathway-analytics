# Segment deep dive
_Synthetic cohort; descriptive segments only._

## insurance_type
| segment | n | diagnosis_rate | mean_delay | median_delay |
|---|---:|---:|---:|---:|
| private | 6499 | 0.293 | 11.5 | 8.5 |
| medicaid | 6216 | 0.248 | 11.4 | 8.1 |
| uninsured | 1322 | 0.178 | 9.9 | 6.5 |
| other | 963 | 0.279 | 11.7 | 8.8 |

## chd_severity
| segment | n | diagnosis_rate | mean_delay | median_delay |
|---|---:|---:|---:|---:|
| Simple | 7911 | 0.168 | 13.9 | 10.8 |
| Complex | 6202 | 0.383 | 8.1 | 5.8 |
| Moderate | 887 | 0.276 | 10.9 | 7.2 |

## age_band
| segment | n | diagnosis_rate | mean_delay | median_delay |
|---|---:|---:|---:|---:|
| 6-12 | 5858 | 0.275 | 11.4 | 8.3 |
| 13+ | 4891 | 0.248 | 11.3 | 8.1 |
| 3-5 | 3846 | 0.264 | 11.2 | 8.2 |
| 0-2 | 405 | 0.267 | 12.0 | 8.5 |

## cohort_era
| segment | n | diagnosis_rate | mean_delay | median_delay |
|---|---:|---:|---:|---:|
| 2021+ | 8880 | 0.260 | 11.3 | 8.2 |
| 2017-2020 | 6120 | 0.268 | 11.4 | 8.2 |

## svi_tertile
| segment | n | diagnosis_rate | mean_delay | median_delay |
|---|---:|---:|---:|---:|
| T1_lowest_SVI | 5000 | 0.312 | 11.8 | 8.8 |
| T2_mid_SVI | 5000 | 0.255 | 11.4 | 8.2 |
| T3_highest_SVI | 5000 | 0.223 | 10.7 | 7.5 |

## insurance_x_severity
| segment | n | diagnosis_rate | mean_delay | median_delay |
|---|---:|---:|---:|---:|
| private | Simple | 3440 | 0.188 | 14.1 | 11.0 |
| medicaid | Simple | 3275 | 0.154 | 14.0 | 10.6 |
| private | Complex | 2670 | 0.420 | 8.2 | 6.2 |
| medicaid | Complex | 2592 | 0.369 | 8.1 | 5.5 |
| uninsured | Simple | 683 | 0.098 | 12.2 | 8.8 |
| uninsured | Complex | 551 | 0.278 | 7.2 | 4.2 |
| other | Simple | 513 | 0.216 | 14.7 | 11.8 |
| other | Complex | 389 | 0.375 | 8.0 | 5.4 |
| private | Moderate | 389 | 0.350 | 11.1 | 7.8 |
| medicaid | Moderate | 349 | 0.235 | 11.3 | 7.5 |
| uninsured | Moderate | 88 | 0.170 | 8.8 | 5.6 |
| other | Moderate | 61 | 0.197 | 10.6 | 6.2 |

### Callout (insurance × severity, n≥80, highest mean delay)

- **other | Simple**: n=513, diagnosis_rate=0.216, mean_delay=14.7
