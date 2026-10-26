// Builds reports/technical_report.docx and reports/project_proposal.docx
// Usage: node scripts/build_reports_docx.js <path-to-report_data.json>
// The JSON holds tables exported from outputs/*.csv so every number comes from the notebook run.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, Footer,
  AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType, LevelFormat, PageNumber,
} = require("docx");

const ROOT = path.resolve(__dirname, "..");
const data = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const TEAM = "Team members: [add names and USNs]";
const CONTENT_W = 9638; // A4 with 2 cm margins, in DXA

// ---------- helpers ----------
function runs(text, base = {}) {
  return text.split(/(\*\*[^*]+\*\*)/).filter(Boolean).map((t) =>
    t.startsWith("**") ? new TextRun({ ...base, text: t.slice(2, -2), bold: true }) : new TextRun({ ...base, text: t }));
}
const p = (text, o = {}) => new Paragraph({ spacing: { after: 120, line: 276 }, alignment: o.align, children: runs(text, o.run || {}) });
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const bullets = (items) => items.map((t) => new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 60, line: 276 }, children: runs(t) }));
const numbered = (items, inst) => items.map((t) => new Paragraph({ numbering: { reference: "numbers", level: 0, instance: inst }, spacing: { after: 60, line: 276 }, children: runs(t) }));

function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}
let figNo = 0;
function fig(name, caption, width = 580) {
  const file = path.join(ROOT, "figures", name);
  const s = pngSize(file);
  figNo += 1;
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 }, keepNext: true,
      children: [new ImageRun({ type: "png", data: fs.readFileSync(file), transformation: { width, height: Math.round((width * s.h) / s.w) },
        altText: { title: caption, description: caption, name } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
      children: [new TextRun({ text: `Figure ${figNo}: ${caption}`, italics: true, size: 20 })] }),
  ];
}

function table(headers, rows, widths, o = {}) {
  const sz = o.size || 20;
  const border = { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const cell = (text, w, header, bold, align) => new TableCell({
    width: { size: w, type: WidthType.DXA }, borders,
    shading: header ? { fill: "DCE6F1", type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    children: [new Paragraph({ alignment: align, children: [new TextRun({ text: String(text), bold: header || bold, size: sz })] })],
  });
  const al = (i) => (o.leftCols || [0]).includes(i) ? AlignmentType.LEFT : AlignmentType.CENTER;
  const total = widths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: [
      new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, widths[i], true, true, al(i))) }),
      ...rows.map((r, ri) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, widths[i], false, o.boldRow === ri, al(i))) })),
    ],
  });
}
const gap = () => new Paragraph({ spacing: { after: 160 }, children: [] });

function makeDoc(title, children) {
  return new Document({
    creator: "arkodeepbr", title,
    styles: {
      default: { document: { run: { font: "Calibri", size: 22 } } },
      paragraphStyles: [
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 32, bold: true, font: "Calibri", color: "1F3864" }, paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0, keepNext: true, keepLines: true } },
        { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 26, bold: true, font: "Calibri", color: "2F5496" }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1, keepNext: true, keepLines: true } },
      ],
    },
    numbering: { config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ] },
    sections: [{
      properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "NYC Taxi Trip Duration  |  Applied Data Science Skill Lab, RVCE  |  Page ", size: 18, color: "666666" }),
                   new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "666666" })] })] }) },
      children,
    }],
  });
}

function titleBlock(title, subtitle) {
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 600, after: 120 }, children: [new TextRun({ text: title, bold: true, size: 44, color: "1F3864" })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 360 }, children: [new TextRun({ text: subtitle, size: 28, color: "2F5496" })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Applied Data Science Skill Lab, CSE (Data Science), RVCE", size: 24 })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: TEAM, size: 24 })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 360 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "2F5496", space: 8 } },
      children: [new TextRun({ text: "Code and data: https://github.com/arkodeepbr/arkodeepbr-skilllab-datascience", size: 20, color: "555555" })] }),
  ];
}

