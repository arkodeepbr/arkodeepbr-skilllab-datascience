"""Build and execute notebooks/nyc_taxi_trip_duration.ipynb.

The notebook cells are defined below. The script executes each code cell in one
shared namespace (capturing printed output and matplotlib figures) and writes a
standard .ipynb file with the outputs embedded, so the notebook opens with all
results visible in Jupyter, VS Code, Colab or GitHub.

Run from the repository root:  python scripts/build_notebook.py
"""
import base64
import contextlib
import io
import json
import os
import sys
import uuid
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
NB_DIR = ROOT / "notebooks"
NB_PATH = NB_DIR / "nyc_taxi_trip_duration.ipynb"

sys.path.insert(0, str(ROOT / "scripts"))
try:
    from observations import OBS  # written after the first run, holds interpretation text
except ImportError:
    OBS = {}

CELLS = []


def md(text):
    CELLS.append(("md", text))


def code(text):
    CELLS.append(("code", text))


def obs(key, fallback="_Observation pending._"):
    md(OBS.get(key, fallback))


# --------------------------------------------------------------------------- #
# Title
# --------------------------------------------------------------------------- #
md("""# NYC Taxi Trip Duration: Exploratory Analysis and Prediction

**Course:** Applied Data Science Skill Lab, CSE (Data Science), RVCE
**Mini-Project:** Exploratory Analysis and Prediction of Taxi Trip Duration using Python, Pandas and Scikit-learn
**Team members:** _add names and USNs_

This notebook follows the six-stage mini-project workflow:

**Problem Identification → Data Acquisition → Data Preparation → Exploratory Data Analysis → Visualization & Predictive Modelling → Interpretation & Presentation**""")

# --------------------------------------------------------------------------- #
# Stage 1
# --------------------------------------------------------------------------- #
md("""## Stage 1: Problem Identification

**Problem statement.** Taxi trip time in a large city depends on distance, time of day, day of week and location. Passengers, drivers and fleet operators cannot predict it reliably from distance alone because traffic and demand change through the day. This project analyses New York City yellow-taxi trips from January to June 2016 and builds a model that predicts **how long a trip will take (in seconds)** from information known at pickup time.

**Objectives**
1. Acquire and document the NYC Taxi Trip Duration dataset.
2. Clean and prepare the data, documenting every decision.
3. Explore how trip duration varies with distance, hour, weekday, month, vendor and passenger count.
4. Build and compare regression models using Scikit-learn.
5. Evaluate the models on unseen test data with MAE, RMSE and R², and interpret their usefulness and limitations.

**Analytical questions**
- Q1. How is trip duration distributed, and are the extreme values errors or real?
- Q2. How strongly does trip distance explain duration?
- Q3. How do demand and trip duration change across hours of the day, weekdays and months?
- Q4. Do vendor, passenger count or the store-and-forward flag matter?
- Q5. How accurately can duration be predicted from pickup-time information, and where does the model fail?

**Expected outcomes.** A cleaned dataset, a set of labelled visualizations with interpretation, and a regression model that clearly beats a naive baseline.

**Intended application.** Estimated-time-of-arrival (ETA) and fare estimation, driver dispatch planning, and urban mobility analysis.""")

# --------------------------------------------------------------------------- #
# Stage 2
# --------------------------------------------------------------------------- #
md("""## Stage 2: Data Acquisition

**Dataset:** NYC Taxi Trip Duration
**Source:** Kaggle competition *nyc-taxi-trip-duration* (https://www.kaggle.com/competitions/nyc-taxi-trip-duration/data). The trip records originate from the NYC Taxi & Limousine Commission (TLC) yellow-taxi data for 2016.
**Usage:** The data is used for academic purposes under the Kaggle competition rules. It contains no passenger names or other direct personal identifiers, and trip IDs are anonymous.

**Sample used here:** the full `train.csv` has about 1.46 million trips. Because of file-size limits, a **100,000-trip sample** of `train.csv` is used for the whole project (stored as `data/train_sample.csv`). The notebook also runs unchanged on the full file.""")

code("""import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams.update({"figure.dpi": 100, "axes.titlesize": 13, "axes.titleweight": "bold", "axes.labelsize": 11})
ACCENT = "#2b6cb0"
RANDOM_STATE = 42
pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 40)

# The notebook looks for the data in the usual places (repo, Colab, current folder).
CANDIDATES = [Path("../data/train_sample.csv"), Path("data/train_sample.csv"), Path("train_sample.csv"),
              Path("train.csv"), Path("/content/train.csv")]
DATA_PATH = next((p for p in CANDIDATES if p.exists()), None)
assert DATA_PATH is not None, "Put train_sample.csv (or train.csv) in the data/ folder."

REPO_MODE = Path("../data").exists()
FIG_DIR = Path("../figures") if REPO_MODE else Path("figures")
DATA_DIR = Path("../data") if REPO_MODE else Path(".")
OUT_DIR = Path("../outputs") if REPO_MODE else Path("outputs")
for d in (FIG_DIR, OUT_DIR):
    d.mkdir(exist_ok=True)
print("Data file:", DATA_PATH)""")

code("""# Optional (Google Colab only): download the full dataset straight from Kaggle.
# 1) Upload your kaggle.json API token, 2) accept the competition rules on Kaggle, 3) uncomment:
# !pip install -q kaggle
# !kaggle competitions download -c nyc-taxi-trip-duration && unzip -o nyc-taxi-trip-duration.zip train.zip && unzip -o train.zip
print("Skipped: using the local sample.")""")

code("""raw = pd.read_csv(DATA_PATH)
print(f"Records: {raw.shape[0]:,}   Attributes: {raw.shape[1]}")
display(raw.head())""")

