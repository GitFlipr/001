# ARIMA and GARCH

## What it is

**ARIMA (AutoRegressive Integrated Moving Average):** Models level or returns with AR(p), integration I(d), and MA(q). ARMA = AR + MA for stationary series. **GARCH (Generalized Autoregressive Conditional Heteroskedasticity):** Models volatility clustering—variance depends on past variance and past squared shocks.

Combined: ARIMA for mean, GARCH for conditional variance. Captures fat tails and time-varying volatility.

## When to use it

For return and volatility forecasting when autocorrelation and vol clustering matter. ADF confirms d (unit root); ACF/PACF suggest p, q. Use for volatility forecasts (VaR, position sizing) and return prediction bands.

## How it works

**ARIMA:** Box–Jenkins: identify p, q via ACF/PACF or AIC/BIC; fit; forecast. **GARCH(p,q):** σ²_t = ω + Σ βᵢσ²_{t-i} + Σ αⱼε²_{t-j}. Fit mean model (AR) and variance model (GARCH) jointly. Tools: statsmodels ARIMA, `arch` package.

## Inputs

Return series. Config: ARIMA order (p,d,q), GARCH order (p,q). Use ADF for d; AIC/BIC for p, q.

## Outputs

Fitted coefficients; residual diagnostics; forecast and confidence bands (mean and volatility). Location: results/, logs/.

## Related tests

adf_test (stationarity); acf_pacf (lag structure); distribution_fitting (residual normality); var_cvar (volatility for risk).

## External reference

[ARIMA GARCH model (letianzj)](https://letianzj.github.io/arima-garch-model.html).
