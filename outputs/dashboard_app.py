import html
import json
from pathlib import Path
from typing import Dict

from outputs.dashboard_data import load_dashboard_payload



def _img_tag(path_str: str, alt: str) -> str:
    path = Path(path_str)
    rel = f"../figures/{path.name}"
    return f'<img src="{html.escape(rel)}" alt="{html.escape(alt)}" style="width:100%;border:1px solid #ddd;border-radius:10px;">'



def build_dashboard_html(payload: Dict[str, object]) -> str:
    comparison_rows = payload["comparison_rows"]
    figs = payload["figure_paths"]

    table_rows_html = "".join(
        f"<tr>"
        f"<td>{html.escape(row['schedule'])}</td>"
        f"<td>{float(row['n_paths']):.0f}</td>"
        f"<td>{float(row['mean_X_T']):,.2f}</td>"
        f"<td>{float(row['std_X_T']):,.2f}</td>"
        f"<td>[{float(row['mean_ci_lower']):,.2f}, {float(row['mean_ci_upper']):,.2f}]</td>"
        f"<td>{float(row['itm_probability']):.4f}</td>"
        f"<td>[{float(row['prob_ci_lower']):.4f}, {float(row['prob_ci_upper']):.4f}]</td>"
        f"<td>{html.escape(str(row['covers_bsm_price']))}</td>"
        f"<td>{html.escape(str(row['target_met']))}</td>"
        f"</tr>"
        for row in comparison_rows
    )

    weekly_row = next(row for row in comparison_rows if row["schedule"] == "weekly")
    daily_row = next(row for row in comparison_rows if row["schedule"] == "daily")

    payload_json = html.escape(json.dumps(payload))

    return f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>Delta Hedging Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 0; background: #f7f7fb; color: #1f2937; }}
    .container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
    h1, h2 {{ margin-top: 0; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 24px; }}
    .card {{ background: white; border-radius: 12px; padding: 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
    table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; }}
    th, td {{ padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: left; font-size: 14px; }}
    th {{ background: #111827; color: white; }}
    .chart-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 18px; margin-top: 20px; }}
    .note {{ font-size: 14px; color: #4b5563; }}
    .mono {{ font-family: monospace; font-size: 13px; white-space: pre-wrap; background: #f3f4f6; padding: 12px; border-radius: 8px; }}
  </style>
</head>
<body>
  <div class=\"container\">
    <h1>Delta Hedging Dashboard</h1>
    <p class=\"note\">This dashboard brings together the project outputs for weekly and daily rebalancing, including summary statistics, confidence intervals, standard deviation paths, and terminal-cost distributions.</p>

    <div class=\"grid\">
      <div class=\"card\"><h2>Weekly mean X(T)</h2><p>{float(weekly_row['mean_X_T']):,.2f}</p></div>
      <div class=\"card\"><h2>Daily mean X(T)</h2><p>{float(daily_row['mean_X_T']):,.2f}</p></div>
      <div class=\"card\"><h2>Weekly ITM prob.</h2><p>{float(weekly_row['itm_probability']):.4f}</p></div>
      <div class=\"card\"><h2>Daily ITM prob.</h2><p>{float(daily_row['itm_probability']):.4f}</p></div>
    </div>

    <h2>Comparison table</h2>
    <table>
      <thead>
        <tr>
          <th>Schedule</th><th>N paths</th><th>Mean X(T)</th><th>Std X(T)</th><th>Mean CI</th><th>ITM prob.</th><th>Prob CI</th><th>Covers BSM</th><th>Target met</th>
        </tr>
      </thead>
      <tbody>
        {table_rows_html}
      </tbody>
    </table>

    <h2>Charts</h2>
    <div class=\"chart-grid\">
      <div class=\"card\">{_img_tag(figs['overlay_std'], 'Weekly vs Daily std of X(t)')}</div>
      <div class=\"card\">{_img_tag(figs['mean_comp'], 'Mean X(T) comparison')}</div>
      <div class=\"card\">{_img_tag(figs['std_comp'], 'Std X(T) comparison')}</div>
      <div class=\"card\">{_img_tag(figs['weekly_hist'], 'Weekly terminal X(T) histogram')}</div>
      <div class=\"card\">{_img_tag(figs['daily_hist'], 'Daily terminal X(T) histogram')}</div>
      <div class=\"card\">{_img_tag(figs['weekly_std'], 'Weekly std of X(t)')}</div>
      <div class=\"card\">{_img_tag(figs['daily_std'], 'Daily std of X(t)')}</div>
    </div>

    <h2>Payload preview</h2>
    <div class=\"mono\">{payload_json}</div>
  </div>
</body>
</html>
"""



def generate_dashboard(results_dir: Path, output_html: Path) -> Path:
    payload = load_dashboard_payload(results_dir)
    html_text = build_dashboard_html(payload)
    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_html.write_text(html_text, encoding="utf-8")
    return output_html