code("""dictionary = pd.DataFrame({
    "Variable": ["id", "vendor_id", "pickup_datetime", "dropoff_datetime", "passenger_count",
                 "pickup_longitude", "pickup_latitude", "dropoff_longitude", "dropoff_latitude",
                 "store_and_fwd_flag", "trip_duration"],
    "Type": ["identifier", "categorical (1/2)", "datetime", "datetime", "numerical (discrete)",
             "numerical", "numerical", "numerical", "numerical", "categorical (Y/N)", "numerical (target)"],
    "Description": ["Unique trip identifier",
                    "Taxi technology provider that supplied the record",
                    "Date and time the meter was engaged",
                    "Date and time the meter was disengaged (not available when predicting)",
                    "Number of passengers in the vehicle (driver-entered)",
                    "Longitude where the meter was engaged", "Latitude where the meter was engaged",
                    "Longitude where the meter was disengaged", "Latitude where the meter was disengaged",
                    "Y = trip record was held in vehicle memory before being sent to the vendor (no connection)",
                    "Trip duration in seconds (dropoff minus pickup)"]})
display(dictionary)

pick = pd.to_datetime(raw["pickup_datetime"])
print("\\nTime period of pickups:", pick.min(), "to", pick.max())
print("\\nData types:")
print(raw.dtypes.to_string())""")

md("""**Limitations and constraints of the dataset**
- Covers only **six months (Jan to Jun 2016)** of one taxi type; patterns for other seasons, years or ride-hailing services are not represented.
- No weather, traffic, road-network or event information, which strongly affect trip time.
- `passenger_count` is entered by the driver and can be wrong (it contains 0).
- GPS coordinates are only start and end points, not the route taken.
- `dropoff_datetime` is simply pickup + duration, so it must **not** be used as a model input (target leakage).""")

# --------------------------------------------------------------------------- #
# Stage 3
# --------------------------------------------------------------------------- #
md("""## Stage 3: Data Preparation

### 3.1 Inspect structure and data types""")

code("""raw.info()""")

md("### 3.2 Missing values, duplicates and consistency checks")

code("""print("Missing values per column:")
print(raw.isna().sum().to_string())
print("\\nFully duplicated rows :", raw.duplicated().sum())
print("Duplicated trip ids   :", raw["id"].duplicated().sum())

pickup = pd.to_datetime(raw["pickup_datetime"])
dropoff = pd.to_datetime(raw["dropoff_datetime"])
print("\\nDropoff before/at pickup          :", (dropoff <= pickup).sum())
print("Duration != dropoff - pickup (sec):", ((dropoff - pickup).dt.total_seconds() != raw["trip_duration"]).sum())
print("\\nvendor_id values        :", raw["vendor_id"].unique().tolist())
print("store_and_fwd_flag      :", sorted(raw["store_and_fwd_flag"].unique()))
print("passenger_count values  :", sorted(raw["passenger_count"].unique().tolist()))""")

md("""**Decision:** there are no missing values and no duplicates, and the recorded duration matches the timestamps exactly, so no imputation or de-duplication is needed. The remaining quality risk is *implausible values* (zero passengers, GPS points outside NYC, extreme or impossible durations), checked next.

### 3.3 Fix data formats and create derived variables
Derived variables (feature engineering):
- **Time features:** pickup hour, weekday, month, weekend flag, weekday rush-hour flag (07:00–10:00 and 16:00–19:00).
- **Distance features:** straight-line (haversine) distance, Manhattan-style distance (north-south plus east-west legs), and compass bearing, since taxis travel on a street grid.
- **log trip duration:** the raw duration is heavily right-skewed, so the model is trained on `log1p(duration)`.""")

code("""def haversine(lat1, lon1, lat2, lon2):
    \"\"\"Great-circle distance in km.\"\"\"
    r = 6371.0088
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def bearing(lat1, lon1, lat2, lon2):
    \"\"\"Initial compass bearing (degrees, 0-360).\"\"\"
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    x = np.sin(dlon) * np.cos(lat2)
    y = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
    return (np.degrees(np.arctan2(x, y)) + 360) % 360


def add_features(d):
    \"\"\"Add derived variables. Works on training data and on new trips (used again in Stage 5B).\"\"\"
    d = d.copy()
    d["pickup_datetime"] = pd.to_datetime(d["pickup_datetime"])
    d["pickup_hour"] = d["pickup_datetime"].dt.hour
    d["pickup_weekday"] = d["pickup_datetime"].dt.weekday          # Monday = 0
    d["pickup_month"] = d["pickup_datetime"].dt.month
    d["pickup_date"] = d["pickup_datetime"].dt.date
    d["is_weekend"] = (d["pickup_weekday"] >= 5).astype(int)
    d["is_rush_hour"] = ((d["is_weekend"] == 0) &
                         (d["pickup_hour"].between(7, 9) | d["pickup_hour"].between(16, 18))).astype(int)
    d["store_fwd"] = (d["store_and_fwd_flag"] == "Y").astype(int)
    d["haversine_km"] = haversine(d["pickup_latitude"], d["pickup_longitude"],
                                  d["dropoff_latitude"], d["dropoff_longitude"])
    d["manhattan_km"] = (haversine(d["pickup_latitude"], d["pickup_longitude"], d["pickup_latitude"], d["dropoff_longitude"])
                         + haversine(d["pickup_latitude"], d["dropoff_longitude"], d["dropoff_latitude"], d["dropoff_longitude"]))
    d["bearing"] = bearing(d["pickup_latitude"], d["pickup_longitude"], d["dropoff_latitude"], d["dropoff_longitude"])
    d["log_haversine"] = np.log1p(d["haversine_km"])
    return d


df = add_features(raw)
df["dropoff_datetime"] = pd.to_datetime(df["dropoff_datetime"])
weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
df["weekday_name"] = pd.Categorical(df["pickup_weekday"].map(dict(enumerate(weekday_names))),
                                    categories=weekday_names, ordered=True)
# These two use the target, so they are for analysis only and are never model inputs:
df["log_duration"] = np.log1p(df["trip_duration"])
df["speed_kmh"] = df["haversine_km"] / (df["trip_duration"] / 3600)
display(df[["pickup_datetime", "pickup_hour", "weekday_name", "is_rush_hour", "haversine_km",
            "manhattan_km", "bearing", "trip_duration", "speed_kmh"]].head())""")

