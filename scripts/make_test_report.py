#!/usr/bin/env python3
"""Run ngspice regression decks and build a self-contained HTML report."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import math
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


COLORS = [
    "#166534",
    "#1d4ed8",
    "#b45309",
    "#be123c",
    "#6d28d9",
    "#0f766e",
    "#334155",
]


@dataclass
class Measurement:
    name: str
    value: str
    at: str | None


@dataclass
class TestResult:
    name: str
    deck_path: Path
    report_deck_path: Path
    log_path: Path
    data_path: Path
    returncode: int
    passed: bool
    measurements: list[Measurement]
    signals: list[str]
    rows: list[list[float]]
    netlist: str
    log: str


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def detect_signals(netlist: str) -> list[str]:
    signals: list[str] = []
    seen: set[str] = set()
    title_skipped = False

    def add(node: str) -> None:
        node = node.strip()
        if not node or node == "0" or node.startswith("$"):
            return
        if node.upper().startswith("NG_"):
            return
        if node not in seen:
            seen.add(node)
            signals.append(node)

    for raw_line in netlist.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if not title_skipped:
            title_skipped = True
            continue
        if line.startswith("*") or line.startswith("."):
            continue
        tokens = line.split()
        if not tokens:
            continue
        kind = tokens[0][0].lower()
        if kind in {"v", "r", "c", "l"} and len(tokens) >= 3:
            add(tokens[1])
            add(tokens[2])
        elif kind == "x" and len(tokens) >= 3:
            pins: list[str] = []
            for token in tokens[1:]:
                if token.lower().startswith("params:"):
                    break
                pins.append(token)
            if pins:
                pins = pins[:-1]
            for pin in pins:
                add(pin)

    return signals


def make_report_deck(netlist: str, data_path: Path, signals: list[str]) -> str:
    vectors = " ".join(f"v({signal})" for signal in signals)
    wrdata_lines = [
        "set wr_singlescale",
        "set wr_vecnames",
        f"wrdata {data_path.as_posix()} {vectors}",
    ]

    out: list[str] = []
    inserted = False
    for line in netlist.splitlines():
        out.append(line)
        if not inserted and line.strip().lower() == "run":
            out.extend(wrdata_lines)
            inserted = True

    if not inserted:
        raise ValueError("test deck has no control 'run' command to instrument")

    return "\n".join(out) + "\n"


def parse_measurements(log: str) -> list[Measurement]:
    measurements: list[Measurement] = []
    pattern = re.compile(
        r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?)(?:\s+at=\s*([-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?))?",
    )
    for line in log.splitlines():
        match = pattern.match(line)
        if match:
            measurements.append(
                Measurement(match.group(1), match.group(2), match.group(3))
            )
    return measurements


def parse_wrdata(path: Path) -> tuple[list[str], list[list[float]]]:
    if not path.exists():
        return [], []

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines:
        return [], []

    headers = lines[0].split()
    rows: list[list[float]] = []
    width = len(headers)
    for line in lines[1:]:
        parts = line.split()
        if len(parts) != width:
            continue
        try:
            rows.append([float(part) for part in parts])
        except ValueError:
            continue

    return headers, rows


def run_test(root: Path, deck_path: Path, report_dir: Path, ngspice: str) -> TestResult:
    name = deck_path.stem
    data_dir = report_dir / "data"
    deck_dir = report_dir / "decks"
    log_dir = report_dir / "logs"
    for directory in (data_dir, deck_dir, log_dir):
        directory.mkdir(parents=True, exist_ok=True)

    data_path = data_dir / f"{name}.dat"
    report_deck_path = deck_dir / f"{name}.cir"
    log_path = log_dir / f"{name}.log"

    netlist = deck_path.read_text(encoding="utf-8", errors="replace")
    signals = detect_signals(netlist)
    if not signals:
        raise ValueError(f"{deck_path} has no detected node voltages to plot")

    report_deck = make_report_deck(netlist, data_path.relative_to(root), signals)
    report_deck_path.write_text(report_deck, encoding="utf-8")

    proc = subprocess.run(
        [ngspice, "-b", str(report_deck_path.relative_to(root))],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log_path.write_text(proc.stdout, encoding="utf-8")

    headers, rows = parse_wrdata(data_path)
    plotted_signals = [header[2:-1] for header in headers[1:] if header.startswith("v(")]
    if plotted_signals:
        signals = plotted_signals

    passed = proc.returncode == 0 and "TEST PASS" in proc.stdout
    return TestResult(
        name=name,
        deck_path=deck_path,
        report_deck_path=report_deck_path,
        log_path=log_path,
        data_path=data_path,
        returncode=proc.returncode,
        passed=passed,
        measurements=parse_measurements(proc.stdout),
        signals=signals,
        rows=rows,
        netlist=netlist,
        log=proc.stdout,
    )


def fmt_float(value: float) -> str:
    if value == 0:
        return "0"
    abs_value = abs(value)
    if 1e-3 <= abs_value < 1e4:
        return f"{value:.5g}"
    return f"{value:.3e}"


def decimate(rows: list[list[float]], max_points: int = 900) -> list[list[float]]:
    if len(rows) <= max_points:
        return rows
    step = max(1, math.ceil(len(rows) / max_points))
    sampled = rows[::step]
    if sampled[-1] is not rows[-1]:
        sampled.append(rows[-1])
    return sampled


def make_svg(result: TestResult) -> str:
    if not result.rows or not result.signals:
        return '<p class="muted">No waveform data was written.</p>'

    rows = decimate(result.rows)
    times = [row[0] for row in rows]
    t_min = min(times)
    t_max = max(times)
    t_span = t_max - t_min if t_max != t_min else 1.0
    time_scale = 1000.0 if t_max < 10.0 else 1.0
    time_unit = "ms" if time_scale == 1000.0 else "s"

    width = 980
    lane_height = 116
    margin_left = 76
    margin_right = 26
    margin_top = 28
    margin_bottom = 36
    chart_width = width - margin_left - margin_right
    height = margin_top + lane_height * len(result.signals) + margin_bottom

    parts = [
        f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(result.name)} waveforms">',
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="8" fill="#ffffff" />',
    ]

    for tick in range(6):
        x = margin_left + chart_width * tick / 5
        label = (t_min + t_span * tick / 5) * time_scale
        parts.append(
            f'<line x1="{x:.2f}" y1="{margin_top}" x2="{x:.2f}" y2="{height - margin_bottom}" stroke="#e2e8f0" />'
        )
        parts.append(
            f'<text x="{x:.2f}" y="{height - 12}" text-anchor="middle" class="axis">{fmt_float(label)}</text>'
        )

    parts.append(
        f'<text x="{width - margin_right}" y="{height - 12}" text-anchor="end" class="axis">time ({time_unit})</text>'
    )

    for index, signal in enumerate(result.signals):
        column = index + 1
        y_top = margin_top + lane_height * index
        y_bottom = y_top + lane_height - 22
        y_mid = (y_top + y_bottom) / 2
        values = [row[column] for row in rows if len(row) > column]
        if not values:
            continue
        v_min = min(values)
        v_max = max(values)
        if v_min == v_max:
            pad = max(abs(v_min) * 0.1, 1.0)
            v_min -= pad
            v_max += pad
        else:
            pad = (v_max - v_min) * 0.08
            v_min -= pad
            v_max += pad
        v_span = v_max - v_min

        parts.append(
            f'<line x1="{margin_left}" y1="{y_bottom:.2f}" x2="{width - margin_right}" y2="{y_bottom:.2f}" stroke="#cbd5e1" />'
        )
        parts.append(
            f'<text x="16" y="{y_top + 18}" class="label">{html.escape(signal)}</text>'
        )
        parts.append(
            f'<text x="16" y="{y_top + 38}" class="axis">{fmt_float(v_max)} V</text>'
        )
        parts.append(
            f'<text x="16" y="{y_bottom:.2f}" class="axis">{fmt_float(v_min)} V</text>'
        )

        if v_min < 0 < v_max:
            zero_y = y_bottom - ((0 - v_min) / v_span) * (y_bottom - y_top)
            parts.append(
                f'<line x1="{margin_left}" y1="{zero_y:.2f}" x2="{width - margin_right}" y2="{zero_y:.2f}" stroke="#e2e8f0" stroke-dasharray="3 3" />'
            )

        points: list[str] = []
        for row in rows:
            if len(row) <= column:
                continue
            x = margin_left + ((row[0] - t_min) / t_span) * chart_width
            y = y_bottom - ((row[column] - v_min) / v_span) * (y_bottom - y_top)
            points.append(f"{x:.2f},{y:.2f}")

        color = COLORS[index % len(COLORS)]
        parts.append(
            f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" />'
        )
        parts.append(
            f'<circle cx="{margin_left}" cy="{y_mid:.2f}" r="0.01" fill="transparent" />'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def measurement_table(result: TestResult) -> str:
    if not result.measurements:
        return '<p class="muted">No measurements found in log.</p>'

    rows = []
    for measurement in result.measurements:
        at = measurement.at or ""
        rows.append(
            "<tr>"
            f"<td>{html.escape(measurement.name)}</td>"
            f"<td>{html.escape(measurement.value)}</td>"
            f"<td>{html.escape(at)}</td>"
            "</tr>"
        )
    return (
        "<table>"
        "<thead><tr><th>Measurement</th><th>Value</th><th>At</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
    )


def html_report(results: list[TestResult], output_path: Path, ngspice: str) -> str:
    passed = sum(1 for result in results if result.passed)
    total = len(results)
    generated_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rel_output = output_path.as_posix()

    cards = []
    for result in results:
        status_class = "pass" if result.passed else "fail"
        status_text = "PASS" if result.passed else "FAIL"
        log_rel = os.path.relpath(result.log_path, output_path.parent)
        data_rel = os.path.relpath(result.data_path, output_path.parent)
        deck_rel = os.path.relpath(result.report_deck_path, output_path.parent)
        cards.append(
            f"""
