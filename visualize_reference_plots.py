
from __future__ import annotations

import argparse
import re
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import cm
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

# Reference palette: predicted = blue, measured = orange.
PREDICTED = "#1f77b4"
MEASURED = "#ff7f0e"

SYSTEM_PALETTE = {
    "Gas": "#1f77b4",
    "Power": "#ff7f0e",
    "Lights": "#2ca02c",
    "Server": "#8c564b",
    "Systems": "#2ca02c",
    "L&P": "#1f77b4",
    "Chillers": "#ff7f0e",
    "Services": "#8c564b",
    "Workshops": "#d62728",
}

sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams.update({
    "figure.figsize": (11, 6),
    "figure.dpi": 130,
    "savefig.dpi": 180,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titleweight": "regular",
    "legend.frameon": False,
})


def slug(text: str) -> str:
    """Create a filename-safe string."""
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(text)).strip("_")[:100]


def canonical(name: str) -> str:
    """Normalize common dataset column names."""
    s = re.sub(r"[^a-z0-9]+", "", str(name).lower())

    aliases = {
        "datetime": "datetime",
        "dateandtime": "datetime",
        "timestamp": "datetime",
        "localtime": "datetime",
        "timeindex": "datetime",
        "date": "date",
        "time": "time",
        "hour": "hour",
        "hourending": "hour",
        "dayofweek": "weekday",
        "weekday": "weekday",
        "dayname": "weekday",
        "daytype": "daytype",
        "weekend": "daytype",
        "month": "month",
        "system": "system",
        "enduse": "system",
        "category": "system",
        "variable": "variable",
        "energy": "energy",
        "energykwh": "energy",
        "electricity": "energy",
        "value": "energy",
        "measured": "measured",
        "actual": "measured",
        "observed": "measured",
        "predicted": "predicted",
        "prediction": "predicted",
        "forecast": "predicted",
        "error": "error",
        "residual": "error",
        "lp": "lp",
        "lppredicted": "lp_predicted",
        "lpmeasured": "lp_measured",
        "cooling": "cooling",
        "heating": "heating",
    }

    if s in aliases:
        return aliases[s]

    if any(k in s for k in ("predicted", "prediction", "forecast")):
        return "predicted"
    if any(k in s for k in ("measured", "observed", "actual")):
        return "measured"
    if "datetime" in s or "timestamp" in s:
        return "datetime"

    return s


def read_csv(path: Path) -> pd.DataFrame:
    """Read a CSV and normalize its column headings."""
    df = pd.read_csv(path, low_memory=False)
    df.columns = [str(c).strip() for c in df.columns]

    # EnergyPlus uses headings such as "Date/Time".
    time_col = next(
        (c for c in df.columns
         if canonical(c) in ("datetime", "date")),
        None,
    )

    if time_col:
        raw = df[time_col].astype(str).str.strip()

        # Common EnergyPlus format: 01/01  00:15:00
        parsed = pd.to_datetime(
            raw, format="%m/%d %H:%M:%S", errors="coerce"
        )

        if parsed.isna().mean() > 0.5:
            parsed = pd.to_datetime(raw, errors="coerce")

        df["__datetime"] = parsed
        df["__hour"] = parsed.dt.hour
        df["__month"] = parsed.dt.month
        df["__weekday"] = parsed.dt.day_name()
        df["__weekday_number"] = parsed.dt.dayofweek

    return df


def numeric_columns(df: pd.DataFrame) -> list[str]:
    """Return numeric columns suitable for plotting."""
    return [
        c for c in df.select_dtypes(include=np.number).columns
        if not c.startswith("__")
    ]