md("""### 3.4 Identify and handle implausible records
Rules below are applied only to records that are very likely **recording errors**, and the number removed by each rule is reported. Unusually long (but plausible) trips are *not* removed here; they are investigated in Stage 4 with the IQR method.""")

code("""# Approximate bounding box around New York City
in_box = lambda lon, lat: lon.between(-74.30, -73.60) & lat.between(40.45, 41.00)
outside_nyc = ~(in_box(df["pickup_longitude"], df["pickup_latitude"]) &
                in_box(df["dropoff_longitude"], df["dropoff_latitude"]))

rules = {
    "0 passengers": df["passenger_count"].eq(0),
    "pickup/dropoff outside NYC bounding box": outside_nyc,
    "duration < 60 s (cancelled / meter error)": df["trip_duration"] < 60,
    "duration > 3 h (meter left running)": df["trip_duration"] > 3 * 3600,
    "implied speed > 120 km/h (impossible in city)": df["speed_kmh"] > 120,
}
summary = pd.DataFrame({"records_flagged": {k: int(v.sum()) for k, v in rules.items()}})
summary["percent_of_data"] = (summary["records_flagged"] / len(df) * 100).round(3)
display(summary)
summary.to_csv(OUT_DIR / "cleaning_rules_summary.csv")

invalid = np.logical_or.reduce(list(rules.values()))
print(f"\\nUnique records removed: {invalid.sum():,} of {len(df):,} ({invalid.mean():.2%})")
clean = df.loc[~invalid].reset_index(drop=True)
print(f"Cleaned dataset: {clean.shape[0]:,} records")""")

md("""**Decisions and reasons**
- **0 passengers:** a trip with nobody in the car is not a valid passenger trip.
- **Outside NYC box:** coordinates far from the city (e.g. other states) are GPS errors or very atypical long-distance trips that this model is not designed for.
- **< 60 s and > 3 h:** such durations are not realistic urban taxi trips (cancelled fares, meter left running).
- **Speed > 120 km/h:** physically impossible in the city and indicates a bad coordinate or timestamp.
- Short, slow or round-trip journeys that pass these rules are **kept**.

### 3.5 Numerical vs categorical variables and feature selection""")

code("""numerical = ["passenger_count", "pickup_longitude", "pickup_latitude", "dropoff_longitude", "dropoff_latitude",
             "haversine_km", "manhattan_km", "bearing", "pickup_hour", "pickup_weekday", "pickup_month"]
categorical = ["vendor_id", "store_and_fwd_flag", "is_weekend", "is_rush_hour"]
print("Numerical  :", numerical)
print("Categorical:", categorical)

FEATURES = ["vendor_id", "passenger_count", "store_fwd",
            "pickup_longitude", "pickup_latitude", "dropoff_longitude", "dropoff_latitude",
            "pickup_hour", "pickup_weekday", "pickup_month", "is_weekend", "is_rush_hour",
            "haversine_km", "log_haversine", "manhattan_km", "bearing"]
TARGET = "trip_duration"
excluded = {"id": "identifier, no predictive meaning",
            "dropoff_datetime": "equals pickup + duration, so it leaks the target",
            "speed_kmh / log_duration": "computed from the target, analysis only",
            "pickup_datetime / pickup_date": "replaced by hour, weekday, month features"}
print("\\nModel input features (%d): %s" % (len(FEATURES), FEATURES))
print("Target:", TARGET)
print("\\nExcluded variables:")
for k, v in excluded.items():
    print(f"  - {k}: {v}")""")

code("""cleaned_path = DATA_DIR / "train_cleaned.csv"
clean.drop(columns=["pickup_date", "weekday_name"]).to_csv(cleaned_path, index=False)
print("Saved cleaned dataset ->", cleaned_path, f"({len(clean):,} rows, {clean.shape[1] - 2} columns)")""")

# --------------------------------------------------------------------------- #
# Stage 4
# --------------------------------------------------------------------------- #
md("""## Stage 4: Exploratory Data Analysis (EDA)

### 4.1 Descriptive statistics (mean, median, mode, standard deviation, min, max, quartiles)""")

code("""stat_cols = ["trip_duration", "haversine_km", "manhattan_km", "speed_kmh", "passenger_count", "pickup_hour"]
desc = clean[stat_cols].describe(percentiles=[0.25, 0.5, 0.75]).T
desc["mode"] = clean[stat_cols].mode().iloc[0]
desc["skewness"] = clean[stat_cols].skew()
eda_desc = desc[["count", "mean", "50%", "mode", "std", "min", "25%", "75%", "max", "skewness"]].rename(columns={"50%": "median", "25%": "Q1 (25%)", "75%": "Q3 (75%)"}).round(3)
display(eda_desc)
eda_desc.to_csv(OUT_DIR / "eda_descriptive_statistics.csv")""")

md("### 4.2 Frequency tables for categorical variables")

code("""freq_frames = []
for col in ["vendor_id", "passenger_count", "store_and_fwd_flag", "weekday_name", "pickup_month", "is_rush_hour"]:
    vc = clean[col].value_counts().sort_index()
    table = pd.DataFrame({"count": vc, "percent": (vc / len(clean) * 100).round(2)})
    print(f"--- {col} ---")
    print(table.to_string(), "\\n")
    freq_frames.append(table.reset_index().rename(columns={col: "value"}).assign(variable=col)[["variable", "value", "count", "percent"]])
pd.concat(freq_frames).to_csv(OUT_DIR / "eda_frequency_tables.csv", index=False)""")

