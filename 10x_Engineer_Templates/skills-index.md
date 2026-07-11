# Skills Index

All skills built in this project, grouped by the batch they were requested in. 63 skills total.

## 1. Data ingestion (first batch)

**`hl-grpc-ticker-stream`** — Connects to Hyperliquid's live WebSocket feed (wss://api.hyperliquid.xyz/ws) to stream real-time trades, L2 book updates, BBO, and user fills for any perp or spot asset. Used to feed live tick data into sub-bots, OFI/CUSUM calculations, and anomaly detection in my trading system where candle-based polling is too slow. Target environments: Hyperliquid perps & spot markets.

**`defillama-tvl-fetcher`** — Pulls Total Value Locked (TVL) and DEX/perp volume data across chains and protocols from the free, keyless DefiLlama API (api.llama.fi) to detect where liquidity is rotating. Used to flag shifting liquid zones, screen chains/protocols for regime changes before deploying capital or sizing sub-bots, and feed cross-chain liquidity context into the backtesting engine. Target environments: any DeFi chain or protocol tracked by DefiLlama (500+ chains, 7000+ protocols).

**`polymarket-clob-fetcher`** — Extracts historic and live order book data, prices, midpoints, and spreads for Polymarket prediction market contracts via the Gamma discovery API and CLOB trading API. Used to pull event-probability time series for signal research, cross-reference prediction-market implied odds against other data feeds, and screen markets by liquidity before analysis. Target environment: Polymarket (Polygon-settled prediction markets).

**`dex-pool-scanner`** — Monitors liquidity pools across Raydium, Uniswap v3, PancakeSwap, Camelot, SaucerSwap, Magnetic, SushiSwap, and other DEXs for sudden pool-depth spikes or drains, using DexScreener as a fast cross-chain screening layer and direct RPC calls for verified per-pool precision. Used to detect liquidity events (rug pulls, whale LPs entering/exiting, MEV-driven depth shifts) that matter for anomaly detection and liquidation-cluster-adjacent strategies in my trading system. Target environments: Solana, Ethereum, Arbitrum, BSC, Hedera, and any other chain with an on-chain AMM.

**`hl-funding-tracker-2`** — Pulls multi-day historical funding rate and premium data for Hyperliquid perpetuals via the HyperCore POST/info API, and tracks live predicted funding across venues. Used to feed funding-rate distributions into basis trading strategies, identify carry/arbitrage windows, and assess funding cost drag on held positions in my sub-bot/master-bot system. Target environment: Hyperliquid perpetuals.

## 2. Signal & analytics

**`regime-classifier`** — Classifies the current market environment (e.g. high-vol ranging, low-vol trending, high-vol trending) from OHLCV data using ATR/trend matrices, Gaussian Mixture Models, and Hidden Markov Models. Used to gate which sub-bot strategies are active, size positions, and adjust CUSUM/OFI thresholds based on the prevailing regime rather than treating all market conditions the same. Target environment: any OHLCV series, most commonly Hyperliquid candles from the hl-historical-candles / hl-grpc-ticker-stream skills.

**`onchain-gas-oracle`** — Evaluates current block-native gas/priority-fee rates across EVM chains (via eth_feeHistory) and Solana (via getRecentPrioritizationFees) to calculate transaction friction dynamically before executing on-chain arb or liquidity-event trades. Used to decide whether an arb's expected edge survives current network fee conditions and to set competitive-but-not-wasteful gas parameters. Target environments: any EVM chain (Ethereum, Arbitrum, BSC, Polygon, etc.) and Solana.

**`basis-arb-calc`** — Computes the premium/discount spread between spot markets and Hyperliquid perpetual futures, converts it to an annualized basis, and nets out funding costs to evaluate carry-trade viability. Used to identify and size basis/carry positions and to assess whether a held position's funding drag is currently working for or against it. Target environment: Hyperliquid perps, paired with any spot price source (Hyperliquid spot, or external CEX/DEX).

