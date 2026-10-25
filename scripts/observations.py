"""Interpretation text inserted into the notebook (numbers come from the executed notebook outputs)."""

OBS = {}

OBS["outliers"] = """**Observations (outlier investigation)**
- With the IQR rule (fences at Q1 − 1.5·IQR and Q3 + 1.5·IQR), **4,908 trips (4.95%)** have a duration above the upper fence of **2,090 s (about 35 min)**. No trip falls below the lower fence because the fence is negative.
- These are **not errors**. Their median distance is **12.5 km versus 2.0 km** for typical trips, **89.6% travel more than 5 km** (only 14.3% of typical trips do), and they run at a plausible median speed of 16 km/h. About **58.5% start or end near the JFK/LaGuardia airport zones**. They are genuinely long journeys, so they are **kept**.
- The IQR rule also flags 9.7% of distances and 10.8% of passenger counts. For passenger count this is an artefact: most trips carry one person, so the IQR is tiny and groups of 4–6 look unusual even though they are valid.
- **Decision:** no further records are removed. Instead the skew is handled by modelling the **log of the duration** (skewness falls from 2.27 to −0.14)."""

OBS["eda_summary"] = """### 4.5 Summary of EDA findings
1. **Duration is right-skewed:** median 11.1 min, mean 14.0 min, 95th percentile 34.7 min. Most trips are short, with a long tail of airport and cross-borough trips.
2. **Distance is the dominant driver:** straight-line distance and duration have a correlation of about 0.77. Median distance is 2.1 km.
3. **Vendors are balanced** (53% / 47%) and have almost identical durations (14.0 min each). `passenger_count` is 71% single riders and has no meaningful link to duration.
4. **Store-and-forward trips (0.6% of data)** last longer on average (18.3 min versus 14.0 min). The sample is small and the flag is probably a proxy for longer or out-of-area trips, so it should not be read as a cause.
5. Demand and duration follow strong **time-of-day and weekday patterns**, shown in the next section."""

OBS["viz"] = """### Interpretation of the visualizations
- **Fig 1–2 (distribution, box plots):** the middle half of trips take about 7 to 18 minutes. The right tail is long, which supports using a log transform before modelling.
- **Fig 3 (distance vs duration):** the relationship is clearly increasing (r = 0.77), but trips of the same distance differ by 2 to 3 times in duration. Distance alone leaves a lot unexplained, which is why time-of-day features matter.
- **Fig 4 (hourly):** demand is lowest at about 05:00 (1,041 trips) and highest in the evening (about 6,200 trips at 18:00–19:00). Mean duration is **longest in the afternoon (16.2 min at 15:00)** and shortest at 06:00 (11.0 min). Evening has the most trips but the afternoon has the slowest ones, which is consistent with congestion building up during the day.
- **Fig 5 (weekday × hour):** weekday daytime trips are the slowest (median up to 14 min on Tuesday to Thursday between 10:00 and 14:00), while Sunday morning is the fastest (about 7 min). Weekend trips average 12.8 min against 14.5 min on weekdays. Friday has the most trips and Monday the fewest.
- **Fig 6 (daily trend):** the quietest days are **23 January (122 trips)** and 24 January (253 trips), which coincide with the major snowstorm that hit New York on 22–24 January 2016, and **30 May (369 trips)**, which was Memorial Day. These dates come from outside the dataset and are noted only as a plausible explanation. Mean trip duration also **rises steadily from 13.2 min in January to 15.0 min in June (+13.5%)**.
- **Fig 7 (location density):** pickups concentrate in Manhattan (Midtown and Lower Manhattan), with two clear secondary clusters at the JFK and LaGuardia airports. Dropoffs are more widely spread across the outer boroughs.
- **Fig 8 (categories):** vendors and rush-hour status make little difference to the average duration (rush hour adds about 1 minute); the store-and-forward flag shows the larger gap discussed above.
- **Fig 9 (correlation):** only distance has a strong link with duration (haversine 0.77, Manhattan 0.75). Pickup longitude (0.36) is a weaker, indirect signal because the airports lie to the east. Hour, weekday, passenger count and vendor each have correlations below 0.07 with duration. **Correlation does not show causation:** for example, longitude does not make a trip longer; it marks where long airport trips start."""