md("### 4.3 Distribution of numerical variables")

code("""dist = pd.DataFrame({"skewness": clean[["trip_duration", "log_duration", "haversine_km"]].skew(),
                     "kurtosis": clean[["trip_duration", "log_duration", "haversine_km"]].kurt()})
display(dist.round(3))
for q in (0.50, 0.90, 0.95, 0.99):
    print(f"{int(q*100)}th percentile of trip_duration: {clean['trip_duration'].quantile(q):,.0f} s ({clean['trip_duration'].quantile(q)/60:.1f} min)")""")

md("### 4.4 Outlier detection with the IQR method (investigated, not automatically removed)")

code("""def iqr_summary(s):
    q1, q3 = s.quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    n = int(((s < lo) | (s > hi)).sum())
    return pd.Series({"Q1": q1, "Q3": q3, "IQR": iqr, "lower_fence": lo, "upper_fence": hi,
                      "n_outliers": n, "percent": 100 * n / len(s)})

iqr_table = pd.DataFrame({c: iqr_summary(clean[c]) for c in ["trip_duration", "haversine_km", "manhattan_km", "speed_kmh", "passenger_count"]}).T
display(iqr_table.round(2))
iqr_table.round(3).to_csv(OUT_DIR / "eda_iqr_outliers.csv")

# Investigate: are the 'outlier' durations real or errors?
fence = iqr_table.loc["trip_duration", "upper_fence"]
long_trips = clean[clean["trip_duration"] > fence]
normal = clean[clean["trip_duration"] <= fence]
cmp = pd.DataFrame({
    "typical trips": [len(normal), normal["trip_duration"].median(), normal["haversine_km"].median(), normal["speed_kmh"].median()],
    "IQR-outlier trips": [len(long_trips), long_trips["trip_duration"].median(), long_trips["haversine_km"].median(), long_trips["speed_kmh"].median()]},
    index=["count", "median duration (s)", "median distance (km)", "median speed (km/h)"])
display(cmp.round(2))
print(f"\\nShare of IQR-outlier trips that are longer than 5 km: {(long_trips['haversine_km'] > 5).mean():.1%}")
print(f"Share of typical trips longer than 5 km            : {(normal['haversine_km'] > 5).mean():.1%}")
print(f"Share of outlier trips that start/end at airports (approx. JFK/LGA zones): ", end="")
air = lambda lon, lat: ((lon.between(-73.83, -73.74) & lat.between(40.62, 40.67)) | (lon.between(-73.89, -73.85) & lat.between(40.76, 40.79)))
is_airport = air(long_trips["pickup_longitude"], long_trips["pickup_latitude"]) | air(long_trips["dropoff_longitude"], long_trips["dropoff_latitude"])
print(f"{is_airport.mean():.1%}")""")

obs("outliers")

obs("eda_summary")

# --------------------------------------------------------------------------- #
# Stage 5A
# --------------------------------------------------------------------------- #
md("""## Stage 5A: Data Visualization (Matplotlib and Seaborn)

Each chart answers one of the analytical questions from Stage 1.""")

code("""# Figure 1 - Distribution of trip duration (Q1)
fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
ax[0].hist(clean["trip_duration"] / 60, bins=80, color=ACCENT, edgecolor="white")
ax[0].set(title="Trip duration is right-skewed", xlabel="Trip duration (minutes)", ylabel="Number of trips")
ax[1].hist(clean["log_duration"], bins=80, color=ACCENT, edgecolor="white")
ax[1].set(title="After log transform: close to symmetric", xlabel="log(1 + duration in seconds)", ylabel="Number of trips")
plt.tight_layout(); plt.savefig(FIG_DIR / "fig01_duration_distribution.png", dpi=130, bbox_inches="tight"); plt.show()""")

code("""# Figure 2 - Spread and outliers (box plots) (Q1)
fig, ax = plt.subplots(1, 3, figsize=(14, 4.5))
sns.boxplot(y=clean["trip_duration"] / 60, ax=ax[0], color=ACCENT, flierprops={"markersize": 2, "alpha": 0.4})
ax[0].set(title="Trip duration", ylabel="Minutes")
sns.boxplot(y=clean["haversine_km"], ax=ax[1], color=ACCENT, flierprops={"markersize": 2, "alpha": 0.4})
ax[1].set(title="Straight-line distance", ylabel="Kilometres")
sns.boxplot(data=clean, x="passenger_count", y=clean["trip_duration"] / 60, ax=ax[2], color=ACCENT, flierprops={"markersize": 2, "alpha": 0.4})
ax[2].set(title="Duration by passenger count", xlabel="Passengers", ylabel="Minutes", ylim=(0, 60))
plt.tight_layout(); plt.savefig(FIG_DIR / "fig02_boxplots.png", dpi=130, bbox_inches="tight"); plt.show()""")

code("""# Figure 3 - Distance vs duration (Q2)
samp = clean.sample(6000, random_state=RANDOM_STATE)
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.scatter(samp["haversine_km"], samp["trip_duration"] / 60, s=6, alpha=0.35, color=ACCENT)
ax.set(title="Longer distance means longer trips, but with wide scatter", xlabel="Straight-line distance (km)",
       ylabel="Trip duration (minutes)", xlim=(0, 30), ylim=(0, 120))
r = clean[["haversine_km", "trip_duration"]].corr().iloc[0, 1]
r_log = clean[["log_haversine", "log_duration"]].corr().iloc[0, 1]
ax.text(0.97, 0.05, f"Pearson r = {r:.2f}  (log-log r = {r_log:.2f})", transform=ax.transAxes, ha="right",
        bbox=dict(boxstyle="round", fc="white", ec="grey"))
plt.tight_layout(); plt.savefig(FIG_DIR / "fig03_distance_vs_duration.png", dpi=130, bbox_inches="tight"); plt.show()""")