**`predict-market-prob-calc`** — Translates prediction-market order book spreads (bid/ask, midpoint) into implied probability vectors, correcting for vig/overround and spread-driven bias across related outcomes. Used to turn raw Polymarket-style share prices into clean probability estimates for cross-referencing against models, other venues, or sportsbook odds. Target environment: Polymarket and similar share-price prediction markets (works with the polymarket-clob-fetcher skill's output).

**`orderbook-imbalance-calc`** — Calculates order flow imbalance (OFI) and static volume imbalance across L2/L4 order book levels to produce a near-term micro-momentum signal. Used to bias short-horizon execution and entry timing within the sub-bot system, complementing the CUSUM change-point detection already in use. Target environment: any L2/L4 book snapshot or stream, most commonly Hyperliquid's l2Book/l4Book WebSocket feed (see hl-grpc-ticker-stream).

**`correlation-matrix-builder`** — Generates cross-token Pearson correlation matrices over shifting rolling timeframes from OHLCV or return series, and tracks how correlation structure evolves over time. Used for sub-bot portfolio construction (avoiding over-concentrated correlated exposure across nodes), regime-aware pair selection for basis/relative-value strategies, and flagging correlation breakdowns that matter for risk management. Target environment: any set of assets with aligned price history, most commonly Hyperliquid perps/spot via hl-historical-candles.

## 3. Execution & wallet infrastructure

**`hl-atomic-bulk-order`** — Wraps Hyperliquid's bulk order placement (multiple orders in a single signed action) for instant multi-position routing across the sub-bot system — entering several legs of a spread, a basis trade, or a multi-asset rebalance atomically rather than as separate sequential requests. Target environment: Hyperliquid perps & spot, via the official Python/TS SDKs or raw exchange endpoint.

**`hl-approve-agent-wallet`** — Spins up an ephemeral agent (API) wallet and registers it against a Hyperliquid master account via the approveAgent action, so sub-bots can sign trading actions without ever holding the master private key. Covers generation, approval, funding-account separation, expiry, and revocation. Target environment: Hyperliquid perps & spot.

**`paraswap-cowswap-router`** — Constructs and signs MEV-protected, intent-based orders through CoW Protocol and ParaSwap (rebranded Velora in 2026) for EVM-chain swaps — signing an off-chain intent rather than broadcasting a public-mempool transaction, so solvers/resolvers compete to fill without exposing the trade to sandwich bots. Target environment: Ethereum, Arbitrum, Base, Gnosis Chain, Polygon (CoW Protocol); broader EVM coverage via ParaSwap/Velora.

**`solana-jupiter-swap`** — Routes programmatic token swaps on Solana through Jupiter's aggregator API (quote → swap-instructions/transaction → sign → submit) using a private-key-controlled wallet. Covers the Metis routing engine's quote/swap flow, slippage and priority-fee configuration, and key-handling practices for unattended execution. Target environment: Solana, any SPL token pair Jupiter routes.

**`hl-modify-twap-vwap-order`** — Orchestrates Hyperliquid's native TWAP order type and a custom-built VWAP execution layer to scale positions in or out over time without moving the book — covers the twapOrder action, its built-in catch-up/slippage mechanics, monitoring running TWAPs, and how to approximate VWAP (which Hyperliquid has no native order type for) on top of it. Target environment: Hyperliquid perps & spot.

**`pred-market-outcome-buy`** — Handles the outcome/share-token identification and encoding needed to actually place a buy order on prediction-market venues — Hyperliquid's HIP-4 outcome markets (merged Yes/No order books, asset-ID scheme) and Polymarket (clobTokenIds, condition IDs) — since both require resolving a human-readable market into the right token/asset identifier before an order can be submitted at all. Target environment: Hyperliquid HIP-4 outcome markets, Polymarket CLOB.

## 4. Validation & testing pipeline

**`event-driven-backtester`** — A vector-free, loop-based event simulator accounting for fills, fees, and latency slips. Used to backtest sub-bot strategies (CUSUM, OFI, basis, regime-gated) with realistic execution mechanics rather than optimistic vectorized approximations, before deploying to the live sub-bot/master-bot system. Target environment: any OHLCV/tick/order-book history, most commonly Hyperliquid data via hl-historical-candles / hl-grpc-ticker-stream.

**`monte-carlo-risk-sim`** — Simulates thousands of random permutations of a strategy's equity curve to forecast maximum drawdown limits and other risk statistics beyond what a single historical backtest can show. Used to size positions responsibly and set risk limits for sub-bots before committing capital, using the output of event-driven-backtester as input. Target environment: any per-trade or per-period P&L series, most commonly output from event-driven-backtester.

**`forward-test-shadow-broker`** — Acts as a virtual mock exchange, matching live WebSocket feeds against agent orders without committing real capital — for forward-testing sub-bot strategies against live, current market conditions after backtesting but before going live. Target environment: any live market data feed, most commonly Hyperliquid's WebSocket via hl-grpc-ticker-stream, paired with the same strategy/execution code path used in production.

**`cross-validation-walk-forward`** — Automatically splits and steps historical data to run walk-forward optimizations, validating strategy parameters out-of-sample across rolling windows to guard against overfitting. Used to check whether a strategy's backtested edge (from event-driven-backtester) generalizes beyond the specific window it was tuned on, before proceeding to forward-test-shadow-broker. Target environment: any historical OHLCV/trade series, most commonly Hyperliquid candles via hl-historical-candles.

**`bot-pnl-heartbeat`** — A standardized telemetry parser and schema allowing sub-bots to report current position size, margin usage, and real-time PnL to the master bot. Used to give the master-bot orchestration layer a consistent, low-latency view across all sub-bots/nodes regardless of which strategy or venue each one runs, for aggregate risk monitoring and kill-switch decisions. Target environment: the multi-node sub-bot/master-bot architecture, any venue (Hyperliquid, Solana DEXs, prediction markets).

## 5. Orchestration & risk control

**`sub-bot-spawner`** — Dynamically instantiates a new thread, process, or Docker container running a specific sub-bot strategy when triggered — by the master-bot's own logic (e.g. regime-classifier flags an opportunity a currently-idle strategy handles) or a manual/scheduled trigger. Covers process vs. container tradeoffs, resource isolation, and clean startup/teardown so spawned sub-bots integrate correctly with the rest of the sub-bot/master-bot system. Target environment: the multi-node sub-bot/master-bot architecture, any strategy/venue.

**`emergency-circuit-breaker`** — Instantly flattens a sub-bot's positions and revokes its trading credentials when specific risk parameters are violated — a fail-safe kill-switch triggered by the master-bot's risk monitoring (drawdown breach, margin-ratio breach, heartbeat loss, anomalous behavior) rather than normal strategy exit logic. Target environment: the multi-node sub-bot/master-bot architecture, any venue (Hyperliquid, Solana DEXs, EVM aggregators, prediction markets).

**`state-persister`** — Saves sub-bot run state, trailing stops, and execution logs to a lightweight embedded database (SQLite or Redis) so sub-bots can recover cleanly after a crash/restart without losing position context, and so the master-bot and post-hoc analysis tools have a durable record. Target environment: the multi-node sub-bot/master-bot architecture, any strategy/venue.

**`master-capital-allocator`** — Calculates and pushes Kelly criterion or risk-parity sizing updates to all active sub-bots based on recent performance, replacing static per-bot allocations with a dynamic capital allocation that scales winning strategies up and losing/riskier ones down. Target environment: the multi-node sub-bot/master-bot architecture, drawing performance data from bot-pnl-heartbeat and risk estimates from monte-carlo-risk-sim / correlation-matrix-builder.

**`portfolio-var-monitor`** — Computes total structural portfolio Value at Risk (VaR) across all combined sub-bots, accounting for cross-strategy and cross-asset correlation rather than summing each sub-bot's risk in isolation. Target environment: the multi-node sub-bot/master-bot architecture; draws position data from bot-pnl-heartbeat and correlation structure from correlation-matrix-builder.

## 6. Monitoring & alerting gaps

**`cusum-changepoint-detector`** — Implements CUSUM (cumulative sum) change-point detection to flag when a price/return series has shifted mean or regime, distinguishing genuine structural breaks from normal noise. Used as the core trigger for sub-bot entries/regime transitions across the system — referenced throughout regime-classifier, orderbook-imbalance-calc, and sub-bot-spawner as the existing detection layer those skills complement, not duplicate. Target environment: any price/return/OFI series, most commonly Hyperliquid candles or tick data.

**`liquidation-cluster-mapper`** — Estimates where leveraged positions are likely to cluster and cascade-liquidate on Hyperliquid perps, combining open interest, funding/premium, and a modeled leverage distribution into a probability-weighted liquidation-price map — since no venue exposes aggregate cross-account liquidation levels directly. Used for liquidation-cluster positioning: anticipating where cascades are likely to accelerate a move, informing entry/exit timing and stop placement around those zones. Target environment: Hyperliquid perps, cross-referenced against dex-pool-scanner for on-chain venues.

**`alert-dispatcher`** — Routes alerts from across the sub-bot/master-bot system (circuit breaker trips, VaR threshold breaches, heartbeat staleness, allocator rebalances) to the right channel and urgency level — Telegram/Slack for routine visibility, paging for anything requiring immediate human action. Referenced throughout the system (emergency-circuit-breaker's alert.page_human, portfolio-var-monitor's threshold surfacing) as the notification layer those skills call into rather than re-implement. Target environment: the multi-node sub-bot/master-bot architecture, any alert source.

**`execution-quality-analyzer`** — Performs post-trade transaction cost analysis (TCA) — comparing realized fill prices against arrival-price and other benchmarks to measure actual slippage, timing cost, and fee drag per bot/strategy/venue. Closes the loop referenced in hl-modify-twap-vwap-order ('log every child fill to compute realized slippage') and forward-test-shadow-broker (comparing shadow-predicted vs realized execution cost). Target environment: fills from any venue, most commonly sourced from state-persister's execution log.

**`venue-health-monitor`** — Continuously monitors uptime, latency, and rate-limit headroom across every connected venue and data source (Hyperliquid REST/WebSocket, Solana/EVM RPCs, Polymarket, DefiLlama) so the master-bot can distinguish 'my strategy has no edge right now' from 'the infrastructure underneath it is degraded' — and so sub-bot-spawner and emergency-circuit-breaker can factor infra health into their decisions. Target environment: every external dependency in the sub-bot/master-bot system.

## 7. Coordination & secure infrastructure

**`cross-bot-hedging-coordinator`** — Scans multi-bot open positions to detect when two different sub-bots are net-long and net-short the exact same exposure — burning capital on fees/spread/funding for a net position that's smaller (or zero) once netted, without either bot being aware of the other. Target environment: the multi-node sub-bot/master-bot architecture, any venue combination where two independently-run strategies could end up trading the same underlying exposure.

**`regime-hot-swapper`** — Signals running sub-bots to switch internal logic profiles in place — e.g. instructing a grid bot to widen spacing because volatility just spiked, or a trend-follower to tighten stops going into a choppier regime — without tearing down and respawning the bot. Target environment: the multi-node sub-bot/master-bot architecture, triggered by regime-classifier and/or cusum-changepoint-detector output.

**`kms-wallet-signer`** — Interfaces with AWS KMS, Google Cloud KMS, or an HSM to sign raw EVM/Solana transactions using a secp256k1/ed25519 key that never leaves the hardware/cloud security boundary — the private key material is never loaded into application memory, unlike the raw-keypair patterns used elsewhere in this system (solana-jupiter-swap, paraswap-cowswap-router). Target environment: any EVM chain (via secp256k1 asymmetric KMS keys) and, with caveats noted below, Solana (via ed25519 KMS support where available).

**`rpc-failover-manager`** — Continuously monitors and rotates across multiple private RPC providers (QuickNode, Alchemy, Helius, etc.) per chain to avoid rate limits, degraded responses, or dropped connections during high-congestion events — extending venue-health-monitor's health-tracking pattern specifically to the RPC-provider layer that on-chain execution (solana-jupiter-swap, paraswap-cowswap-router, onchain-gas-oracle) depends on. Target environment: any chain with multiple available RPC providers — Ethereum/L2s (Alchemy, QuickNode, Infura), Solana (Helius, QuickNode, Triton).

**`gas-station-refueler`** — Automatically bridges/sends small balances of native gas tokens (ETH, SOL, POL/MATIC, etc.) from a funding wallet to sub-wallets and agent wallets running low on on-chain balance, so execution never stalls on 'insufficient balance for gas' — while keeping the automated transfer path tightly scoped (allowlisted destinations, hard caps, one-directional) given it moves real funds without a human confirming each transfer. Target environment: any EVM chain and Solana, wherever sub-bots/agent wallets need native gas to operate.

## 8. Backtesting extensions

**`multi-strategy-portfolio-backtester`** — Combines multiple sub-bot strategies' individual backtests into one portfolio-level backtest, accounting for shared capital, cross-strategy correlation, and netting effects that per-strategy backtests miss entirely. Target environment: multiple event-driven-backtester outputs run over the same historical period, combined via correlation-matrix-builder's covariance structure.

**`parameter-sensitivity-heatmap`** — Runs a strategy across a grid of parameter combinations and visualizes the resulting performance surface (Sharpe, drawdown, return) to distinguish a genuinely robust parameter region from a narrow, overfit peak. Complements cross-validation-walk-forward's temporal robustness check with a parameter-space robustness check. Target environment: any strategy runnable through event-driven-backtester with 2-3 tunable parameters.

**`historical-data-quality-validator`** — Screens historical OHLCV/tick data for gaps, duplicates, outliers, and other data-quality issues before it's used in backtesting or signal research — garbage-in-garbage-out prevention for event-driven-backtester, correlation-matrix-builder, and every other skill in this system that consumes historical-data-fetching skill output. Target environment: candle/tick data from hl-historical-candles or any other historical source.

## 9. DeFi

**`lending-rate-scanner`** — Scans supply and borrow rates across DeFi lending protocols (Aave, Compound, and similar) across chains to identify yield opportunities and borrowing-cost arbitrage. Feeds basis-arb-calc-style carry analysis and flashloan-arb-executor's cost accounting. Target environment: Aave V3 (all deployed chains), Compound V3, any lending protocol exposing on-chain reserve data.

**`flashloan-arb-executor`** — Wraps Aave V3 flash loan primitives (flashLoanSimple/flashLoan) to execute capital-free arbitrage — borrow, trade across the price discrepancy, repay principal plus premium, keep the spread — atomically within one transaction. Target environment: any EVM chain with an Aave V3 deployment, paired with dex-pool-scanner for opportunity detection and onchain-gas-oracle for cost accounting.

**`uniswap-flash-swap-wrapper`** — Wraps Uniswap V2/V3's native flash swap mechanics (borrow a pool's tokens, use them, repay within the same transaction) as a capital-source alternative to Aave flash loans — useful when the arb path already routes through a specific Uniswap-family pool, avoiding a separate protocol's premium and an extra external call. Target environment: Uniswap V2-fork and V3-fork pools (SushiSwap, PancakeSwap V3, and similar) on any EVM chain.

