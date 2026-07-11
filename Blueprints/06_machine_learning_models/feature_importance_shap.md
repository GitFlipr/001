# Feature importance and SHAP

## What it is

**Feature importance** ranks which inputs matter most for model predictions. **SHAP (SHapley Additive exPlanations)** assigns each feature a contribution to each prediction, with theoretical grounding (Shapley values). Essential for interpretability when using tree or ML models.

## When to use it

After training random forest, gradient boosting, or other ML models. To validate that important features make economic sense (sanity check). To debug overfitting (e.g. future-leaking features ranking high). For regulatory or stakeholder explainability. Before going live: understand why the model predicts what it does.

## How it works

- **Tree importance:** Gain (reduction in loss when splitting on feature) or split count. Fast; built into sklearn, XGBoost, LightGBM.
- **SHAP:** For each prediction, compute each feature's marginal contribution. TreeExplainer for trees (fast); KernelExplainer for any model (slower). Output: per-sample contributions; aggregate (mean |SHAP|) for global importance.
- **Plots:** Bar plot (global importance); beeswarm (feature values vs SHAP); dependence plots (one feature vs its SHAP).

## Inputs

Trained model; features and (optionally) target for explanation. Config: which samples to explain; background set for SHAP.

## Outputs

Feature importance table; SHAP values; plots (bar, beeswarm, dependence). Location: results/, logs/.

## Interpretation

High importance + sensible feature: good. High importance + suspicious feature (e.g. future date): leakage. Low importance: feature may not help or is redundant. Use to prune features or validate strategy logic.

## Related tests

Random forest; gradient_boosting (models that produce importances); linear_model (coefficients as natural importance); time_series_cv; rolling window backtests.