code("""# Figure 4 - Demand and duration across the day (Q3)
hourly = clean.groupby("pickup_hour").agg(trips=("id", "size"), mean_min=("trip_duration", lambda s: s.mean() / 60),
                                          median_min=("trip_duration", lambda s: s.median() / 60))
fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
ax[0].bar(hourly.index, hourly["trips"], color=ACCENT)
ax[0].set(title="Taxi demand by hour of day", xlabel="Pickup hour", ylabel="Number of trips", xticks=range(0, 24, 2))
ax[1].plot(hourly.index, hourly["mean_min"], marker="o", color=ACCENT, label="Mean")
ax[1].plot(hourly.index, hourly["median_min"], marker="s", color="#dd6b20", label="Median")
ax[1].set(title="Trip duration by hour of day", xlabel="Pickup hour", ylabel="Minutes", xticks=range(0, 24, 2))
ax[1].legend()
plt.tight_layout(); plt.savefig(FIG_DIR / "fig04_hourly_demand_duration.png", dpi=130, bbox_inches="tight"); plt.show()
display(hourly.round(2).T)""")

code("""# Figure 5 - Weekday patterns and weekday x hour heatmap (Q3)
wd = clean.groupby("weekday_name", observed=True).agg(trips=("id", "size"), mean_min=("trip_duration", lambda s: s.mean() / 60))
heat = clean.pivot_table(index="weekday_name", columns="pickup_hour", values="trip_duration", aggfunc="median", observed=True) / 60
fig, ax = plt.subplots(1, 2, figsize=(15, 4.8), gridspec_kw={"width_ratios": [1, 2]})
ax[0].bar(wd.index.astype(str), wd["trips"], color=ACCENT)
ax[0].set(title="Trips by weekday", xlabel="Weekday", ylabel="Number of trips")
sns.heatmap(heat, cmap="YlOrRd", ax=ax[1], cbar_kws={"label": "Median duration (min)"})
ax[1].set(title="Median trip duration by weekday and hour", xlabel="Pickup hour", ylabel="")
plt.tight_layout(); plt.savefig(FIG_DIR / "fig05_weekday_patterns.png", dpi=130, bbox_inches="tight"); plt.show()
display(wd.round(2).T)""")

code("""# Figure 6 - Trend over time (line chart) (Q3)
daily = clean.groupby("pickup_date").agg(trips=("id", "size"), mean_min=("trip_duration", lambda s: s.mean() / 60))
daily.index = pd.to_datetime(daily.index)
fig, ax = plt.subplots(2, 1, figsize=(13, 7), sharex=True)
ax[0].plot(daily.index, daily["trips"], color=ACCENT)
ax[0].set(title="Daily number of trips in the sample (Jan to Jun 2016)", ylabel="Trips per day")
ax[1].plot(daily.index, daily["mean_min"], color="#dd6b20")
ax[1].set(title="Daily mean trip duration", ylabel="Minutes", xlabel="Date")
plt.tight_layout(); plt.savefig(FIG_DIR / "fig06_daily_trend.png", dpi=130, bbox_inches="tight"); plt.show()
print("Lowest 3 days by trip count:")
print(daily.nsmallest(3, "trips").round(2).to_string())
monthly = clean.groupby("pickup_month").agg(trips=("id", "size"), mean_min=("trip_duration", lambda s: s.mean() / 60))
print("\\nBy month:"); print(monthly.round(2).to_string())""")

code("""# Figure 7 - Where do trips start? (Q3/Q4)
fig, ax = plt.subplots(1, 2, figsize=(13, 6))
hb = ax[0].hexbin(clean["pickup_longitude"], clean["pickup_latitude"], gridsize=130, bins="log", cmap="viridis",
                  extent=(-74.05, -73.75, 40.62, 40.88), mincnt=1)
ax[0].set(title="Pickup density (log scale)", xlabel="Longitude", ylabel="Latitude"); plt.colorbar(hb, ax=ax[0], label="Trips per hexagon (log scale)")
hb2 = ax[1].hexbin(clean["dropoff_longitude"], clean["dropoff_latitude"], gridsize=130, bins="log", cmap="viridis",
                   extent=(-74.05, -73.75, 40.62, 40.88), mincnt=1)
ax[1].set(title="Dropoff density (log scale)", xlabel="Longitude", ylabel="Latitude"); plt.colorbar(hb2, ax=ax[1], label="Trips per hexagon (log scale)")
plt.tight_layout(); plt.savefig(FIG_DIR / "fig07_pickup_dropoff_density.png", dpi=130, bbox_inches="tight"); plt.show()""")

code("""# Figure 8 - Categorical comparisons: vendor, store-and-forward flag, rush hour (Q4)
fig, ax = plt.subplots(1, 3, figsize=(14, 4.5))
for a, col, title in zip(ax, ["vendor_id", "store_and_fwd_flag", "is_rush_hour"],
                         ["Vendor", "Store-and-forward flag", "Weekday rush hour (1 = yes)"]):
    g = clean.groupby(col)["trip_duration"].agg(["mean", "median"]) / 60
    g.plot(kind="bar", ax=a, color=[ACCENT, "#dd6b20"], rot=0)
    a.set(title=title, xlabel="", ylabel="Minutes")
plt.tight_layout(); plt.savefig(FIG_DIR / "fig08_category_comparison.png", dpi=130, bbox_inches="tight"); plt.show()""")

