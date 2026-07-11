# Joint plots (scatter, hex bin, regression)

## What it is

Joint plots show the relationship between two variables: scatter (one point per observation), hex bin (points binned into hexagons), and/or a regression line. They answer: how do two series move together? (e.g. open vs close, return vs volume.)

## When to use it

To detect linear or non-linear relationships. To spot outliers or clusters. To decide which pairs to model together. Before regression or ML: joint plots inform which pairs are worth including and whether linearity is plausible.

## How it works

Scatter: plot (x, y) per row. Hex bin: divide (x,y) into hexagons, colour by count. Regression line: fit y ~ x, plot fit. Tools: sns.scatterplot, sns.jointplot, sns.regplot.

## Inputs

Data: two columns (e.g. returns and lag_returns). Config: which pair(s), plot type (scatter/hex/regression).

## Outputs

Plots per pair in results/. Optional correlation or regression stats in JSON/logs.

## How to run / implement

Run the joint_plots module; config for data path, variable pairs, output path. Implement: load data, for each pair call scatter/hex/regplot, save figures.

## Interpretation

Strong linear trend: good candidate for linear regression or as a feature. Weak or noisy: try other features or non-linear models. Outliers: consider winsorization or robust methods. Non-linear shape: consider transforms or non-linear models.

## Related tests

Summary stats (univariate); distribution fitting (joint distributions); linear regression / Lasso / Ridge (use strong relationships as features).