**`defi-liquidation-bot`** — Monitors Aave V3 (and similar) borrow positions for health factor breaches and executes profitable liquidationCall transactions, optionally funded via flashloan-arb-executor's flashloan mechanism so no standing capital is needed to cover the debt being repaid. This is a protocol-sanctioned, permissionless, economically-incentivized role in DeFi lending markets — protocols pay a liquidation bonus specifically to attract this activity, since it keeps the lending protocol solvent. Target environment: Aave V3 (any deployed chain), Compound V3, or similar over-collateralized lending protocols.

**`impermanent-loss-calculator`** — Calculates impermanent loss (IL) for AMM liquidity positions — both classic constant-product (Uniswap V2-style, full-range) and concentrated-liquidity (Uniswap V3-style, range-bound) — and nets it against accumulated fee income to determine whether an LP position is actually profitable relative to simply holding the underlying assets. Target environment: any constant-product or concentrated-liquidity AMM position, most commonly assessed via dex-pool-scanner's pool data.

**`concentrated-liquidity-rebalancer`** — Manages and rebalances Uniswap V3-style concentrated liquidity positions — deciding range width based on volatility regime, detecting when price has exited the active range, and executing reposition transactions (withdraw, re-mint at a new range) when the cost of staying out-of-range exceeds the cost of rebalancing. Target environment: Uniswap V3 and Algebra-style (Camelot) concentrated-liquidity pools, informed by impermanent-loss-calculator and regime-classifier.