code("""# Figure 9 - Correlation heatmap of numerical variables (Q2, Q4)
corr_cols = ["trip_duration", "haversine_km", "manhattan_km", "passenger_count", "pickup_hour", "pickup_weekday",
             "pickup_month", "is_rush_hour", "vendor_id", "pickup_latitude", "pickup_longitude", "dropoff_latitude", "dropoff_longitude"]
corr = clean[corr_cols].corr()
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1, ax=ax, annot_kws={"size": 8})
ax.set_title("Correlation matrix of numerical variables")
plt.tight_layout(); plt.savefig(FIG_DIR / "fig09_correlation_heatmap.png", dpi=130, bbox_inches="tight"); plt.show()
print("Correlation with trip_duration (strongest first):")
print(corr["trip_duration"].drop("trip_duration").sort_values(key=abs, ascending=False).round(3).to_string())""")

obs("viz")

# --------------------------------------------------------------------------- #
# Stage 5B
# --------------------------------------------------------------------------- #
md("""## Stage 5B: Predictive Modelling

**Load the dataset and identify input features and target variable.**
The data is already loaded in a Pandas DataFrame (`clean`). The **target** is `trip_duration` (seconds), a continuous number, so this is a **regression** problem. The **inputs** are the 16 pickup-time features chosen in Stage 3.5.""")

code("""X = clean[FEATURES]
y = clean[TARGET]
print("Input matrix  :", X.shape)
print("Target vector :", y.shape)
print("\\nFeatures:", list(X.columns))
print("Task type: regression (continuous target in seconds)")""")

md("""**Preprocess the dataset and divide it into training and testing sets.**
Preprocessing was done in Stage 3 (cleaning, derived features). Here the data is split **80% training / 20% testing** with a fixed random seed. The test set is never used to fit any model. The target is modelled on the log scale (`log1p`) because durations are heavily right-skewed, and predictions are converted back to seconds for all reported metrics.""")

code("""from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=RANDOM_STATE)
y_train_log, y_test_log = np.log1p(y_train), np.log1p(y_test)
print(f"Training set: {X_train.shape[0]:,} trips")
print(f"Testing set : {X_test.shape[0]:,} trips")
print(f"\\nMean duration  train: {y_train.mean():.1f} s   test: {y_test.mean():.1f} s  (similar, so the split is representative)")""")

md("""**Train regression models using Scikit-learn.**
Four models are compared, from simple to flexible:
1. **Baseline:** always predicts the median training duration (a model must beat this to be useful).
2. **Linear Regression** on standardised features (interpretable, but assumes straight-line relationships).
3. **Random Forest Regressor** (many decision trees averaged).
4. **Histogram Gradient Boosting Regressor** (trees built one after another, each correcting the previous errors).""")

code("""import time
from sklearn.dummy import DummyRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor

models = {
    "Baseline (median)": DummyRegressor(strategy="median"),
    "Linear Regression": make_pipeline(StandardScaler(), LinearRegression()),
    "Random Forest": RandomForestRegressor(n_estimators=100, min_samples_leaf=5, max_features=0.6,
                                           n_jobs=-1, random_state=RANDOM_STATE),
    "Gradient Boosting": HistGradientBoostingRegressor(learning_rate=0.08, max_iter=500, max_leaf_nodes=48,
                                                       early_stopping=True, validation_fraction=0.1,
                                                       n_iter_no_change=25, random_state=RANDOM_STATE),
}
fitted, fit_seconds = {}, {}
for name, model in models.items():
    t0 = time.time()
    model.fit(X_train, y_train_log)
    fitted[name], fit_seconds[name] = model, time.time() - t0
    print(f"{name:20s} trained in {fit_seconds[name]:5.1f} s")""")

md("""**Use the trained models to predict outcomes for the test records.**""")

code("""predictions = {name: np.expm1(m.predict(X_test)).clip(min=1) for name, m in fitted.items()}   # back to seconds
print({k: v[:3].round(0).tolist() for k, v in predictions.items()})""")

md("""**Evaluate the predictions using appropriate metrics.**
- **MAE** (mean absolute error, seconds): the average size of the error, the main metric for regression in this lab.
- **RMSE** (seconds): penalises large errors more heavily.
- **Median AE** (seconds): the typical error, not distorted by a few extreme trips.
- **R² (log scale)** and **RMSLE**: how well relative errors are explained (RMSLE is the metric used in the original Kaggle competition).""")

code("""from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score

rows = []
for name, pred in predictions.items():
    rows.append({"Model": name,
                 "MAE (s)": mean_absolute_error(y_test, pred),
                 "RMSE (s)": mean_squared_error(y_test, pred) ** 0.5,
                 "Median AE (s)": median_absolute_error(y_test, pred),
                 "R2 (log scale)": r2_score(y_test_log, np.log1p(pred)),
                 "RMSLE": mean_squared_error(y_test_log, np.log1p(pred)) ** 0.5,
                 "Train time (s)": fit_seconds[name]})
results = pd.DataFrame(rows).set_index("Model").round(3)
display(results)
results.to_csv(OUT_DIR / "model_comparison.csv")

best_name = results.drop(index="Baseline (median)")["MAE (s)"].idxmin()
base_mae = results.loc["Baseline (median)", "MAE (s)"]
best_mae = results.loc[best_name, "MAE (s)"]
print(f"\\nBest model by MAE: {best_name}  (MAE {best_mae:.1f} s = {best_mae/60:.2f} min)")
print(f"Improvement over baseline: {(1 - best_mae / base_mae):.1%}")""")

