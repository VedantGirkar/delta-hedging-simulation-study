import csv as _csv
from pathlib import Path
import shutil
from Config import PROJECT_NAME, RESULTS_DIR, BASE_DIR


def _load_terminal_costs_table(results_dir: Path) -> str:
    path = results_dir / "tables" / "all_terminal_costs.csv"
    if not path.exists():
        return "*(Run Stage 6 first to generate terminal costs)*"
    rows = list(_csv.DictReader(open(path)))
    weekly_rows = [r for r in rows if r["schedule"] == "weekly"]
    daily_rows  = [r for r in rows if r["schedule"] == "daily"]

    def make_md_table(data, label):
        lines = [f"### {label}\n",
                 "| Path | X(T) ($) | In the Money? |",
                 "|---|---|---|"]
        for r in data:
            lines.append(f"| {r['path']} | {float(r['X_T']):,.2f} | {r['ITM']} |")
        return "\n".join(lines)

    return make_md_table(weekly_rows, "Weekly — All Simulated X(T)") + \
           "\n\n" + make_md_table(daily_rows, "Daily — All Simulated X(T)")


def _load_std_xt_table(results_dir: Path) -> str:
    path = results_dir / "tables" / "std_xt_paths.csv"
    if not path.exists():
        return "*(Run Stage 6 first)*"
    rows = list(_csv.DictReader(open(path)))
    weekly = [r for r in rows if r["schedule"] == "weekly"]
    daily  = [r for r in rows if r["schedule"] == "daily"]

    def make_md(data, label):
        lines = [f"### {label}\n",
                 "| Step | t | Std of X(t) ($) |",
                 "|---|---|---|"]
        for i, r in enumerate(data):
            lines.append(f"| {i} | {float(r['t']):.4f} | {float(r['std_X_t']):,.2f} |")
        return "\n".join(lines)

    return make_md(weekly, "Weekly — Std of X(t)") + "\n\n" + make_md(daily, "Daily — Std of X(t)")