**`yield-vault-scanner`** — Scans yield-aggregator vaults (Yearn-style auto-compounding strategies, liquid staking, and similar ERC-4626 vaults) across protocols and chains for net APY, fee structure, and underlying strategy risk, to identify where idle capital should be deployed. Target environment: any ERC-4626-compliant vault or similar yield-bearing wrapper, cross-referenced with lending-rate-scanner and defillama-tvl-fetcher.

## 10. Arbitrage

**`triangular-arb-scanner`** — Detects triangular arbitrage opportunities — price discrepancies across three (or more) trading pairs within a single venue that imply a profitable closed-loop trade (A to B to C back to A) — accounting for fees and slippage at each leg. Target environment: any venue with multiple cross-listed pairs for the same set of assets, most commonly Hyperliquid spot markets or a single DEX with several pools.

**`cross-dex-arb-scanner`** — Scans the same asset pair's price across multiple DEXs (Uniswap, SushiSwap, Raydium, Camelot, and others per dex-pool-scanner's coverage) to detect exploitable price discrepancies, sized against real depth on both sides. Target environment: any set of DEX pools trading the same underlying asset pair, cross-chain or same-chain, feeding flashloan-arb-executor or uniswap-flash-swap-wrapper for execution.

**`cex-dex-arb-monitor`** — Monitors price gaps between centralized venues (Hyperliquid spot/perp) and decentralized venues (Uniswap, Raydium, and other DEXs) for the same or economically-equivalent asset, distinct from basis-arb-calc's spot-vs-perp-on-the-same-venue focus and cross-dex-arb-scanner's DEX-vs-DEX focus. Target environment: Hyperliquid spot/perp prices via hl-grpc-ticker-stream, DEX prices via dex-pool-scanner.