code("""fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
plot_df = results.drop(index="Baseline (median)").reset_index()
sns.barplot(data=plot_df, x="Model", y="MAE (s)", color=ACCENT, ax=ax[0])
ax[0].axhline(base_mae, color="#c53030", ls="--", label=f"Baseline MAE = {base_mae:.0f} s")
ax[0].set(title="Test-set MAE by model (lower is better)", xlabel="", ylabel="MAE (seconds)"); ax[0].legend()
for p in ax[0].patches:
    ax[0].annotate(f"{p.get_height():.0f}", (p.get_x() + p.get_width() / 2, p.get_height()), ha="center", va="bottom")
sns.barplot(data=plot_df, x="Model", y="R2 (log scale)", color="#2f855a", ax=ax[1])
ax[1].set(title="R² on log scale (higher is better)", xlabel="", ylabel="R²", ylim=(0, 1))
for p in ax[1].patches:
    ax[1].annotate(f"{p.get_height():.3f}", (p.get_x() + p.get_width() / 2, p.get_height()), ha="center", va="bottom")
plt.tight_layout(); plt.savefig(FIG_DIR / "fig10_model_comparison.png", dpi=130, bbox_inches="tight"); plt.show()""")

md("""**Compare predicted with actual values and display them in a structured table.**
The table below uses 15 random test trips and the best model.""")

code("""best_pred = predictions[best_name]
avp = pd.DataFrame({
    "trip_id": clean.loc[X_test.index, "id"].values,
    "pickup_time": clean.loc[X_test.index, "pickup_datetime"].dt.strftime("%a %H:%M").values,
    "distance_km": clean.loc[X_test.index, "haversine_km"].round(2).values,
    "actual_sec": y_test.values,
    "predicted_sec": best_pred.round(0),
})
avp["error_sec"] = (avp["predicted_sec"] - avp["actual_sec"]).round(0)
avp["abs_error_sec"] = avp["error_sec"].abs()
avp["abs_error_%"] = (avp["abs_error_sec"] / avp["actual_sec"] * 100).round(1)
avp["actual_min"] = (avp["actual_sec"] / 60).round(1)
avp["predicted_min"] = (avp["predicted_sec"] / 60).round(1)
avp.to_csv(OUT_DIR / "actual_vs_predicted_test.csv", index=False)      # full test set saved
print(f"Model: {best_name}   |   showing 15 of {len(avp):,} test trips (full table saved to outputs/)\\n")
display(avp.sample(15, random_state=7).reset_index(drop=True))""")

code("""# Visual comparison of predicted and actual durations
fig, ax = plt.subplots(1, 2, figsize=(13, 5.5))
s = avp.sample(5000, random_state=RANDOM_STATE)
ax[0].scatter(s["actual_sec"] / 60, s["predicted_sec"] / 60, s=6, alpha=0.3, color=ACCENT)
lim = 60
ax[0].plot([0, lim], [0, lim], color="#c53030", ls="--", label="Perfect prediction")
ax[0].set(title=f"Actual vs predicted ({best_name})", xlabel="Actual duration (min)", ylabel="Predicted duration (min)", xlim=(0, lim), ylim=(0, lim)); ax[0].legend()
resid = (avp["predicted_sec"] - avp["actual_sec"]) / 60
ax[1].hist(resid.clip(-30, 30), bins=80, color=ACCENT, edgecolor="white")
ax[1].axvline(0, color="#c53030", ls="--")
ax[1].set(title="Prediction error (predicted minus actual)", xlabel="Error (minutes, clipped at ±30)", ylabel="Number of test trips")
plt.tight_layout(); plt.savefig(FIG_DIR / "fig11_actual_vs_predicted.png", dpi=130, bbox_inches="tight"); plt.show()
within = lambda m: (avp["abs_error_sec"] <= m * 60).mean()
print(f"Predictions within 2 min of actual: {within(2):.1%}   within 5 min: {within(5):.1%}   within 10 min: {within(10):.1%}")""")

md("""### Where does the model do well and badly? (error analysis)""")

code("""err = avp.copy()
err["hour"] = clean.loc[X_test.index, "pickup_hour"].values
err["dist_band"] = pd.cut(err["distance_km"], [0, 1, 2, 4, 8, 15, 100], labels=["<1 km", "1-2 km", "2-4 km", "4-8 km", "8-15 km", ">15 km"])
by_dist = err.groupby("dist_band", observed=True).agg(trips=("trip_id", "size"), mean_actual_min=("actual_min", "mean"),
                                                      MAE_sec=("abs_error_sec", "mean"), MAPE_pct=("abs_error_%", "mean"))
display(by_dist.round(1))
by_hour = err.groupby("hour").agg(MAE_sec=("abs_error_sec", "mean"), MAPE_pct=("abs_error_%", "mean"))

fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
ax[0].bar(by_dist.index.astype(str), by_dist["MAE_sec"], color=ACCENT)
ax[0].set(title="Error grows with trip distance", xlabel="Straight-line distance", ylabel="MAE (seconds)")
ax[1].plot(by_hour.index, by_hour["MAE_sec"], marker="o", color="#dd6b20")
ax[1].set(title="Error by pickup hour", xlabel="Pickup hour", ylabel="MAE (seconds)", xticks=range(0, 24, 2))
plt.tight_layout(); plt.savefig(FIG_DIR / "fig12_error_analysis.png", dpi=130, bbox_inches="tight"); plt.show()""")

code("""# Which features drive the predictions? (permutation importance on a test subset)
from sklearn.inspection import permutation_importance

sub = X_test.sample(5000, random_state=RANDOM_STATE)
pi = permutation_importance(fitted[best_name], sub, np.log1p(y_test.loc[sub.index]), n_repeats=5,
                            random_state=RANDOM_STATE, scoring="neg_mean_squared_error")
imp = pd.Series(pi.importances_mean, index=X_test.columns).sort_values()
fig, ax = plt.subplots(figsize=(8, 6))
imp.plot(kind="barh", color=ACCENT, ax=ax)
ax.set(title=f"Feature importance ({best_name})", xlabel="Increase in squared log error when the feature is shuffled")
plt.tight_layout(); plt.savefig(FIG_DIR / "fig13_feature_importance.png", dpi=130, bbox_inches="tight"); plt.show()
print((imp / imp.sum() * 100).sort_values(ascending=False).round(1).head(8).to_string())""")

