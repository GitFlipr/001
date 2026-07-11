# From skills to system: architecture blueprint

This turns the 63 SKILL.md files into an actual running environment — either a full production upgrade or a standalone testing/paper-trading setup. The core decision this document makes explicit: **not every skill should become the same kind of thing.** Some belong as always-on background services, some as callable tool functions, some as plain imported code libraries, and a small number as genuine LLM-driven agents. Treating all 63 as "agents" would be slower, less auditable, and in a few cases (anything that moves funds or trips a circuit breaker) actively dangerous. Treating all 63 as static code with no agent anywhere wastes the one place an LLM genuinely adds value: research and judgment-heavy synthesis.

## 1. The four implementation primitives

| Primitive | What it is | Use when |
|---|---|---|
| **Daemon / service** | Always-running background process, no request-response — just continuously does its job and publishes state | The skill's job is inherently continuous (streaming data, monitoring, heartbeating) |
| **Tool / function** | Callable on demand, stateless or thin-state, returns a result and exits | The skill answers a specific question or performs a specific bounded action when asked |
| **Library / module** | Imported code with no independent runtime at all | Pure computation — math, statistics, formulas — with no orchestration or external calls of its own |
| **Agent / sub-agent** | An LLM-driven reasoning loop with its own context and tool access | The task is genuinely open-ended, judgment-heavy, or benefits from natural-language synthesis — and is **not** on a hard latency or safety-critical path |

**The one rule that matters most**: anything safety-critical, latency-sensitive, or fund-moving (circuit breaker, gas refueling, order signing, allocator sizing) is a deterministic service or tool — never an agent making a judgment call in the loop. An LLM should never be the thing deciding in real time whether to flatten a position; it can absolutely be the thing that reviews *why* the breaker tripped afterward and writes up what happened.

## 2. Full mapping — all 63 skills

### Daemons / services (always-running, no request-response)
These run continuously, one process each (or grouped by venue), publishing to the shared message bus described in Section 4.

`hl-grpc-ticker-stream` · `hl-historical-candles` (polling mode) · `dex-pool-scanner` · `venue-health-monitor` · `rpc-failover-manager` · `new-pool-launch-detector` · `bot-pnl-heartbeat` (the aggregation side) · `alert-dispatcher` (the dispatch side) · `state-persister` (the write side)

### Tools / callable functions (invoked on demand, bounded action or answer)
These are the ones worth exposing as an MCP server (Section 5) so Claude or another agent can call them directly.

*Data lookups*: `defillama-tvl-fetcher` · `polymarket-clob-fetcher` · `hl-funding-tracker-2` · `lending-rate-scanner` · `yield-vault-scanner` · `token-unlock-vesting-tracker` · `oracle-price-deviation-monitor`

*Execution actions* (fund-moving — see the guardrail note in Section 6 before exposing these): `hl-atomic-bulk-order` · `hl-approve-agent-wallet` · `paraswap-cowswap-router` · `solana-jupiter-swap` · `hl-modify-twap-vwap-order` · `pred-market-outcome-buy` · `flashloan-arb-executor` · `uniswap-flash-swap-wrapper` · `flashloan-collateral-swap` · `defi-liquidation-bot` · `snipe-execution-router` · `gas-station-refueler` · `mev-protection-submitter` · `kms-wallet-signer`

*Orchestration actions*: `sub-bot-spawner` · `emergency-circuit-breaker` · `regime-hot-swapper`

*Screening / one-shot analysis*: `token-safety-screener` · `historical-data-quality-validator`

### Libraries / modules (pure computation, imported by the above — no independent runtime)
`regime-classifier` · `basis-arb-calc` · `predict-market-prob-calc` · `orderbook-imbalance-calc` · `correlation-matrix-builder` · `cusum-changepoint-detector` · `liquidation-cluster-mapper` · `impermanent-loss-calculator` · `triangular-arb-scanner` · `cross-dex-arb-scanner` · `cex-dex-arb-monitor` · `cross-chain-bridge-arb-monitor` · `execution-quality-analyzer` · `portfolio-var-monitor` · `master-capital-allocator` · `cross-bot-hedging-coordinator` · `concentrated-liquidity-rebalancer` · `onchain-gas-oracle`

These get called *by* sub-bot workers and the risk control plane on every decision cycle — they don't run standalone.

### Validation / research pipeline (offline, batch — not live-running at all)
`event-driven-backtester` · `monte-carlo-risk-sim` · `cross-validation-walk-forward` · `parameter-sensitivity-heatmap` · `multi-strategy-portfolio-backtester` · `forward-test-shadow-broker`