// ---------- TECHNICAL REPORT ----------
function technicalReport() {
  figNo = 0;
  const c = [...titleBlock("NYC Taxi Trip Duration", "Exploratory Analysis and Prediction: Technical Report")];

  c.push(h1("1. Introduction and Problem Statement"));
  c.push(p("Taxi trip time in a large city depends on distance, time of day, day of the week and location. Distance alone is a weak predictor because traffic and demand change through the day. This project analyses New York City yellow-taxi trips from January to June 2016 and builds a regression model that predicts **trip duration in seconds** from information known at pickup: the pickup time and the pickup and dropoff coordinates."));
  c.push(p("Possible uses are estimated time of arrival (ETA) and fare estimation, driver dispatch planning and urban mobility analysis. The work follows the six-stage mini-project workflow and covers Experiment 3.4, Prediction and Performance Analysis using a Trained Machine Learning Model."));

  c.push(h1("2. Objectives"));
  c.push(...numbered([
    "Acquire and document the dataset.",
    "Clean and prepare the data with Python and Pandas, documenting each decision.",
    "Explore distributions, relationships and outliers.",
    "Visualize patterns with Matplotlib and Seaborn.",
    "Train, compare and evaluate regression models with Scikit-learn.",
    "Interpret the results, including usefulness and limitations.",
  ], 1));

  c.push(h1("3. Dataset Description and Source"));
  c.push(...bullets([
    "**Name and source:** New York City Taxi Trip Duration, Kaggle competition (https://www.kaggle.com/competitions/nyc-taxi-trip-duration/data), based on 2016 NYC Taxi & Limousine Commission yellow-taxi records.",
    "**Size:** about 1.46 million trips in the full file; a **100,000-trip sample** with 11 attributes is used here.",
    "**Time period:** 1 January to 30 June 2016.",
    "**Privacy and usage:** no personal identifiers are present; the data is used for academic purposes under the competition rules.",
  ]));
  c.push(gap());
  c.push(table(["Variable", "Type", "Description"], [
    ["id", "identifier", "Unique trip identifier"],
    ["vendor_id", "categorical (1/2)", "Taxi technology provider that supplied the record"],
    ["pickup_datetime", "datetime", "Date and time the meter was engaged"],
    ["dropoff_datetime", "datetime", "Date and time the meter was disengaged"],
    ["passenger_count", "integer", "Number of passengers (driver-entered)"],
    ["pickup_longitude / latitude", "float", "Where the meter was engaged"],
    ["dropoff_longitude / latitude", "float", "Where the meter was disengaged"],
    ["store_and_fwd_flag", "categorical (Y/N)", "Y = record held in the vehicle before being sent to the vendor"],
    ["trip_duration", "integer (target)", "Trip duration in seconds"],
  ], [2700, 1900, 5038], { leftCols: [0, 1, 2], size: 19 }));
  c.push(gap());
  c.push(h2("Limitations of the dataset"));
  c.push(...bullets([
    "Six months only and one taxi type; no weather, live traffic or route data.",
    "Driver-entered passenger counts can be wrong (one trip has 0).",
    "Only start and end coordinates are known, not the route taken.",
    "dropoff_datetime equals pickup plus duration, so it cannot be a model input (target leakage).",
  ]));

  c.push(h1("4. Data Preparation and Cleaning"));
  c.push(p("Inspection found **no missing values, no duplicated rows or trip ids**, and the recorded duration matches the timestamps exactly. The remaining risk was implausible values, handled with documented rules:"));
  const reasons = ["not a valid passenger trip", "GPS error or atypical trip", "cancelled fare or meter error", "meter left running", "impossible in city traffic"];
  c.push(table(["Rule", "Records flagged", "% of data", "Reason"],
    data.cleaning.map((r, i) => [r[0], r[1], r[2], reasons[i]]), [3600, 1500, 1200, 3338], { leftCols: [0, 3], size: 19 }));
  c.push(gap());
  c.push(p("Records can break more than one rule. In total **761 unique records (0.76%) were removed, leaving 99,239**. Long but plausible trips were kept."));
  c.push(p("**Derived variables:** pickup hour, weekday, month, weekend flag, weekday rush-hour flag (07:00 to 10:00 and 16:00 to 19:00), straight-line (haversine) distance, Manhattan-style distance, compass bearing, and the log of distance and duration. Speed was computed for analysis only because it uses the target. The cleaned file is data/train_cleaned.csv."));

  c.push(h1("5. Exploratory Data Analysis"));
  c.push(h2("5.1 Descriptive statistics"));
  c.push(table(["Variable", "Mean", "Median", "Mode", "Std", "Min", "Q1", "Q3", "Max"], data.desc, [1900, 940, 940, 940, 940, 1000, 940, 1000, 1038], { size: 17 }));
  c.push(p("Durations and distances are in seconds and kilometres.", { run: { italics: true, size: 18 } }));
  c.push(h2("5.2 Main observations"));
  c.push(...bullets([
    "**Duration** has a median of 11.1 min and a mean of 14.0 min. It is right-skewed (skewness 2.27); the 95th percentile is 34.7 min and the 99th is 54.7 min. After a log transform the skewness is -0.14.",
    "**Distance:** median 2.1 km, mean 3.4 km. Its correlation with duration is 0.77.",
    "**Categories:** the vendor split is 53% and 47% with identical mean durations (14.0 min); 71% of trips carry one passenger; 0.6% of trips have the store-and-forward flag and last longer on average (18.3 min against 14.0 min). Full frequency tables are in outputs/eda_frequency_tables.csv.",
  ]));
  c.push(h2("5.3 Outlier investigation (IQR method)"));
  c.push(table(["Variable", "Q1", "Q3", "Upper fence", "Outliers", "% of trips"], data.iqr, [2400, 1400, 1400, 1700, 1400, 1338], { size: 19 }));
  c.push(gap());
  c.push(p("**4,908 trips (4.95%)** exceed the duration fence of 2,090 s. Their median distance is 12.5 km (typical trips: 2.0 km), 89.6% travel more than 5 km, and about 58.5% start or end in the airport zones. They are genuine long trips and were **not removed**. The skew is handled by modelling log duration instead."));

  c.push(h1("6. Visualization and Insight Generation"));
  c.push(...fig("fig01_duration_distribution.png", "Trip duration is right-skewed; the log transform makes it close to symmetric."));
  c.push(...fig("fig02_boxplots.png", "Spread and outliers of duration, distance and duration by passenger count."));
  c.push(p("**Insight:** the middle half of trips take about 7 to 18 minutes, with a long tail of airport and cross-borough trips."));
  c.push(...fig("fig03_distance_vs_duration.png", "Longer distance means longer trips (r = 0.77), but with wide scatter.", 520));
  c.push(...fig("fig04_hourly_demand_duration.png", "Demand and trip duration by hour of day."));
  c.push(p("**Insight:** demand is lowest at about 05:00 (1,041 trips) and highest at 18:00 to 19:00 (about 6,200 trips). Mean duration is longest in the afternoon (16.2 min at 15:00), which is consistent with congestion building up during the day."));
  c.push(...fig("fig05_weekday_patterns.png", "Trips by weekday and median duration by weekday and hour.", 600));
  c.push(p("**Insight:** weekday daytime trips are the slowest (median up to 14 min), while Sunday morning is the fastest (about 7 min). Weekend trips average 12.8 min against 14.5 min on weekdays."));
  c.push(...fig("fig06_daily_trend.png", "Daily number of trips and mean duration, January to June 2016."));
  c.push(p("**Insight:** the quietest days are 23 January (122 trips) and 24 January (253 trips), which coincide with the major snowstorm of 22 to 24 January 2016, and 30 May (369 trips), Memorial Day. These dates are an outside explanation, not part of the dataset. Mean duration rises from 13.2 min in January to 15.0 min in June (+13.5%)."));
  c.push(...fig("fig07_pickup_dropoff_density.png", "Pickup and dropoff density: Manhattan and the JFK and LaGuardia airports.", 560));
  c.push(...fig("fig08_category_comparison.png", "Mean and median duration by vendor, store-and-forward flag and rush hour."));
  c.push(...fig("fig09_correlation_heatmap.png", "Correlation matrix of numerical variables.", 470));
  c.push(p("Only distance is strongly linked to duration (haversine 0.77, Manhattan 0.75). Hour, weekday, passenger count and vendor each have a correlation below 0.07 in size. **Correlation is not read as causation:** pickup longitude (0.36) marks where airport trips start; it does not make trips longer."));

  c.push(h1("7. Predictive Modelling and Evaluation"));
  c.push(p("**Task:** regression. **Target:** trip_duration, modelled as log(1 + duration) and converted back to seconds for evaluation. **Features (16):** vendor, passenger count, store-and-forward flag, four coordinates, hour, weekday, month, weekend and rush-hour flags, haversine distance and its log, Manhattan distance and bearing. **Split:** 80% training (79,391 trips) and 20% testing (19,848 trips), random seed 42. The test set was never used to fit a model."));
  c.push(table(["Model", "MAE (s)", "RMSE (s)", "Median AE (s)", "R² (log)", "RMSLE"], data.models, [2800, 1300, 1300, 1700, 1300, 1238], { boldRow: 3, size: 20 }));
  c.push(gap());
  c.push(...bullets([
    "Gradient Boosting reduces MAE by **59.8%** compared with the baseline (178 s, about 3.0 min, against 7.4 min).",
    "**52.9%** of test predictions are within 2 minutes of the actual duration, **84.3%** within 5 minutes and 95.9% within 10 minutes.",
    "5-fold cross-validation gives an RMSLE of 0.326 (+/- 0.003) against 0.328 on the test set, so there is no sign of overfitting.",
  ]));
  c.push(...fig("fig10_model_comparison.png", "Test-set MAE and log-scale R² for each model.", 540));
  c.push(h2("Actual versus predicted values (Experiment 3.4)"));
  c.push(p("Fifteen random test trips predicted by the Gradient Boosting model. The full test-set table is in outputs/actual_vs_predicted_test.csv."));
  c.push(table(["Trip id", "Pickup", "Distance (km)", "Actual (s)", "Predicted (s)", "Error (s)", "Abs. error %"], data.avp, [1700, 1300, 1400, 1200, 1500, 1200, 1338], { size: 18 }));
  c.push(gap());
  c.push(...fig("fig11_actual_vs_predicted.png", "Actual versus predicted duration and the distribution of prediction errors.", 580));
  c.push(...fig("fig12_error_analysis.png", "Error by trip distance and by pickup hour.", 560));
  c.push(...fig("fig13_feature_importance.png", "Permutation feature importance of the Gradient Boosting model.", 400));
  c.push(p("Three new hypothetical trips were also predicted: Times Square to Wall Street at 08:30 on a Wednesday (26.7 min) and at 03:00 on a Sunday (17.9 min), and Grand Central to JFK on a Friday at 17:30 (68.6 min)."));

  c.push(h1("8. Key Findings and Interpretation"));
  c.push(...numbered([
    "Trip distance is the dominant driver of duration; time of day, weekday and season add smaller but clear effects (afternoon and weekday trips are slower).",
    "Distance features account for most of the predictive power (haversine distance about 76% of permutation importance), followed by pickup hour (8%) and bearing (5%). Passenger count and vendor contribute almost nothing, matching the EDA.",
    "Absolute error grows with distance (130 s under 1 km to 422 s above 15 km) while relative error falls (39% to 16%). Short trips are dominated by traffic lights, hailing and waiting, which the data cannot describe.",
    "The model is accurate enough for ETA display, rough fare estimates and dispatch planning, with a typical error of about 3 minutes.",
  ], 2));

  c.push(h1("9. Limitations and Possible Improvements"));
  c.push(h2("Limitations"));
  c.push(...bullets([
    "No weather, live traffic, road closures, accidents or events, which cause most large errors; about 4% of predictions are wrong by more than 10 minutes.",
    "Straight-line distance is used instead of the real route.",
    "Training on log duration pulls predictions toward typical values, so very long trips are underestimated.",
    "Only six months of 2016 and a 100,000-trip sample; results may not hold for other periods.",
    "The model finds associations only; the cause of trends such as rising durations from January to June cannot be established from this data.",
  ]));
  c.push(h2("Possible improvements"));
  c.push(...numbered([
    "Add weather and public-holiday features.",
    "Use road-network route distance and time (for example from OSRM) and pickup and dropoff zone clusters.",
    "Train on the full 1.46 million trips with hyperparameter tuning and ensembles.",
    "Use quantile regression to give a time range instead of a single value.",
  ], 3));

  c.push(h1("10. Conclusion and References"));
  c.push(p("Distance and time of day make taxi trip duration reasonably predictable. A gradient-boosting model cuts the average error by about 60% compared with a naive guess and reaches a test MAE of about 3 minutes. The remaining error comes mainly from factors outside the dataset, chiefly traffic and weather, so predictions should be used as estimates and not as exact times."));
  c.push(h2("References"));
  c.push(...numbered([
    "Kaggle. New York City Taxi Trip Duration competition. https://www.kaggle.com/competitions/nyc-taxi-trip-duration",
    "NYC Taxi & Limousine Commission. TLC Trip Record Data. https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page",
    "Pedregosa et al. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research 12, 2825-2830.",
    "McKinney, W. (2010). Data Structures for Statistical Computing in Python. Proceedings of the 9th Python in Science Conference.",
    "Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. Computing in Science & Engineering 9(3).",
    "Waskom, M. (2021). seaborn: statistical data visualization. Journal of Open Source Software 6(60), 3021.",
  ], 4));
  return makeDoc("NYC Taxi Trip Duration: Technical Report", c);
}