def build_report_text(stage6: dict, stage7: dict) -> str:
    w   = stage6['weekly_summary']
    d   = stage6['daily_summary']
    bsm = stage6['benchmark_total_bsm_price']

    terminal_table = _load_terminal_costs_table(RESULTS_DIR)
    std_xt_table   = _load_std_xt_table(RESULTS_DIR)

    return f"""# Delta Hedging Simulation Report
**Course:** 16:958:535:01
**Random Seed:** 42 (fixed for reproducibility)
**Paths per study:** {w['n_paths']} (weekly), {d['n_paths']} (daily)

---

## 1. Project Objective

A company sold a European call option on 100,000 shares. This simulation study:

1. Estimates E[X(T)] and Var^(1/2)(X(T)) for weekly and daily delta hedging.
2. Constructs a 95% CI for E[X(T)] with error margin no greater than 2% of E[X(T)].
3. Checks whether that CI covers the BSM price of the entire option.
4. Constructs a 95% CI for P(option ITM at T).
5. Plots and tables the standard deviation of X(t) against t.
6. Compares weekly and daily rebalancing.

---

## 2. Model Inputs

| Parameter | Value |
|---|---|
| S0 | 49.00 |
| K | 50.00 |
| T | 20/52 years |
| r | 0.05 |
| sigma | 0.20 |
| mu | 0.13 |
| Shares | 100,000 |

---

## 3. BSM Benchmark

| Quantity | Value |
|---|---|
| BSM call price (per share) | $2.4005 |
| BSM total option value (100,000 shares) | ${bsm:,.2f} |
| Delta at t=0 | 52.22% |

---

## 4. Simulation Results Summary

### Weekly Rebalancing

| Metric | Value |
|---|---|
| Paths simulated | {w['n_paths']} |
| Mean X(T) | ${float(w['mean_X_T']):,.2f} |
| Std X(T) | ${float(w['std_X_T']):,.2f} |
| 95% CI for E[X(T)] | [${float(w['mean_ci_lower']):,.2f}, ${float(w['mean_ci_upper']):,.2f}] |
| CI half-width as % of mean | ~{abs((float(w['mean_ci_upper'])-float(w['mean_ci_lower']))/2/float(w['mean_X_T'])*100):.1f}% |
| Precision target met (≤2%)? | {w['target_met']} |
| CI covers BSM price? | {w['covers_bsm_price']} |
| P(ITM) estimate | {float(w['itm_probability']):.4f} |
| 95% CI for P(ITM) | [{float(w['prob_ci_lower']):.4f}, {float(w['prob_ci_upper']):.4f}] |

### Daily Rebalancing

| Metric | Value |
|---|---|
| Paths simulated | {d['n_paths']} |
| Mean X(T) | ${float(d['mean_X_T']):,.2f} |
| Std X(T) | ${float(d['std_X_T']):,.2f} |
| 95% CI for E[X(T)] | [${float(d['mean_ci_lower']):,.2f}, ${float(d['mean_ci_upper']):,.2f}] |
| CI half-width as % of mean | ~{abs((float(d['mean_ci_upper'])-float(d['mean_ci_lower']))/2/float(d['mean_X_T'])*100):.1f}% |
| Precision target met (≤2%)? | {d['target_met']} |
| CI covers BSM price? | {d['covers_bsm_price']} |
| P(ITM) estimate | {float(d['itm_probability']):.4f} |
| 95% CI for P(ITM) | [{float(d['prob_ci_lower']):.4f}, {float(d['prob_ci_upper']):.4f}] |

---

## 5. Standard Deviation of X(t) Against t

{std_xt_table}

---

## 6. Weekly vs Daily Comparison

| Metric | Weekly | Daily |
|---|---|---|
| Mean X(T) | ${float(w['mean_X_T']):,.2f} | ${float(d['mean_X_T']):,.2f} |
| Std X(T) | ${float(w['std_X_T']):,.2f} | ${float(d['std_X_T']):,.2f} |
| P(ITM) | {float(w['itm_probability']):.4f} | {float(d['itm_probability']):.4f} |
| CI covers BSM? | {w['covers_bsm_price']} | {d['covers_bsm_price']} |
| Precision met? | {w['target_met']} | {d['target_met']} |

---

## 7. All Simulated Terminal Costs X(T)

Every simulated path's terminal hedge cost and ITM indicator is listed below.

{terminal_table}

---

## 8. Discussion

E[X(T)] estimates are ${float(w['mean_X_T']):,.2f} (weekly) and ${float(d['mean_X_T']):,.2f}
(daily), both substantially larger than the BSM benchmark of ${bsm:,.2f}. X(T) is the gross
cumulative cost of the self-financed stock account before netting the premium received.

Std X(T) is ${float(w['std_X_T']):,.2f} (weekly) and ${float(d['std_X_T']):,.2f} (daily),
reflecting high variability across paths, which is expected under discrete hedging.

The 95% CIs for E[X(T)] do not cover the BSM price under the current 200-path cap.
CI half-widths are ~10-11%, well above the 2% target. More paths are needed.

P(ITM) estimates of {float(w['itm_probability']):.4f} (weekly) and {float(d['itm_probability']):.4f}
(daily) exceed N(d2) ~ 0.466 because the simulation uses real-world drift mu=0.13 > r=0.05.

Weekly and daily results are similar at 200 paths, suggesting hedging frequency alone
does not dramatically shift the X(T) distribution here. A larger study is needed to
determine whether weekly rebalancing is sufficient.

---

## 9. Appendix — Code

All source code is in appendix_code/. Reproduce results with:

    python run_all.py

Key files: Config.py, Main.py, core/bsm.py, core/gbm.py, core/hedge_engine.py,
analysis/confidence_intervals.py, analysis/precision_control.py,
outputs/charts.py, outputs/tables.py, pipeline/final_pipeline.py
"""


def build_submission_package() -> dict:
    from Main import build_stage6_summary, build_stage7_summary

    stage6 = build_stage6_summary()
    stage7 = build_stage7_summary()

    submission_dir = BASE_DIR / 'submission'
    if submission_dir.exists():
        shutil.rmtree(submission_dir)
    submission_dir.mkdir(parents=True, exist_ok=True)

    appendix_dir = submission_dir / 'appendix_code'
    appendix_dir.mkdir(parents=True, exist_ok=True)

    for rel in ['Config.py', 'Main.py', 'run_all.py', 'README.md',
                'core', 'analysis', 'outputs', 'pipeline', 'scripts', 'report']:
        src = BASE_DIR / rel
        dst = appendix_dir / rel
        if src.is_dir():
            shutil.copytree(src, dst)
        elif src.exists():
            shutil.copy2(src, dst)

    report_file = submission_dir / 'final_report.md'
    report_file.write_text(build_report_text(stage6, stage7), encoding='utf-8')

    summary_file = submission_dir / 'submission_summary.txt'
    summary_file.write_text(
        f"Report: {report_file}\nDashboard: {stage7['dashboard_file']}\n",
        encoding='utf-8'
    )

    copied_count = sum(1 for _ in appendix_dir.rglob('*'))
    return {
        'submission_dir': submission_dir,
        'report_file': report_file,
        'summary_file': summary_file,
        'appendix_dir': appendix_dir,
        'copied_file_count': copied_count,
    }