def save_plot(fig, output_dir: Path, filename: str) -> None:
    """Save a figure and release its memory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{slug(filename)}.png"

    fig.tight_layout()
    fig.savefig(destination, bbox_inches="tight")
    plt.close(fig)

    print(f"[SAVED] {destination}")


def sampled(df: pd.DataFrame, columns: list[str],
            maximum: int = 15000) -> pd.DataFrame:
    """Limit plotted rows for performance."""
    result = df[columns].dropna()
    if len(result) > maximum:
        result = result.sample(maximum, random_state=42)
    return result


# ------------------------------------------------------------
# 1. BoxPlot
# ------------------------------------------------------------

def box_plot(df: pd.DataFrame, cols: list[str],
             output_dir: Path, source: str) -> int:
    if not cols:
        return 0

    # Choose representative variables, prioritizing building variables.
    preferred = [
        c for c in cols
        if any(k in c.lower() for k in (
            "temperature", "heating rate", "electricity rate",
            "relative humidity", "occupant count"
        ))
    ]
    chosen = (preferred or cols)[:8]

    data = [
        df[c].dropna().sample(
            min(15000, df[c].notna().sum()), random_state=42
        ) if df[c].notna().sum() else pd.Series(dtype=float)
        for c in chosen
    ]

    if not any(len(series) for series in data):
        return 0

    fig, ax = plt.subplots(figsize=(max(10, len(chosen) * 1.5), 6))

    bp = ax.boxplot(
        data,
        patch_artist=True,
        showfliers=False,
        tick_labels=[c.replace(" [", "\n[")[:38] for c in chosen],
    )

    colors = list(SYSTEM_PALETTE.values())
    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor(colors[i % len(colors)])
        patch.set_alpha(0.8)

    ax.set_title(f"BoxPlot — {source}")
    ax.set_ylabel("Value")
    ax.tick_params(axis="x", labelrotation=25)

    save_plot(fig, output_dir, f"{source}_BoxPlot")
    return 1


# ------------------------------------------------------------
# 2. Energy_HeatMap
# ------------------------------------------------------------

def energy_heatmap(df: pd.DataFrame, cols: list[str],
                   output_dir: Path, source: str) -> int:
    if "__datetime" not in df or not cols:
        print(f"[SKIP] Energy_HeatMap — {source}: no datetime column.")
        return 0

    # Prefer variables relevant to building energy and performance.
    preferred = [
        c for c in cols
        if any(k in c.lower() for k in (
            "electricity rate", "heating rate", "cooling rate",
            "energy", "temperature"
        ))
    ]
    chosen = (preferred or cols)[:4]
    count = 0

    for col in chosen:
        temp = df[["__datetime", col]].dropna().copy()
        if temp.empty:
            continue

        temp["day"] = temp["__datetime"].dt.strftime("%m-%d")
        temp["hour"] = temp["__datetime"].dt.hour

        pivot = temp.pivot_table(
            index="day",
            columns="hour",
            values=col,
            aggfunc="mean",
        )

        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(
            pivot,
            cmap="magma",
            ax=ax,
            xticklabels=3,
            yticklabels=30,
            cbar_kws={"label": col},
        )

        ax.set_title(f"Energy_HeatMap — {col}")
        ax.set_xlabel("Hour of day")
        ax.set_ylabel("Day of year (month-day)")

        save_plot(fig, output_dir, f"{source}_Energy_HeatMap_{col}")
        count += 1

    return count


# ------------------------------------------------------------
# 3. MonthlyBarPlotSingle_PredictedvsMeasured
# ------------------------------------------------------------

def find_column(df: pd.DataFrame, kind: str) -> str | None:
    """Find a measured/predicted column using common naming variants."""
    for col in df.columns:
        normalized = canonical(col)
        if normalized == kind:
            return col

    return None


def prediction_plots(df: pd.DataFrame, output_dir: Path,
                     source: str) -> int:
    measured_col = find_column(df, "measured")
    predicted_col = find_column(df, "predicted")

    if not measured_col or not predicted_col:
        print(
            f"[SKIP] Prediction plots — {source}: "
            "no measured/predicted columns found."
        )
        return 0

    temp = df[[measured_col, predicted_col]].copy()
    temp[measured_col] = pd.to_numeric(temp[measured_col], errors="coerce")
    temp[predicted_col] = pd.to_numeric(temp[predicted_col], errors="coerce")
    temp = temp.dropna()

    if temp.empty:
        return 0

    measured = temp[measured_col]
    predicted = temp[predicted_col]
    count = 0

    # Predicted versus measured scatter plot.
    fig, ax = plt.subplots()
    ax.scatter(
        measured, predicted,
        s=20, alpha=0.55, color=PREDICTED, label="Predicted",
    )

    lower = min(measured.min(), predicted.min())
    upper = max(measured.max(), predicted.max())

    ax.plot(
        [lower, upper], [lower, upper],
        linestyle="--", color=MEASURED, label="Ideal agreement",
    )

    ax.set_xlabel("Measured")
    ax.set_ylabel("Predicted")
    ax.set_title(f"MonthlyBarPlotSingle_PredictedvsMeasured — {source}")
    ax.legend()

    save_plot(
        fig, output_dir,
        f"{source}_MonthlyBarPlotSingle_PredictedvsMeasured",
    )
    count += 1

    # Prediction residuals.
    residual = predicted - measured

    fig, ax = plt.subplots()
    ax.hist(residual, bins=30, color=PREDICTED, alpha=0.85)
    ax.axvline(0, color=MEASURED, linestyle="--", label="Zero error")
    ax.set_title(f"WeekdayErrorPlotLPandSystems — {source}")
    ax.set_xlabel("Predicted − measured")
    ax.set_ylabel("Frequency")
    ax.legend()

    save_plot(
        fig, output_dir,
        f"{source}_WeekdayErrorPlotLPandSystems",
    )
    count += 1

    # Report common regression metrics.
    mae = float(np.mean(np.abs(residual)))
    rmse = float(np.sqrt(np.mean(residual ** 2)))
    bias = float(np.mean(residual))

    print(
        f"[METRICS] {source}: n={len(temp)}, "
        f"MAE={mae:.4f}, RMSE={rmse:.4f}, bias={bias:.4f}"
    )

    return count


# ------------------------------------------------------------
# 4. ScatterSingleVariable
# ------------------------------------------------------------

def scatter_plot(df: pd.DataFrame, cols: list[str],
                 output_dir: Path, source: str) -> int:
    varying = [c for c in cols if df[c].nunique(dropna=True) > 1]
    if len(varying) < 2:
        return 0

    # Prefer two variables with building-performance relevance.
    preferred = [
        c for c in varying
        if any(k in c.lower() for k in (
            "temperature", "heating rate", "electricity rate",
            "solar radiation", "relative humidity"
        ))
    ]
    candidates = preferred if len(preferred) >= 2 else varying
    x_col, y_col = candidates[:2]

    temp = sampled(df, [x_col, y_col], maximum=10000)
    if len(temp) < 2:
        return 0

    fig, ax = plt.subplots()
    ax.scatter(
        temp[x_col], temp[y_col],
        s=14, alpha=0.45, color=PREDICTED, edgecolors="none",
    )

    if len(temp) >= 3:
        try:
            result = stats.linregress(temp[x_col], temp[y_col])
            xx = np.linspace(temp[x_col].min(), temp[x_col].max(), 100)

            ax.plot(
                xx,
                result.slope * xx + result.intercept,
                color=MEASURED,
                linewidth=2,
                label=f"r = {result.rvalue:.2f}, p = {result.pvalue:.2g}",
            )
            ax.legend()
        except (ValueError, FloatingPointError):
            pass

    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.set_title(f"ScatterSingleVariable — {source}")

    save_plot(fig, output_dir, f"{source}_ScatterSingleVariable")
    return 1


# ------------------------------------------------------------
# 5. WeekdayAreaPlot
# ------------------------------------------------------------

def weekday_area_plot(df: pd.DataFrame, cols: list[str],
                      output_dir: Path, source: str) -> int:
    if "__datetime" not in df or not cols:
        return 0

    preferred = [
        c for c in cols
        if any(k in c.lower() for k in (
            "electricity rate", "heating rate", "cooling rate"
        ))
    ]
    col = (preferred or cols)[0]

    temp = df[["__datetime", col]].dropna().copy()
    if temp.empty:
        return 0

    temp["weekday"] = temp["__datetime"].dt.dayofweek
    temp["hour"] = temp["__datetime"].dt.hour

    pivot = temp.groupby(["hour", "weekday"])[col].mean().unstack()
    pivot = pivot.reindex(index=range(24), columns=range(7))

    labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    series = [
        pivot[day].fillna(0).to_numpy()
        for day in range(7)
        if pivot[day].notna().any()
    ]
    present_labels = [
        labels[day] for day in range(7)
        if pivot[day].notna().any()
    ]

    if not series:
        return 0

    fig, ax = plt.subplots()
    ax.stackplot(
        range(24),
        series,
        labels=present_labels,
        colors=list(SYSTEM_PALETTE.values())[:len(series)],
        alpha=0.85,
    )

    ax.set_title(f"WeekdayAreaPlot — {col}")
    ax.set_xlabel("Hour of day")
    ax.set_ylabel(f"Mean {col}")
    ax.set_xticks(range(0, 24, 2))
    ax.legend(loc="upper left", ncol=4)

    save_plot(fig, output_dir, f"{source}_WeekdayAreaPlot")
    return 1


# ------------------------------------------------------------
# 6. HeatMapCorrelations
# ------------------------------------------------------------

def correlation_heatmap(df: pd.DataFrame, cols: list[str],
                         output_dir: Path, source: str) -> int:
    varying = [
        c for c in cols
        if df[c].nunique(dropna=True) > 1
    ][:15]

    if len(varying) < 2:
        print(f"[SKIP] HeatMapCorrelations — {source}: too few variables.")
        return 0

    corr = df[varying].corr(numeric_only=True)

    fig, ax = plt.subplots(
        figsize=(max(9, len(varying) * 0.75),
                 max(7, len(varying) * 0.65))
    )

    sns.heatmap(
        corr,
        cmap="vlag",
        center=0,
        vmin=-1,
        vmax=1,
        annot=len(varying) <= 8,
        fmt=".2f",
        square=True,
        ax=ax,
    )

    ax.set_title(f"HeatMapCorrelations — {source}")

    save_plot(fig, output_dir, f"{source}_HeatMapCorrelations")
    return 1


# ------------------------------------------------------------
# 7. Monthly comparison and weekday prediction errors
# ------------------------------------------------------------

def monthly_prediction_plot(df: pd.DataFrame, output_dir: Path,
                            source: str) -> int:
    """Plot monthly measured/predicted averages if date and both values exist."""
    measured_col = find_column(df, "measured")
    predicted_col = find_column(df, "predicted")

    if "__datetime" not in df or not measured_col or not predicted_col:
        return 0

    temp = df[["__datetime", measured_col, predicted_col]].copy()
    temp[measured_col] = pd.to_numeric(temp[measured_col], errors="coerce")
    temp[predicted_col] = pd.to_numeric(temp[predicted_col], errors="coerce")
    temp = temp.dropna()

    if temp.empty:
        return 0

    temp["month"] = temp["__datetime"].dt.month
    monthly = temp.groupby("month")[[measured_col, predicted_col]].mean()
    monthly = monthly.reindex(range(1, 13))

    fig, ax = plt.subplots()
    x = np.arange(12)
    width = 0.38

    ax.bar(
        x - width / 2, monthly[measured_col],
        width, label="Measured", color=MEASURED,
    )
    ax.bar(
        x + width / 2, monthly[predicted_col],
        width, label="Predicted", color=PREDICTED,
    )

    ax.set_xticks(
        x,
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    )
    ax.set_ylabel("Monthly average")
    ax.set_title(f"Monthly measured vs predicted — {source}")
    ax.legend()

    save_plot(
        fig, output_dir,
        f"{source}_MonthlyBarPlotSingle_PredictedvsMeasured",
    )
    return 1


# ------------------------------------------------------------
# Main program
# ------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate reference-style plots from simulation CSV data."
    )
    parser.add_argument(
        "--data-dir", type=Path, default=Path("results"),
        help="Directory containing EnergyPlus or analysis CSV files.",
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path("visualizations/reference_plots"),
        help="Directory where plots will be saved.",
    )
    args = parser.parse_args()

    if not args.data_dir.exists():
        raise SystemExit(f"Data directory does not exist: {args.data_dir}")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(args.data_dir.rglob("eplusout.csv"))
    if not csv_files:
        csv_files = sorted(args.data_dir.rglob("*.csv"))

    if not csv_files:
        raise SystemExit(
            f"No CSV files found in {args.data_dir.resolve()}. "
            "Run EnergyPlus with --readvars first."
        )

    total_plots = 0

    for path in csv_files:
        source = slug(path.parent.name or path.stem)

        try:
            df = read_csv(path)
        except Exception as exc:
            print(f"[ERROR] Could not read {path}: {exc}")
            continue

        cols = numeric_columns(df)

        print(
            f"\n[DATA] {path}\n"
            f"       Rows: {len(df):,}; numeric variables: {len(cols)}"
        )

        if not cols:
            print("[SKIP] No numeric columns found.")
            continue

        # Generate plots supported by this dataset.
        plot_functions = [
            lambda: box_plot(df, cols, args.output_dir, source),
            lambda: energy_heatmap(df, cols, args.output_dir, source),
            lambda: scatter_plot(df, cols, args.output_dir, source),
            lambda: weekday_area_plot(df, cols, args.output_dir, source),
            lambda: correlation_heatmap(df, cols, args.output_dir, source),
            lambda: prediction_plots(df, args.output_dir, source),
            lambda: monthly_prediction_plot(df, args.output_dir, source),
        ]

        for function in plot_functions:
            try:
                total_plots += function()
            except Exception as exc:
                print(f"[WARNING] A plot could not be generated: {exc}")

    print(
        f"\nFinished. Generated {total_plots} plot(s).\n"
        f"Output directory: {args.output_dir.resolve()}"
    )


if __name__ == "__main__":
    main()