**`cross-chain-bridge-arb-monitor`** — Monitors price and liquidity discrepancies for the same asset (or its wrapped/bridged representations) across chains, netting out bridge time, bridge fees, and destination-chain gas before flagging a genuinely capturable arbitrage — distinct from cross-dex-arb-scanner's same-chain focus. Target environment: any asset with liquid markets on two or more chains connected by a bridge, cross-referenced with defillama-tvl-fetcher for bridge/chain liquidity context.

## 11. Flashloans (additional)

**`flashloan-collateral-swap`** — Uses a flashloan to atomically swap the collateral type backing an existing lending position (e.g. move from ETH collateral to a liquid-staking derivative) without needing to fully unwind and reopen the position — a treasury/risk-management operation distinct from flashloan-arb-executor's profit-seeking arbitrage use of the same primitive. Target environment: Aave V3 or similar over-collateralized lending protocols supporting flashloans.

## 12. New token launch sniping

**`new-pool-launch-detector`** — Watches DEX factory contracts (and Solana program logs for Raydium-style launches) for newly created liquidity pools in near-real-time, as the first-mover detection layer for evaluating and potentially acting on new token launches. Target environment: Uniswap V2/V3-style factories on any EVM chain, Raydium pool initialization on Solana. Pair with token-safety-screener before any execution — detection alone says nothing about whether a new pool is safe to interact with.

