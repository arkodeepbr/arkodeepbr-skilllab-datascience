# Project Proposal

**Course:** Applied Data Science Skill Lab, CSE (Data Science), RVCE
**Project title:** NYC Taxi Trip Duration: Exploratory Analysis and Prediction
**Team members:** _add names and USNs_

## 1. Problem statement
Taxi trip time in a large city depends on distance, time of day, day of the week and location. Passengers, drivers and fleet operators cannot estimate it reliably from distance alone because traffic and demand change through the day. This project analyses New York City yellow-taxi trips from January to June 2016 and builds a regression model that predicts the duration of a trip (in seconds) from information available when the trip starts.

## 2. Objectives
1. Acquire and document the NYC Taxi Trip Duration dataset.
2. Clean and prepare the data with Python and Pandas, documenting every decision.
3. Perform exploratory data analysis: descriptive statistics, frequency tables, distributions and IQR outlier investigation.
4. Visualize patterns with Matplotlib and Seaborn (bar charts, line charts, histograms, box plots, scatter plots, heatmaps).
5. Train and compare regression models with Scikit-learn and evaluate them on unseen test data (MAE, RMSE, R²).
6. Interpret the results, state limitations and suggest improvements.

## 3. Analytical questions
- How is trip duration distributed, and are extreme values errors or real trips?
- How strongly does distance explain duration?
- How do demand and duration change by hour, weekday and month?
- Do vendor, passenger count or the store-and-forward flag matter?
- How accurately can duration be predicted, and where does the model fail?

## 4. Dataset source
Kaggle competition **New York City Taxi Trip Duration** (https://www.kaggle.com/competitions/nyc-taxi-trip-duration/data), derived from the NYC Taxi & Limousine Commission 2016 yellow-taxi records. About 1.46 million trips with 11 attributes: trip id, vendor, pickup and dropoff timestamps, passenger count, pickup and dropoff coordinates, store-and-forward flag and trip duration. A 100,000-trip sample is used (14 MB). The data has no personal identifiers and is used for academic purposes under the competition rules.

## 5. Proposed methods and tools
- **Language and libraries:** Python, Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn.
- **Preparation:** validity checks, removal of impossible records, derived variables (hour, weekday, month, rush-hour flag, haversine and Manhattan distance, bearing).
- **EDA:** mean, median, mode, standard deviation, quartiles, skewness, frequency tables, IQR outlier analysis.
- **Models:** baseline (median), Linear Regression, Random Forest, Histogram Gradient Boosting, trained on log duration with an 80/20 train-test split and 5-fold cross-validation.
- **Metrics:** MAE (primary), RMSE, median absolute error, R² and RMSLE on the log scale.
- **Environment:** Jupyter / Google Colab notebook, GitHub repository for version control.

## 6. Expected outcomes
- A cleaned dataset with documented preprocessing.
- Labelled visualizations with interpretation of time and distance patterns.
- A model that clearly beats a naive baseline, with an honest account of its limitations.
- Technical report and demonstration material following Problem → Data → Analysis → Evidence → Insight → Conclusion.

## 7. Intended application
Estimated time of arrival (ETA) and fare estimation, driver dispatch planning and urban mobility analysis.