// ---------- PROPOSAL ----------
function proposal() {
  const c = [...titleBlock("NYC Taxi Trip Duration", "Project Proposal")];
  c.push(h1("1. Problem Statement"));
  c.push(p("Taxi trip time in a large city depends on distance, time of day, day of the week and location. Passengers, drivers and fleet operators cannot estimate it reliably from distance alone because traffic and demand change through the day. This project analyses New York City yellow-taxi trips from January to June 2016 and builds a regression model that predicts the duration of a trip (in seconds) from information available when the trip starts."));
  c.push(h1("2. Objectives"));
  c.push(...numbered([
    "Acquire and document the NYC Taxi Trip Duration dataset.",
    "Clean and prepare the data with Python and Pandas, documenting every decision.",
    "Perform exploratory data analysis: descriptive statistics, frequency tables, distributions and IQR outlier investigation.",
    "Visualize patterns with Matplotlib and Seaborn (bar charts, line charts, histograms, box plots, scatter plots and heatmaps).",
    "Train and compare regression models with Scikit-learn and evaluate them on unseen test data (MAE, RMSE, R²).",
    "Interpret the results, state limitations and suggest improvements.",
  ], 5));
  c.push(h1("3. Analytical Questions"));
  c.push(...bullets([
    "How is trip duration distributed, and are extreme values errors or real trips?",
    "How strongly does distance explain duration?",
    "How do demand and duration change by hour, weekday and month?",
    "Do vendor, passenger count or the store-and-forward flag matter?",
    "How accurately can duration be predicted, and where does the model fail?",
  ]));
  c.push(h1("4. Dataset Source"));
  c.push(p("Kaggle competition **New York City Taxi Trip Duration** (https://www.kaggle.com/competitions/nyc-taxi-trip-duration/data), derived from the NYC Taxi & Limousine Commission 2016 yellow-taxi records. The full file has about 1.46 million trips and 11 attributes: trip id, vendor, pickup and dropoff timestamps, passenger count, pickup and dropoff coordinates, the store-and-forward flag and trip duration. A 100,000-trip sample is used. The data has no personal identifiers and is used for academic purposes under the competition rules."));
  c.push(h1("5. Proposed Methods and Tools"));
  c.push(...bullets([
    "**Language and libraries:** Python, Pandas, NumPy, Matplotlib, Seaborn and Scikit-learn.",
    "**Preparation:** validity checks, removal of impossible records, and derived variables (hour, weekday, month, rush-hour flag, haversine and Manhattan distance, bearing).",
    "**EDA:** mean, median, mode, standard deviation, quartiles, skewness, frequency tables and IQR outlier analysis.",
    "**Models:** a median baseline, Linear Regression, Random Forest and Histogram Gradient Boosting, trained on log duration with an 80/20 train-test split and 5-fold cross-validation.",
    "**Metrics:** MAE (primary), RMSE, median absolute error, and R² and RMSLE on the log scale.",
    "**Environment:** Jupyter or Google Colab notebook, with a GitHub repository for version control.",
  ]));
  c.push(h1("6. Expected Outcomes"));
  c.push(...bullets([
    "A cleaned dataset with documented preprocessing.",
    "Labelled visualizations with interpretation of time and distance patterns.",
    "A model that clearly beats a naive baseline, with an honest account of its limitations.",
    "A technical report and demonstration material following Problem, Data, Analysis, Evidence, Insight, Conclusion.",
  ]));
  c.push(h1("7. Intended Application"));
  c.push(p("Estimated time of arrival (ETA) and fare estimation, driver dispatch planning and urban mobility analysis."));
  return makeDoc("NYC Taxi Trip Duration: Project Proposal", c);
}

(async () => {
  const out = path.join(ROOT, "reports");
  fs.writeFileSync(path.join(out, "technical_report.docx"), await Packer.toBuffer(technicalReport()));
  fs.writeFileSync(path.join(out, "project_proposal.docx"), await Packer.toBuffer(proposal()));
  console.log("wrote technical_report.docx and project_proposal.docx");
})();
