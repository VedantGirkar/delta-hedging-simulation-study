# Delta Hedging Project

This project studies the performance of periodical delta hedging for a European call option on 100,000 shares under geometric Brownian motion.

## Project stages

- Stage 1: pricing, payoff, and time-grid foundation
- Stage 2: GBM path simulation
- Stage 3: single-path delta hedge engine
- Stage 4: multi-path hedging simulation
- Stage 5: confidence intervals and precision control
- Stage 6: comparison tables and chart generation
- Stage 7: dashboard app for stats, tables, and charts
- Stage 8: cleanup/refactor and unified final pipeline

## Main outputs

- `results/tables/weekly_daily_comparison.csv`
- `results/tables/std_xt_paths.csv`
- `results/figures/`
- `results/dashboard/delta_hedging_dashboard.html`

## How to run

Run the unified pipeline from the project root:

```bash
python run_all.py
```

Run individual stages if needed:

```bash
python scripts/run_stage5.py
python scripts/run_stage6.py
python scripts/run_stage7.py
```

## Notes

- The current precision-control setup is capped at 200 paths for debugging and development.
- For the final submission-quality study, increase the maximum number of paths until the relative error target is met.
