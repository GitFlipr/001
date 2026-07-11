# Mean squared error (MSE)

## What it is

MSE = mean((observed - predicted)^2). RMSE = sqrt(MSE). Standard regression loss; lower is better.

## When to use it

To compare regression models. As training objective for many models. Report RMSE for same units as target.

## How it works

Compute MSE and RMSE from y_true and y_pred. Often per model/symbol in basic_metrics.

## Inputs

Observed target and predictions. Config: which model(s).

## Outputs

MSE/RMSE per model or symbol. Location: results/, logs/.

## Interpretation

Compare with R²; large train–val gap suggests overfitting. Use with bias_variance.

## Related tests

R_squared, basic_metrics; linear_model, lasso_ridge_regression; bias_variance.
