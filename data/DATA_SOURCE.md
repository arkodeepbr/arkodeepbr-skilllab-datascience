# Dataset Source Documentation

## Identification
- **Dataset name:** New York City Taxi Trip Duration
- **Source:** Kaggle competition *nyc-taxi-trip-duration*, file `train.csv`
  https://www.kaggle.com/competitions/nyc-taxi-trip-duration/data
- **Origin of the records:** NYC Taxi & Limousine Commission (TLC) yellow-taxi trip records for 2016
  https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- **Access:** downloaded from Kaggle after joining the competition and accepting its rules.
- **Usage and privacy:** used for academic purposes only, under the competition rules. The data has no names or other direct personal identifiers; trip ids are anonymous.

## Files in this folder
| File | Description |
|---|---|
| `train_sample.csv` | Original data: a 100,000-trip sample of Kaggle's `train.csv` (about 1.46 million trips), unmodified |
| `train_cleaned.csv` | Cleaned data (99,239 trips) with derived variables, produced by the notebook |

## Size and period
- **Original sample:** 100,000 records, 11 attributes.
- **Cleaned data:** 99,239 records (761 records, 0.76%, removed as errors), 23 columns including derived variables.
- **Time period of pickups:** 1 January 2016 to 30 June 2016.

## Original variables
| Variable | Type | Description |
|---|---|---|
| id | identifier | Unique trip identifier |
| vendor_id | categorical (1/2) | Taxi technology provider that supplied the record |
| pickup_datetime | datetime | Date and time the meter was engaged |
| dropoff_datetime | datetime | Date and time the meter was disengaged |
| passenger_count | integer | Number of passengers (driver-entered) |
| pickup_longitude, pickup_latitude | float | Where the meter was engaged |
| dropoff_longitude, dropoff_latitude | float | Where the meter was disengaged |
| store_and_fwd_flag | categorical (Y/N) | Y = record held in the vehicle before being sent to the vendor |
| trip_duration | integer | Trip duration in seconds (target) |

## Derived variables (added in the notebook)
pickup_hour, pickup_weekday, pickup_month, is_weekend, is_rush_hour, store_fwd, haversine_km, manhattan_km, bearing, log_haversine, log_duration, speed_kmh. Details and formulas are in Stage 3.3 of the notebook.

## Limitations
- Six months of one taxi type only; no weather, traffic or route data.
- Driver-entered passenger counts can be wrong (one trip has 0).
- Only start and end coordinates, not the path travelled.
- `dropoff_datetime` equals pickup plus duration, so it must not be used as a model input.

## Cleaning applied
See the notebook (Stage 3.4) and `outputs/cleaning_rules_summary.csv`: 0 passengers (1), outside the NYC bounding box (49), duration under 60 s (592), over 3 h (129), implied speed over 120 km/h (6). Records can break more than one rule, so 761 unique records were removed.
