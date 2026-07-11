# Phase 1: Explore your data

**Goal:** Before any modeling or backtesting, you need to *understand* your data—its scale, shape, and quirks.

**Why this comes first:** Summary stats and plots catch bad data (zeros, wrong units, spikes), show whether returns are skewed or heavy-tailed, and help you choose the right metrics and models later. No formulas required to start: you're just looking at numbers and pictures.

**What you'll learn:** How to describe a series (mean, spread, percentiles), how to visualize distributions (histograms, KDE), and how to pick a probability distribution (e.g. normal vs heavy-tailed) for later use in risk or simulation.

**Tests in this phase:** Historical data sources → data quality checks → summary statistics → histograms/KDE, bar charts, KDE with hue → joint plots (two variables) → distribution fitting (formalize the shape).

**Next:** Phase 2 (time series basics)—once you know what your data looks like, you'll check whether it's "well-behaved" over time (stationary, regimes).