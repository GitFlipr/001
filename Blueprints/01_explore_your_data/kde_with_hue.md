# KDE plot with hue (density by category)

## What it is

A KDE plot with hue shows the estimated density of one variable (e.g. returns) separately for each level of a categorical variable (e.g. regime, symbol). Multiple smooth curves are overlaid so you can compare how the distribution changes across groups.

## When to use it

When you have a grouping variable (regime, symbol, train vs test). To compare distribution shape across groups. Before modeling: if one group is clearly different, consider group-specific models or robust methods. After regime or changepoint detection: overlay KDE by regime.

## How it works

Same as single-series KDE; with hue you split the data by the hue column and compute one KDE per group. Tools: e.g. sns.kdeplot(data=df, x='returns', hue='regime').

## Inputs

Data: table with one numeric column (variable to plot) and one categorical column (hue). Config: series name, hue column, optional bandwidth.

## Outputs

Plots: one figure with multiple KDE curves. Location: results/ and logs/.

## How to run / implement

Run the module that does KDE with hue; config for data path, series, hue column, output path. Implement: sns.kdeplot(..., hue=...), save figure.

## Interpretation

Curves overlap a lot: variable may not separate groups well. Clearly different shapes: use group-specific modeling or robust methods. One group much wider: higher volatility in that group.

## Related tests

Histograms and KDE (single-series); joint plots (two numeric variables); regime detection (HMM, changepoint) often produce the hue column.
