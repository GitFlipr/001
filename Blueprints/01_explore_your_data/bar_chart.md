# Bar chart (categorical counts or summaries)

## What it is

A **bar chart** shows a single value (count or an aggregate like mean, sum) for each category on the x-axis. Each category is a bar; height = the value. Used when the x-axis is **categorical** (e.g. symbol, regime, day of week, model name), not a continuous numeric variable. Common variants: **count plot** (count per category) and **bar plot** (e.g. mean return per symbol).

## When to use it

- **To compare counts or aggregates across categories:** e.g. number of trades per symbol, mean return per regime, win rate by strategy.
- **After summary stats or basic metrics:** Visualize the same numbers (e.g. accuracy per model, trade count per day).
- **To spot imbalance:** One category dominating may require weighting or separate treatment in modeling.
- **For reporting:** Simple and readable for stakeholders.

## How it works

- **Count plot:** For each category, count how many rows have that category; bar height = count.
- **Bar plot (aggregate):** For each category, compute an aggregate (mean, sum, median) of a numeric column; bar height = aggregate.
- Tools: e.g. `sns.countplot(...)` or `sns.barplot(data=..., x='category', y='value')`.

## Inputs

- **Data:** Table with at least one categorical column (x-axis) and, for bar (not count), one numeric column (y-axis).
- **Config:** Category column, value column (if bar), optional order or filters.

## Outputs

- **Plots:** One bar chart per chosen breakdown. Saved to results folder (e.g. PNG/PDF).
- **Optional:** Table of values in JSON or logs.
- **Location:** Typically `results/` (and logs in `logs/`).

## How to run / implement

- **From a pipeline:** Run the module that produces bar charts (e.g. `bar_chart`), with config for data path, category, value, and output path.
- **Implement:** Load data, call `sns.barplot` or `sns.countplot`, save figure.

## Interpretation

- **One category much larger** — consider weighting, stratification, or separate analysis for that group.
- **Similar heights** — balanced across categories; no single category dominating.
- **Use for reporting** — pair with summary stats or basic metrics tables for the same breakdown.

## Related tests

- **Summary stats** — can be broken down by category; bar chart visualizes that breakdown.
- **Basic metrics** — e.g. accuracy per model; bar chart shows the same per-model comparison.
- **Histograms** — for continuous x; use bar chart when x is categorical.