### Agent-worthy (genuine LLM reasoning loop — detailed in Section 3)
None of the 63 skills are *themselves* an agent. Three purpose-built agents are constructed **on top of** groups of the above:
- **Research agent** — uses the validation pipeline as tools
- **Ops/monitoring agent** — uses `alert-dispatcher`, `venue-health-monitor`, `portfolio-var-monitor` output as read-only context
- **Strategy-tuning agent** — uses `parameter-sensitivity-heatmap` + `cross-validation-walk-forward` to propose (never auto-deploy) new configs

## 3. Where agents actually belong

Three agents, each with a narrow, well-justified reason to be an agent rather than a script:

**Research agent.** Given a hypothesis ("does widening the CUSUM threshold during high-vol regimes improve Sharpe"), it calls `event-driven-backtester`, `parameter-sensitivity-heatmap`, `monte-carlo-risk-sim`, and `cross-validation-walk-forward` as tools, reads the results, and writes up findings in natural language — including flagging when a result looks overfit (the exact judgment call `parameter-sensitivity-heatmap`'s file describes: "broad plateau vs. narrow peak" is a visual/qualitative call, which is exactly what an LLM is good at and a fixed threshold isn't). Runs entirely offline against historical data. Zero write access to anything live.

**Ops/monitoring agent.** Subscribes to `alert-dispatcher`'s output stream and has read-only tool access to `venue-health-monitor`, `portfolio-var-monitor`, `bot-pnl-heartbeat`. Its job is triage and summarization: "three alerts fired in the last ten minutes, here's the likely shared root cause, here's what I'd check first" — a genuinely agentic synthesis task. It can *draft* a recommended action (e.g. "recommend manually reviewing bot X") but has no tool that lets it call `emergency-circuit-breaker` or any execution skill itself. Escalation to a human is its only write action.

**Strategy-tuning agent.** Periodically (e.g. weekly) reviews live performance via `execution-quality-analyzer` and `bot-pnl-heartbeat`, cross-references `parameter-sensitivity-heatmap` and `cross-validation-walk-forward` on recent data, and proposes a parameter change. The proposal goes into a review queue — a human (or a separate, much simpler deterministic promotion rule) approves before `regime-hot-swapper` or `master-capital-allocator` ever sees the new numbers. This agent never has write access to live parameters directly.

**Everything else stays deterministic code, including things that feel like they involve "judgment":** `regime-classifier`'s HMM/GMM output is a statistical model, not an LLM call. `master-capital-allocator`'s Kelly/risk-parity math is a formula. `emergency-circuit-breaker`'s trigger logic is `if condition: flatten()` — full stop. This is deliberate: these need to be fast (sub-second), deterministic (the same inputs always produce the same output, so they're testable), and auditable (a human can read the exact rule that fired) in a way an LLM call in the hot path cannot guarantee.

## 4. Shared infrastructure layer (build this once, everything else depends on it)

```
infra/
├── bus/            # message bus — Redis pub/sub (simplest) or NATS (if you outgrow Redis).
│                    # Every daemon publishes here; every worker subscribes. This is what
│                    # bot-pnl-heartbeat, alert-dispatcher, and regime-hot-swapper all assume exists.
├── state/           # state-persister's actual backing stores: Redis (live state) + SQLite (durable log),
│                    # per that skill's own split — don't invent a third pattern here.
├── secrets/         # kms-wallet-signer for anything beyond disposable capital;
│                    # a plain secrets manager (not env vars) for agent-wallet/hot-wallet keys
├── rpc/             # rpc-failover-manager's provider pool config, one per chain
└── registry/        # the "known wallet addresses" allowlist gas-station-refueler reads from,
                       # plus the bot registry sub-bot-spawner and emergency-circuit-breaker both need
```

Build this layer **first**, before any strategy or execution code. Every single skill above assumes at least one piece of this exists (a bus to publish to, a place to persist state, a registry to check against) — skipping straight to strategy logic means retrofitting this underneath code that already assumes it, which is backwards and expensive.

## 5. MCP server layout — what Claude (or another agent) can call directly

Wrap the **tools/callable functions** group from Section 2 as MCP servers, split by risk tier so permissions can differ:

```
mcp-servers/
├── market-data-mcp/       # read-only: defillama, polymarket, funding, lending rates, vesting, oracle deviation
│                           # safe to expose broadly — no side effects possible
├── screening-mcp/         # token-safety-screener, historical-data-quality-validator
│                           # read-only in effect (produces a risk report, doesn't act)
├── orchestration-mcp/      # sub-bot-spawner, regime-hot-swapper, emergency-circuit-breaker
│                           # write access, but scoped to process/config management — no fund movement
└── execution-mcp/          # everything that signs or moves funds — hl-atomic-bulk-order,
                             # solana-jupiter-swap, flashloan-arb-executor, gas-station-refueler, etc.
                             # gate this server's tool calls behind explicit confirmation in any
                             # agent-facing context; never let an agent call these autonomously
                             # in a loop without a human-approved plan for that specific action
```

