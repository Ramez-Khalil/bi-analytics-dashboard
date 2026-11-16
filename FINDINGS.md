# Findings and interpretation

All values below come from this repository's reconstructed pipeline, not copied from coursework.

## Descriptive findings

The public sample contains 7,043 records and 1,869 churn labels (26.54%). Churn rates are:

| Segment | Records | Churn rate |
|---|---:|---:|
| Month-to-month | 3,875 | 42.71% |
| One-year contract | 1,473 | 11.27% |
| Two-year contract | 1,695 | 2.83% |
| Tenure 0–6 months | 1,481 | 52.94% |
| Tenure 49–72 months | 2,239 | 9.51% |

Average monthly charges are $74.44 among churn-labeled records versus $61.27 among non-churn records. These comparisons are descriptive; they are not adjusted causal estimates or formal hypothesis tests. Differences may reflect service mix, contract selection and other confounding variables. A histogram of tenure alone would not establish churn risk, so this project calculates churn rates within tenure groups.

## Held-out model evaluation

All models use the same 2,113-row stratified test set. Churn is the positive class.

| Model | Accuracy | Precision | Recall | F1 | ROC AUC | Average precision |
|---|---:|---:|---:|---:|---:|---:|
| Majority baseline | 73.45% | 0.00% | 0.00% | 0.000 | 0.500 | 0.265 |
| Logistic regression | 80.64% | 66.03% | 55.79% | 0.605 | 0.845 | 0.642 |
| Decision tree | 79.41% | 61.45% | 60.25% | 0.608 | 0.830 | 0.617 |

Logistic regression has better accuracy, precision and ranking discrimination in this run, while the constrained tree catches more churn cases and has slightly higher F1. There is no universal winner across business objectives. At the fixed threshold, logistic regression misses 248 of 561 churn cases and produces 161 false positives. The tree misses 223 and produces 212 false positives. See `reports/metrics.json` for exact values and confusion matrices (rows actual No/Yes, columns predicted No/Yes).

No repeated cross-validation or confidence interval for model metrics is claimed. Test differences are not established as statistically significant. The test results must not be reused to tune settings and then presented as independent evaluation. A future tuning phase needs training-only cross-validation and a new final evaluation protocol.

## Recommended next decisions

1. Investigate early-life service and onboarding issues in customer research.
2. Test voluntary contract incentives with a randomized pilot and measure incremental retention, cost and customer satisfaction.
3. Compare service/value perceptions within price and service segments rather than assuming price cuts solve churn.
4. Choose outreach thresholds using separately validated intervention costs and benefits. This dataset cannot establish campaign ROI.

These are hypotheses for business experiments, not claims of realized revenue or proven retention improvements.
