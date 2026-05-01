from pathlib import Path
import shutil
from Config import PROJECT_NAME, RESULTS_DIR
from Main import build_stage6_summary, build_stage7_summary


def build_report_text(stage6, stage7):
    return f"""# Delta Hedging Simulation Report

## Project objective
Study weekly and daily delta hedging for a European call on 100,000 shares.

## Inputs
- S0 = 49
- K = 50
- T = 20/52
- r = 0.05
- sigma = 0.2
- mu = 0.13

## Weekly vs daily results
- Weekly mean X(T): {stage6['weekly_summary']['mean_X_T']:.2f}
- Daily mean X(T): {stage6['daily_summary']['mean_X_T']:.2f}
- Weekly ITM probability: {stage6['weekly_summary']['itm_probability']:.4f}
- Daily ITM probability: {stage6['daily_summary']['itm_probability']:.4f}
- Weekly CI covers BSM price: {stage6['weekly_summary']['covers_bsm_price']}
- Daily CI covers BSM price: {stage6['daily_summary']['covers_bsm_price']}

## Dashboard
- {stage7['dashboard_file']}

## Discussion
Weekly and daily hedging both produced terminal hedge-cost distributions that were well above the BSM option price benchmark under the current development-scale path cap. The daily rebalancing results were more stable than weekly, but neither study yet met the 2% precision target.

## Appendix
See appendix_code for the project files used to generate the results.
"""


def build_submission_package():
    stage6 = build_stage6_summary()
    stage7 = build_stage7_summary()
    submission_dir = PROJECT_NAME / 'submission'
    if submission_dir.exists():
        shutil.rmtree(submission_dir)
    submission_dir.mkdir(parents=True, exist_ok=True)
    appendix_dir = submission_dir / 'appendix_code'
    appendix_dir.mkdir(parents=True, exist_ok=True)
    for rel in [
        'config.py', 'main.py', 'run_all.py', 'README.md',
        'core', 'analysis', 'outputs', 'pipeline', 'scripts',
    ]:
        src = PROJECT_NAME / rel
        dst = appendix_dir / rel
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
    report_file = submission_dir / 'final_report.md'
    report_file.write_text(build_report_text(stage6, stage7), encoding='utf-8')
    summary_file = submission_dir / 'submission_summary.txt'
    summary_file.write_text(f"Report: {report_file}\nDashboard: {stage7['dashboard_file']}\n", encoding='utf-8')
    copied_count = sum(1 for _ in appendix_dir.rglob('*'))
    return {'submission_dir': submission_dir, 'report_file': report_file, 'summary_file': summary_file, 'appendix_dir': appendix_dir, 'copied_file_count': copied_count}