<section class="test-card">
  <div class="test-head">
    <div>
      <h2>{html.escape(result.name)}</h2>
      <p class="muted">{html.escape(result.deck_path.as_posix())}</p>
    </div>
    <span class="badge {status_class}">{status_text}</span>
  </div>
  <div class="meta">
    <span>return code: {result.returncode}</span>
    <span>samples: {len(result.rows)}</span>
    <span><a href="{html.escape(log_rel)}">log</a></span>
    <span><a href="{html.escape(data_rel)}">data</a></span>
    <span><a href="{html.escape(deck_rel)}">report deck</a></span>
  </div>
  {make_svg(result)}
  <h3>Measurements</h3>
  {measurement_table(result)}
  <details open>
    <summary>Netlist</summary>
    <pre>{html.escape(result.netlist)}</pre>
  </details>
  <details>
    <summary>ngspice log</summary>
    <pre>{html.escape(result.log)}</pre>
  </details>
</section>
"""
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ngfuncs Test Report</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f8fafc;
      --text: #111827;
      --muted: #64748b;
      --line: #dbe3ee;
      --pass: #15803d;
      --fail: #b91c1c;
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 14px/1.45 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 28px 20px 48px;
    }}
    h1, h2, h3, p {{
      margin: 0;
    }}
    h1 {{
      font-size: 28px;
      line-height: 1.15;
    }}
    h2 {{
      font-size: 20px;
    }}
    h3 {{
      margin-top: 18px;
      font-size: 15px;
    }}
    a {{
      color: #1d4ed8;
    }}
    .summary {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: flex-end;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--line);
      margin-bottom: 20px;
    }}
    .summary-box {{
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
    }}
    .test-card {{
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      margin: 18px 0;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
    }}
    .test-head {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: flex-start;
      margin-bottom: 10px;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      border-radius: 999px;
      color: #fff;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.02em;
      padding: 2px 10px;
    }}
    .badge.pass {{
      background: var(--pass);
    }}
    .badge.fail {{
      background: var(--fail);
    }}
    .muted {{
      color: var(--muted);
      margin-top: 4px;
    }}
    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px 14px;
      color: var(--muted);
      margin: 8px 0 14px;
    }}
    .chart {{
      display: block;
      width: 100%;
      height: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
    }}
    .axis {{
      fill: #64748b;
      font-size: 11px;
    }}
    .label {{
      fill: #0f172a;
      font-size: 13px;
      font-weight: 700;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 8px;
      overflow: hidden;
      border-radius: 8px;
    }}
    th, td {{
      text-align: left;
      border-bottom: 1px solid var(--line);
      padding: 8px 10px;
    }}
    th {{
      color: #334155;
      background: #f1f5f9;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    details {{
      margin-top: 16px;
      border-top: 1px solid var(--line);
      padding-top: 12px;
    }}
    summary {{
      cursor: pointer;
      font-weight: 700;
    }}
    pre {{
      overflow: auto;
      max-height: 520px;
      padding: 12px;
      border-radius: 8px;
      background: #0f172a;
      color: #e2e8f0;
      font: 12px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }}
    @media (max-width: 680px) {{
      main {{
        padding: 20px 12px 36px;
      }}
      .summary, .test-head {{
        align-items: flex-start;
        flex-direction: column;
      }}
    }}
  </style>
</head>
<body>
<main>
  <header class="summary">
    <div>
      <h1>ngfuncs Test Report</h1>
      <p class="muted">Generated {html.escape(generated_at)} with {html.escape(ngspice)}</p>
      <p class="muted">Report: {html.escape(rel_output)}</p>
    </div>
    <div class="summary-box">
      <span class="badge {'pass' if passed == total else 'fail'}">{passed}/{total} passed</span>
    </div>
  </header>
  {''.join(cards)}
</main>
</body>
</html>
"""


