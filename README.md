# NYC Taxi Trip Duration: Exploratory Analysis and Prediction

Mini-project for **Applied Data Science Skill Lab**, CSE (Data Science), RVCE.

The project follows the six-stage workflow from the lab guidelines:
Problem Identification → Data Acquisition → Data Preparation → Exploratory Data Analysis → Visualization & Predictive Modelling → Interpretation & Presentation.

**Task:** predict how long a New York City taxi trip will take (seconds) from pickup time and pickup/dropoff coordinates.

## Headline results (100,000-trip sample, 20% held-out test set)

| Model | MAE (s) | RMSE (s) | R² (log scale) |
|---|---|---|---|
| Baseline (median) | 442.6 | 673.8 | -0.001 |
| Linear Regression | 253.0 | 398.8 | 0.641 |
| Random Forest | 189.9 | 314.0 | 0.779 |
| **Gradient Boosting** | **177.8** | **295.6** | **0.798** |

The best model is about 3 minutes off on average (60% better than the baseline), and 84% of predictions are within 5 minutes of the actual duration.

## Repository layout

```
notebooks/nyc_taxi_trip_duration.ipynb   Main notebook (all six stages), outputs included
data/train_sample.csv                    Original 100,000-trip sample (Kaggle train.csv)
data/train_cleaned.csv                   Cleaned data with derived features
data/DATA_SOURCE.md                      Dataset source documentation (source, size, variables, limitations)
figures/                                 All charts (fig01 to fig13)
outputs/                                 Model comparison, actual vs predicted table, EDA tables (descriptive
                                         statistics, frequency tables, IQR outliers), cleaning summary, key results
reports/technical_report.docx            Technical report (10 sections required by the guidelines)
reports/project_proposal.docx            Project proposal
reports/*.md                             Markdown versions of the report and proposal, plus the viva outline
scripts/build_notebook.py                Rebuilds and re-runs the notebook
scripts/build_reports_docx.js            Builds the Word documents from the notebook outputs
scripts/observations.py                  Interpretation text used by the notebook
```

The presentation (13 slides, Problem → Data → Analysis → Evidence → Insight → Conclusion) is kept outside the repo; see `reports/viva_presentation_outline.md` for its plan and likely viva questions.

## Run it

```bash
pip install -r requirements.txt
python scripts/build_notebook.py        # re-runs everything, regenerates figures/outputs
jupyter lab notebooks/nyc_taxi_trip_duration.ipynb   # or open in Google Colab
```

The notebook finds `data/train_sample.csv` automatically. To use the full dataset, place Kaggle's `train.csv` in `data/` and delete (or rename) the sample; all code runs unchanged.

## Data source

Kaggle competition [New York City Taxi Trip Duration](https://www.kaggle.com/competitions/nyc-taxi-trip-duration/data), based on 2016 NYC Taxi & Limousine Commission yellow-taxi records. Used for academic purposes under the competition rules.

## Reproducibility

- Random seed 42 is used for the train/test split and all models, so results are repeatable.
- Tested with Python 3, scikit-learn 1.9.1, pandas 3.0.5 and matplotlib 3.11.2.
- The full notebook runs in about one minute on a 2-core machine with the 100,000-trip sample.

## Team

_Add team members and USNs here._
