# NYC Taxi Trip Duration: Exploratory Analysis and Prediction

**Applied Data Science Skill Lab, CSE (Data Science), RVCE**
**Team members:** _add names and USNs_
**Notebook:** `notebooks/nyc_taxi_trip_duration.ipynb` (all numbers below come from its executed outputs)

---

## 1. Introduction and Problem Statement
Taxi trip time in a large city depends on distance, time of day, day of the week and location. Distance alone is a weak predictor because traffic and demand change through the day. This project analyses New York City yellow-taxi trips from January to June 2016 and builds a regression model that predicts **trip duration in seconds** from information known at pickup: the pickup time and the pickup and dropoff coordinates. Possible uses are ETA and fare estimation, dispatch planning and urban mobility analysis.

## 2. Objectives
1. Acquire and document the dataset.
2. Clean and prepare the data, documenting each decision.
3. Explore distributions, relationships and outliers.
4. Visualize patterns with Matplotlib and Seaborn.
5. Train, compare and evaluate regression models with Scikit-learn.
6. Interpret the results, including usefulness and limitations.

## 3. Dataset Description and Source
- **Name and source:** *New York City Taxi Trip Duration*, Kaggle competition (https://www.kaggle.com/competitions/nyc-taxi-trip-duration/data), based on 2016 NYC Taxi & Limousine Commission yellow-taxi records.
- **Size:** about 1.46 million trips in the full file; a **100,000-trip sample** (11 attributes) is used here.
- **Time period:** 1 January to 30 June 2016.
- **Variables:** `id`, `vendor_id` (1 or 2), `pickup_datetime`, `dropoff_datetime`, `passenger_count`, pickup and dropoff longitude and latitude, `store_and_fwd_flag` (Y/N) and the target `trip_duration` (seconds).
- **Limitations:** six months only; no weather, live traffic or route data; driver-entered passenger counts can be wrong; only start and end coordinates are known; `dropoff_datetime` equals pickup plus duration, so it cannot be used as an input (target leakage).
- **Privacy and usage:** no personal identifiers are present; the data is used for academic purposes under the competition rules.

## 4. Data Preparation and Cleaning
Inspection found **no missing values, no duplicated rows or trip ids**, and the recorded duration matches the timestamps exactly. The remaining risk was implausible values, handled with documented rules:

| Rule | Records flagged | Reason |
|---|---|---|
| 0 passengers | 1 | not a valid passenger trip |
| Pickup/dropoff outside NYC bounding box | 49 | GPS error or atypical trip |
| Duration < 60 s | 592 | cancelled fare or meter error |
| Duration > 3 h | 129 | meter left running |
| Implied speed > 120 km/h | 6 | impossible in city traffic |

Records can break more than one rule; in total **761 unique records (0.76%) were removed, leaving 99,239**. Long but plausible trips were kept.

**Derived variables:** pickup hour, weekday, month, weekend flag, weekday rush-hour flag (07:00–10:00, 16:00–19:00), straight-line (haversine) distance, Manhattan-style distance, compass bearing, and log of distance and duration. Speed was computed for analysis only because it uses the target. The cleaned file is `data/train_cleaned.csv`.

## 5. Exploratory Data Analysis
- **Duration** has a median of 11.1 min, a mean of 14.0 min and a standard deviation of 10.9 min. It is right-skewed (skewness 2.27); the 95th percentile is 34.7 min and the 99th is 54.7 min. After a log transform the skewness is −0.14.
- **Distance:** median 2.1 km, mean 3.4 km (skewness 2.8). Correlation with duration is 0.77.
- **Categories:** vendor split is 53% / 47% with identical mean durations (14.0 min); 71% of trips carry one passenger; 0.6% of trips have the store-and-forward flag and last longer on average (18.3 min versus 14.0 min).
- **Outliers (IQR method):** 4,908 trips (4.95%) exceed the duration fence of 2,090 s. Their median distance is 12.5 km (typical trips: 2.0 km), 89.6% exceed 5 km, and about 58.5% touch the airport zones. They are genuine long trips and were **not removed**.

## 6. Visualization and Insight Generation
Figures are in `figures/`.

| Figure | What it shows | Insight |
|---|---|---|
| fig01, fig02 | Duration histogram, box plots | Skewed with a long tail; log transform justified |
| fig03 | Distance vs duration | r = 0.77, but wide scatter at every distance |
| fig04 | Demand and duration by hour | Fewest trips at 05:00 (1,041), most at 18:00–19:00 (about 6,200); longest trips at 15:00 (16.2 min) |
| fig05 | Weekday and weekday × hour heatmap | Weekday daytime is slowest (median up to 14 min); Sunday morning fastest (about 7 min); weekends 12.8 min vs 14.5 min on weekdays |
| fig06 | Daily trend | Quietest days: 23 Jan (122 trips) and 24 Jan (253), coinciding with the January 2016 snowstorm, and 30 May (Memorial Day); mean duration rises from 13.2 min (Jan) to 15.0 min (Jun) |
| fig07 | Pickup and dropoff density | Pickups concentrate in Manhattan and at JFK and LaGuardia |
| fig08 | Vendor, store-and-forward, rush hour | Vendors identical; rush hour adds about 1 min |
| fig09 | Correlation heatmap | Only distance is strongly linked to duration; hour, weekday, passengers and vendor each have a correlation below 0.07 in size |

Correlation is not read as causation. For example, pickup longitude (r = 0.36) marks where airport trips start; it does not make trips longer.

## 7. Predictive Modelling and Evaluation
**Task:** regression. **Target:** `trip_duration`, modelled as log(1 + duration) and converted back to seconds for evaluation. **Features (16):** vendor, passenger count, store-and-forward flag, four coordinates, hour, weekday, month, weekend and rush-hour flags, haversine distance (and its log), Manhattan distance and bearing. **Split:** 80% training (79,391 trips) and 20% testing (19,848 trips), random seed 42. The test set was never used to fit a model.

| Model | MAE (s) | RMSE (s) | Median AE (s) | R² (log) | RMSLE |
|---|---|---|---|---|---|
| Baseline (median) | 442.6 | 673.8 | 314.0 | −0.001 | 0.729 |
| Linear Regression | 253.0 | 398.8 | 160.4 | 0.641 | 0.437 |
| Random Forest | 189.9 | 314.0 | 118.3 | 0.779 | 0.343 |
| **Gradient Boosting** | **177.8** | **295.6** | **111.6** | **0.798** | **0.328** |

- Gradient Boosting reduces MAE by **59.8%** relative to the baseline (178 s ≈ 3.0 min against 7.4 min).
- **52.9%** of test predictions are within 2 minutes of the actual duration, **84.3%** within 5 minutes and **95.9%** within 10 minutes.
- 5-fold cross-validation RMSLE is 0.326 (± 0.003) against 0.328 on the test set, so there is no sign of overfitting.
- The actual-versus-predicted table for 15 test trips is in the notebook; the full test-set table is `outputs/actual_vs_predicted_test.csv`.
- Three new hypothetical trips were also predicted: Times Square to Wall Street at 08:30 on a Wednesday (26.7 min) and at 03:00 on a Sunday (17.9 min), and Grand Central to JFK on a Friday at 17:30 (68.6 min).

## 8. Key Findings and Interpretation
1. Trip distance is the dominant driver of duration; time of day, weekday and season add smaller but clear effects (afternoon and weekday trips are slower).
2. Distance features account for most of the model's predictive power (haversine distance about 76% of permutation importance), followed by pickup hour (8%) and bearing (5%). Passenger count and vendor contribute almost nothing, matching the EDA.
3. The absolute error grows with distance (130 s under 1 km to 422 s above 15 km) while the relative error falls (39% to 16%): short trips are dominated by lights, hailing and waiting, which the data cannot describe.
4. The model is accurate enough for ETA display, rough fare estimates and dispatch planning, with a typical error of about 3 minutes.

## 9. Limitations and Possible Improvements
**Limitations**
- No weather, live traffic, closures, accidents or events, which cause most of the large errors; about 4% of predictions are wrong by more than 10 minutes.
- Straight-line distance instead of the real route; start and end points only.
- Training on log duration pulls predictions toward typical values, so very long trips are underestimated.
- Only six months of 2016 and a 100,000-trip sample; results may not generalize to other periods.
- Associations only; the cause of trends such as rising durations from January to June cannot be established from this data.

**Improvements**
1. Add weather and public-holiday features.
2. Use road-network route distance and time (for example OSRM) and pickup/dropoff zone clusters.
3. Train on the full 1.46 million trips with hyperparameter tuning and ensembles.
4. Use quantile regression to give a time range instead of a single value.

## 10. Conclusion and References
Distance and time of day make taxi trip duration reasonably predictable. A gradient-boosting model cuts the average error by about 60% compared with a naive guess, reaching a test MAE of about 3 minutes. The remaining error comes mainly from factors outside the dataset, chiefly traffic and weather, so predictions should be used as estimates and not as exact times.

**References**
1. Kaggle. *New York City Taxi Trip Duration* competition. https://www.kaggle.com/competitions/nyc-taxi-trip-duration
2. NYC Taxi & Limousine Commission. *TLC Trip Record Data*. https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
3. Pedregosa et al. (2011). Scikit-learn: Machine Learning in Python. *JMLR* 12, 2825–2830.
4. McKinney, W. (2010). Data Structures for Statistical Computing in Python. *Proc. SciPy 2010*.
5. Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. *Computing in Science & Engineering* 9(3).
6. Waskom, M. (2021). seaborn: statistical data visualization. *JOSS* 6(60), 3021.