**`token-safety-screener`** — Runs pre-trade safety checks on a newly detected token/pool — honeypot simulation, mint/blacklist authority checks, liquidity-lock verification, ownership renouncement, and holder concentration — before any capital is committed. This is a protective gate, not an execution skill: its entire purpose is filtering out scam/malicious tokens before new-pool-launch-detector's speed advantage gets used to buy something worthless. Target environment: any newly launched ERC-20/SPL token, checked immediately after detection and before any snipe-execution-router call.

**`snipe-execution-router`** — Handles execution for buying into a newly launched token immediately after it clears token-safety-screener — gas/priority-fee bidding strategy for fast inclusion, slippage tolerance appropriate for a newly-created, thin-liquidity pool, and private-mempool submission to avoid being front-run on the way in. Target environment: any newly launched EVM or Solana token pool that has already passed safety screening; never call this directly off new-pool-launch-detector's output.

## 13. Other DeFi/MEV infrastructure

**`mev-protection-submitter`** — Submits transactions through private mempools/relays (Flashbots Protect and similar) instead of the public mempool, so pending transactions aren't visible to sandwich bots or other MEV extraction before they confirm. This is the shared submission layer referenced throughout this system's on-chain execution skills (flashloan-arb-executor, defi-liquidation-bot, cross-dex-arb-scanner, snipe-execution-router) rather than something each implements separately. Target environment: any EVM chain with private-relay infrastructure (Ethereum mainnet via Flashbots, with growing support elsewhere); Solana's architecture differs — see the Solana note below.

**`oracle-price-deviation-monitor`** — Monitors the gap between an on-chain oracle's reported price (Chainlink, Pyth, or a protocol's internal oracle) and real-time market price across venues, both as a risk check (avoid trading/lending against a stale or lagging oracle) and an opportunity signal (oracle lag creates a brief, mechanical arbitrage window against anything priced off that oracle). Target environment: any DeFi protocol relying on an on-chain price oracle, cross-referenced with basis-arb-calc, defi-liquidation-bot, and dex-pool-scanner's live price feeds.

**`token-unlock-vesting-tracker`** — Tracks token vesting/unlock schedules (cliff and linear unlock calendars) across projects to anticipate supply-driven price pressure events ahead of time — a common systematic input for both discretionary and systematic crypto positioning, complementing this system's on-chain/market-structure signals with a scheduled, fundamentals-driven one. Target environment: any token with a publicly documented or on-chain-verifiable vesting schedule.

