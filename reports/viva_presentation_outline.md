# Presentation and Viva-Voce Outline

Flow required by the guidelines: **Problem → Data → Analysis → Evidence → Insight → Conclusion**. About 10 to 12 slides, 8 to 10 minutes.

## Slide plan

| # | Stage | Slide | Content and figure |
|---|---|---|---|
| 1 | Problem | Title | NYC Taxi Trip Duration: Prediction and Performance Analysis; team names |
| 2 | Problem | Why it matters | ETA and fare estimation, dispatch; question: can we predict trip time from pickup information? |
| 3 | Data | Dataset | Kaggle / NYC TLC 2016; 100,000 trips (of 1.46 M), 11 attributes, Jan to Jun 2016; limitations |
| 4 | Data | Cleaning | No missing values or duplicates; 761 records (0.76%) removed by 5 rules; 16 features built (table from Stage 3.4) |
| 5 | Analysis | Distribution of duration | fig01: median 11.1 min, skewed; log transform |
| 6 | Evidence | Distance drives duration | fig03: r = 0.77 but wide scatter |
| 7 | Evidence | Time patterns | fig04 and fig05: demand peaks 18:00–19:00, trips slowest at 15:00 and on weekdays |
| 8 | Evidence | Outliers are real | IQR table: 4.95% long trips, 12.5 km median, 58.5% airport; kept |
| 9 | Evidence | Model comparison | fig10 and table: baseline 443 s, Linear 253 s, Random Forest 190 s, Gradient Boosting 178 s |
| 10 | Evidence | Actual vs predicted | fig11 and the 15-row table; 84% within 5 min |
| 11 | Insight | What drives it, where it fails | fig13 and fig12: distance dominates; short trips hardest in relative terms; no traffic or weather |
| 12 | Conclusion | Conclusion and next steps | MAE about 3 min, 60% better than baseline; add weather, route distance, full data |

## Likely viva questions and short answers

**Why regression and not classification?** The target (seconds) is a continuous number.

**Why did you take the log of the duration?** It is strongly right-skewed (skewness 2.27 → −0.14). Models then care about relative errors and are not dominated by a few very long trips. Predictions are converted back to seconds for the reported metrics.

**Why not use `dropoff_datetime` as a feature?** It equals pickup time plus the target, so it would leak the answer; it would not be known when a trip starts.

**How did you handle outliers?** The IQR method flagged 4.95% of durations. We investigated them: they are long airport and cross-borough trips, so they were kept. Only records that are almost certainly errors were removed (0 passengers, outside NYC, under 60 s, over 3 h, speed above 120 km/h).

**Why MAE?** It is in the same unit as the target (seconds) and easy to interpret: the average error is about 178 s. RMSE, median AE, R² and RMSLE are also reported.

**How do you know the model is not overfitted?** Train-test split with an untouched test set, and 5-fold cross-validation: RMSLE 0.326 (± 0.003) against 0.328 on the test set.

**Why did Gradient Boosting win?** The relationship between distance, time and location is non-linear with interactions (for example, the same distance takes longer at 15:00 than at 03:00). Linear Regression cannot capture that; tree ensembles can, and boosting corrects its own errors step by step.

**Which features matter most?** Distance features by far (about 76% by permutation importance), then pickup hour, bearing and weekday. Passenger count and vendor are almost irrelevant.

**Does correlation mean causation here?** No. Pickup longitude correlates with duration only because the airports are in the east; it does not cause longer trips.

**What are the model's limitations?** No weather or live traffic, straight-line distance instead of the route, only six months, long trips underestimated, and about 4% of predictions are off by more than 10 minutes.

**How would you improve it?** Add weather and holidays, use road-network distance, train on all 1.46 million trips with tuning, and give prediction intervals using quantile regression.

**What is the baseline and why use it?** Predicting the median duration for every trip (MAE 443 s). A useful model must beat it; ours does by about 60%.

**Why an 80/20 split?** It leaves enough data to train (79,391 trips) and a large, unseen test set (19,848 trips) for a reliable error estimate.