OBS["modelling"] = """### Interpretation of the modelling results
- **All three models beat the baseline.** The median-only baseline has a test MAE of **443 s (7.4 min)**. Linear Regression reduces it to 253 s, Random Forest to 190 s and **Gradient Boosting to 178 s (2.96 min), a 59.8% improvement**.
- **Gradient Boosting is best on every metric:** MAE 177.8 s, RMSE 295.6 s, median absolute error 111.6 s (typical error under 2 minutes), R² on the log scale 0.798 and RMSLE 0.328. It also trains in about 3 seconds, much faster than the Random Forest (about 16 seconds).
- **Accuracy in practical terms:** 52.9% of test predictions are within 2 minutes of the actual duration, **84.3% within 5 minutes** and 95.9% within 10 minutes.
- **No sign of overfitting:** 5-fold cross-validation on the training data gives an RMSLE of 0.326 (± 0.003), almost identical to the held-out test score of 0.328.
- **What drives the predictions:** distance features dominate (haversine distance alone accounts for about 76% of the permutation importance, and the other distance features are highly correlated with it), followed by pickup hour (8%), travel direction/bearing (5%) and weekday (2.7%). Passenger count and vendor contribute almost nothing, matching the EDA.
- **Error pattern:** the absolute error grows with distance (130 s for trips under 1 km, 422 s above 15 km), but the relative error shrinks (39% for trips under 1 km, 16% above 15 km). Very short trips are hard to predict because their time is dominated by traffic lights, hailing and waiting rather than distance.
- **Sanity check on new trips:** the model predicts 26.7 min for Times Square to Wall Street at 08:30 on a Wednesday but 17.9 min at 03:00 on a Sunday, and 68.6 min for Grand Central to JFK on a Friday at 17:30. All are plausible and show that the model has learned time-of-day effects."""

OBS["interpretation"] = """### Summary of findings
- Trip duration in this sample has a median of 11.1 min and is mainly determined by **trip distance (r = 0.77)**, with a smaller but visible effect of **time of day, weekday and season** (afternoon and weekday trips are slower; average duration rose by about 13% from January to June).
- A **Gradient Boosting regression model** predicts duration with a test **MAE of about 3.0 minutes** (178 s), versus 7.4 minutes for a naive baseline, and 84% of predictions fall within 5 minutes of the actual value.

### Usefulness
- Good enough for **ETA display, rough fare estimates, dispatch and demand planning**, and for comparing typical times between areas and times of day.
- It is cheap to run (a trained model predicts in milliseconds) and needs only pickup and dropoff coordinates plus the pickup time.

### Limitations
- **Missing information:** the data has no weather, live traffic, road closures, accidents or events, which cause most of the large errors (for example one test trip of 8.1 km at 07:02 on a Tuesday took 27.7 min but was predicted at 15.2 min). Errors of more than 10 minutes still occur for about 4% of trips.
- **Straight-line distance** is used instead of the actual route; bridges, one-way streets and highways are not captured.
- **Under-prediction of very long trips:** the model is trained on log durations, which pushes predictions toward typical values, so extreme trips are underestimated (visible below the diagonal in the actual-vs-predicted plot).
- **Limited coverage:** only 6 months of 2016 and a 100,000-trip sample; it may not hold for other seasons, years, or after changes in ride-hailing and congestion pricing.
- **Predicting is not explaining:** the model finds associations only. For example, the rising duration from January to June could reflect weather, construction or traffic growth; the data cannot say which.

### Possible improvements
1. Add **weather** (rain, snow, temperature) and **public-holiday** features; the snowstorm and Memorial Day dips already show their effect.
2. Replace straight-line distance with **road-network route distance and time** (for example from OSRM), and add **pickup/dropoff zone clusters**.
3. Train on the **full 1.46 million trips**, tune hyperparameters with cross-validation, and try ensembles (for example boosting plus random forest).
4. Use **quantile regression** to give a time range (for example 12 to 18 minutes) instead of a single number, which is more honest about uncertainty.

### Conclusion
Trip distance and time of day make taxi trip duration reasonably predictable, and a gradient-boosting model cuts the average error by about 60% compared with a naive guess. The remaining error is mainly due to factors outside the dataset, mostly traffic and weather, so the predictions are best used as **estimates with a typical error of about 3 minutes**, not exact times."""