md("""**New input observations.** The trained model can also predict for trips that are *not* in the dataset. Three hypothetical trips are entered below using only information known at pickup time.""")

code("""new_trips = pd.DataFrame({
    "route": ["Times Square to Wall Street, Wed 08:30", "Times Square to Wall Street, Sun 03:00", "Grand Central to JFK Airport, Fri 17:30"],
    "vendor_id": [2, 2, 2], "passenger_count": [1, 1, 2],
    "pickup_datetime": ["2016-05-11 08:30:00", "2016-05-15 03:00:00", "2016-05-13 17:30:00"],
    "pickup_longitude": [-73.9855, -73.9855, -73.9772], "pickup_latitude": [40.7580, 40.7580, 40.7527],
    "dropoff_longitude": [-74.0088, -74.0088, -73.7781], "dropoff_latitude": [40.7060, 40.7060, 40.6413],
    "store_and_fwd_flag": ["N", "N", "N"]})
new_feat = add_features(new_trips)
new_pred = np.expm1(fitted[best_name].predict(new_feat[FEATURES]))
display(pd.DataFrame({"route": new_trips["route"], "distance_km": new_feat["haversine_km"].round(1),
                      "predicted_min": (new_pred / 60).round(1)}))""")

code("""# Quick robustness check: 5-fold cross-validation of the best model on the training set
from sklearn.model_selection import cross_val_score
cv = cross_val_score(models[best_name].__class__(**models[best_name].get_params()), X_train, y_train_log,
                     cv=5, scoring="neg_root_mean_squared_error", n_jobs=1)
print(f"{best_name}: 5-fold CV RMSLE = {-cv.mean():.4f} (+/- {cv.std():.4f}),  held-out test RMSLE = {results.loc[best_name, 'RMSLE']:.4f}")
print("Similar CV and test scores indicate the model is not overfitted to a lucky split.")""")

obs("modelling")

# --------------------------------------------------------------------------- #
# Stage 6
# --------------------------------------------------------------------------- #
md("""## Stage 6: Interpretation, Documentation and Presentation

**Interpretation of results, usefulness and limitations of the predictions.**""")

obs("interpretation")

code("""# Save a one-page summary of key numbers for the report and slides
summary_out = {
    "records_raw": int(len(raw)), "records_clean": int(len(clean)), "records_removed": int(len(raw) - len(clean)),
    "median_duration_min": round(clean["trip_duration"].median() / 60, 2),
    "mean_duration_min": round(clean["trip_duration"].mean() / 60, 2),
    "corr_distance_duration": round(float(clean[["haversine_km", "trip_duration"]].corr().iloc[0, 1]), 3),
    "best_model": best_name, "best_MAE_sec": round(float(best_mae), 1), "baseline_MAE_sec": round(float(base_mae), 1),
    "best_R2_log": float(results.loc[best_name, "R2 (log scale)"]), "best_RMSLE": float(results.loc[best_name, "RMSLE"]),
}
import json
Path(OUT_DIR / "key_results.json").write_text(json.dumps(summary_out, indent=2))
print(json.dumps(summary_out, indent=2))""")

md("""### References
1. Kaggle. *New York City Taxi Trip Duration* competition. https://www.kaggle.com/competitions/nyc-taxi-trip-duration
2. NYC Taxi & Limousine Commission. *TLC Trip Record Data* (yellow taxi, 2016). https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
3. Pedregosa et al. (2011). Scikit-learn: Machine Learning in Python. *JMLR* 12, 2825–2830.
4. McKinney, W. (2010). Data Structures for Statistical Computing in Python (Pandas). *Proc. SciPy 2010*.
5. Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. *Computing in Science & Engineering* 9(3).
6. Waskom, M. (2021). seaborn: statistical data visualization. *JOSS* 6(60), 3021.""")


# --------------------------------------------------------------------------- #
# Runner: execute cells, capture stdout + figures, write .ipynb
# --------------------------------------------------------------------------- #
def lines(text):
    return text.strip("\n").splitlines(keepends=True)


def run():
    warnings.filterwarnings("ignore")
    os.chdir(NB_DIR)
    ns = {"__name__": "__main__"}
    ns["display"] = lambda obj: print(obj.to_string() if hasattr(obj, "to_string") else obj)
    nb_cells, count = [], 0
    for kind, src in CELLS:
        cid = uuid.uuid4().hex[:8]
        if kind == "md":
            nb_cells.append({"cell_type": "markdown", "id": cid, "metadata": {}, "source": lines(src)})
            continue
        count += 1
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                exec(compile(src.strip("\n"), f"<code cell {count}>", "exec"), ns)
        except Exception:
            print(buf.getvalue())
            print(f"\n--- FAILED in code cell {count} ---\n{src[:400]}")
            raise
        outputs = []
        if buf.getvalue():
            outputs.append({"output_type": "stream", "name": "stdout", "text": buf.getvalue().splitlines(keepends=True)})
        for num in plt.get_fignums():
            b = io.BytesIO()
            plt.figure(num).savefig(b, format="png", dpi=110, bbox_inches="tight")
            outputs.append({"output_type": "display_data", "metadata": {},
                            "data": {"image/png": base64.b64encode(b.getvalue()).decode(), "text/plain": ["<Figure>"]}})
        plt.close("all")
        nb_cells.append({"cell_type": "code", "id": cid, "metadata": {}, "execution_count": count,
                         "source": lines(src), "outputs": outputs})
        print(f"cell {count} ok", flush=True)
    nb = {"cells": nb_cells, "nbformat": 4, "nbformat_minor": 5,
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                       "language_info": {"name": "python"}}}
    NB_PATH.write_text(json.dumps(nb, indent=1))
    print("wrote", NB_PATH)


if __name__ == "__main__":
    run()