The research/ops/tuning agents from Section 3 only ever get `market-data-mcp` and `screening-mcp` (read-only) plus their own validation-pipeline tools. `execution-mcp` and `orchestration-mcp` are for the deterministic control plane's own internal use, or for a human operator working through Claude Code/Cowork directly — not for an autonomous agent loop.

## 6. Guardrails that must survive the transition from "skill doc" to "running code"

Every one of these was called out in the individual skill files — this is the checklist to confirm none of them got lost in translation to actual code:

- **`gas-station-refueler`**: allowlist check and hard caps must be enforced in code before every transfer, not just documented — a refactor that "temporarily" bypasses the allowlist for testing is exactly how this guardrail gets silently dropped.
- **`emergency-circuit-breaker`**: runs in a separate process from the sub-bots it monitors, full stop. If it's a method inside the same process as a sub-bot's strategy loop, a hung/crashed sub-bot can't trip its own breaker — verify this at the deployment topology level, not just in code review.
- **`hl-approve-agent-wallet` / `kms-wallet-signer`**: master keys and KMS-backed keys never enter a sub-bot's process memory or a container image. Confirm this with an actual secrets-audit, not just a comment saying it's true.
- **`master-capital-allocator`**: must read `emergency-circuit-breaker`'s halted-bot list before every rebalance — this is an explicit cross-check in that skill's file and an easy one to forget when the two are built by different people/sprints.
- **Research agent, ops agent, tuning agent**: none of the three should have a code path — not a debug flag, not a "just this once" override — that reaches `execution-mcp`. Test this by trying to break it, not just by reading the permission config.

## 7. Phased build-out (testing setup first, production second)

**Phase 0 — Infra scaffolding.** Section 4's bus/state/secrets/rpc/registry layer, plus `venue-health-monitor` and `rpc-failover-manager` running against real venues but nothing trading. Confirms the foundation works before anything financial touches it.

**Phase 1 — Data + research environment, fully isolated.** Bring up the data daemons (`hl-grpc-ticker-stream`, `dex-pool-scanner`, etc.) and the validation pipeline (`event-driven-backtester` through `multi-strategy-portfolio-backtester`), plus the research agent. Nothing here can place an order — this phase is pure data and offline analysis, and is a complete, useful "testing setup" on its own if that's all you want right now.

**Phase 2 — Shadow/paper trading.** Add `forward-test-shadow-broker` running the *real* strategy code against live daemons, with execution routed to the shadow broker instead of a venue. This is the first point where `bot-pnl-heartbeat`, `state-persister`, and the risk control plane (`portfolio-var-monitor`, `master-capital-allocator`, `emergency-circuit-breaker`) all run for real — just against simulated fills. Stay here until `execution-quality-analyzer` shows shadow-realized costs matching backtest predictions, per that skill's own go/no-go criteria.

**Phase 3 — First live strategy, small capital.** Swap the shadow broker for real execution adapters (`hl-atomic-bulk-order` or whichever venue), on exactly one strategy, with the full risk control plane active and `emergency-circuit-breaker` thresholds set conservatively tight. Everything from Phase 2 keeps running unchanged underneath — this phase only changes where fills come from.

**Phase 4 — Scale out.** `sub-bot-spawner` brings additional strategies online, `master-capital-allocator` starts doing real dynamic sizing across more than one bot, `cross-bot-hedging-coordinator` and `portfolio-var-monitor`'s netting logic start actually mattering. Only reach this phase once Phase 3 has run long enough for `execution-quality-analyzer` and the Monte Carlo/walk-forward validation to have real live data to check against, not just backtest data.

**If you only want a testing setup, not a live upgrade**: stop at the end of Phase 2. That alone is a complete, self-contained environment — real data, real strategy code, real risk-control logic, zero capital at risk — and is the right place to spend the most time before phase 3 is even worth considering.

## 8. Suggested repo structure

```
trading-system/
├── infra/                    # Section 4
├── mcp-servers/               # Section 5
├── daemons/                   # one subfolder per Section 2 "daemon" skill
├── workers/                   # sub-bot strategy processes; import the "library" skills directly
├── control-plane/              # allocator, breaker, var-monitor, spawner — the deterministic orchestration
├── execution-adapters/         # per-venue: hyperliquid/, solana/, evm/
├── research/                   # backtester, walk-forward, monte-carlo, sensitivity heatmap + the research agent
├── shadow/                     # forward-test-shadow-broker's mock exchange
└── ops/                        # alert-dispatcher config, ops agent, runbooks
```

This mirrors Section 2's grouping directly — a skill's category above should tell you which folder its implementation lives in, with no ambiguity.
