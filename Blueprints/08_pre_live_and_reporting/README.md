# Phase 8: Pre-live and reporting

**Goal:** Right before going live: **pseudo-live testing** (simulate live with no future data), **integration checks** (API, config, data freshness), **report generation** (one report from all your results), and **attribution** (PnL breakdown).

**Why it matters:** A backtest that looks great can fail in live because of latency, slippage, or bad config. Pseudo-live catches that. Integration checks catch misconfig and stale data. Reports and attribution give you and stakeholders a single place to see performance and risk.

**What you’ll learn:** How pseudo-live differs from a simple backtest (no peeking, execution simulation); what to check before flipping the switch; how to aggregate results into a report and break down PnL by source.

**Tests in this phase:** Event-driven backtest framework → pseudo-live testing → integration checks → slippage and latency testing → kill switch and circuit breaker → paper trading reconciliation → report generation → attribution.

**Next:** You’re ready to go live (with caution). Phase 9 (advanced/specialty) is optional—deeper topics you can add when needed.