def main(argv: list[str]) -> int:
    root = project_root()
    parser = argparse.ArgumentParser()
    parser.add_argument("--cm", default=os.environ.get("NGFUNCS_CM", "build/ngfuncs.cm"))
    parser.add_argument("--output", default="tests/output/report/index.html")
    parser.add_argument("--ngspice", default=os.environ.get("NGSPICE", "ngspice"))
    args = parser.parse_args(argv)

    cm_path = root / args.cm
    if not cm_path.exists():
        print(f"Missing {args.cm}", file=sys.stderr)
        print("Run: make build-cm", file=sys.stderr)
        return 2

    ngspice_path = shutil.which(args.ngspice)
    if ngspice_path is None:
        print(f"Missing ngspice executable: {args.ngspice}", file=sys.stderr)
        return 2

    output_path = root / args.output
    report_dir = output_path.parent
    report_dir.mkdir(parents=True, exist_ok=True)

    decks = sorted((root / "tests").glob("test_*.cir"))
    if not decks:
        print("No tests/test_*.cir decks found", file=sys.stderr)
        return 2

    results: list[TestResult] = []
    status = 0
    for deck in decks:
        print(f"running {deck.relative_to(root)}")
        try:
            result = run_test(root, deck, report_dir, ngspice_path)
        except Exception as exc:
            print(f"fail {deck.relative_to(root)}; {exc}", file=sys.stderr)
            status = 1
            continue
        results.append(result)
        if result.passed:
            print(f"pass {deck.relative_to(root)}")
        else:
            print(f"fail {deck.relative_to(root)}; see {result.log_path.relative_to(root)}", file=sys.stderr)
            status = 1

    output_path.write_text(html_report(results, output_path.relative_to(root), ngspice_path), encoding="utf-8")
    print(f"report {output_path.relative_to(root)}")
    return status


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
