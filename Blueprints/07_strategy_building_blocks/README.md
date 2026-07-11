# Phase 7: Strategy building blocks

**Goal:** Add **trading building blocks**: swing highs/lows, Fibonacci and Gann levels, and (optionally) Black–Scholes for options. These feed into strategy logic and level-based backtests.

**Why it matters:** Many strategies use “levels” (support/resistance, retracements) or options. Swing detection finds structure; Fib and Gann turn that into concrete levels; you can then test those levels with permutation or significance tests from Phase 5. Black–Scholes is for when you trade or hedge options.

**What you’ll learn:** How swing detection works; how Fibonacci retracements and extensions and Gann angles are computed; how they plug into backtests; basics of option pricing (Black–Scholes, implied vol, Greeks) if you need them.

**Tests in this phase:** Exponential moving average (EMA/EWMA) → swing detection → Fibonacci retracements, extensions → Gann angles, Gann Square of Nine → VWAP/TWAP (execution benchmarks) → Black–Scholes, variations, implied vol and Greeks → mean reversion (z-score, half-life) → cointegration and pairs trading → Kalman filter pairs trading.

**Next:** Phase 8 (pre-live and reporting) when you’re ready to simulate live and ship reports.
