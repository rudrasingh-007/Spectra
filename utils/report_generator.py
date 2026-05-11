"""HTML report generation helpers for Spectra audit results."""

import json
import os
from datetime import datetime


def cleanup_old_reports(reports_dir, keep=3):
	"""Keep only the most recent HTML reports and delete older ones silently."""

	try:
		report_files = [
			os.path.join(reports_dir, file_name)
			for file_name in os.listdir(reports_dir)
			if file_name.lower().endswith(".html")
		]
		report_files.sort(key=os.path.getmtime)

		if len(report_files) <= keep:
			return

		for old_file in report_files[:-keep]:
			try:
				os.remove(old_file)
			except OSError:
				pass
	except OSError:
		pass


def generate_report(
	pii_score,
	pii_findings,
	regurgitation_score,
	regurgitation_cases,
	membership_score,
	membership_data,
	model_name,
):
	"""Create a detailed standalone HTML audit report and return its saved path."""

	def clamp_score(value):
		return max(0.0, min(100.0, float(value)))

	def score_band(score):
		if score <= 30:
			return "low"
		if score <= 70:
			return "medium"
		return "high"

	def score_color(score):
		band = score_band(score)
		if band == "low":
			return "#22c55e"
		if band == "medium":
			return "#f59e0b"
		return "#ef4444"

	def escape_text(value):
		return json.dumps(str(value))[1:-1]

	# Normalize primary score values and compute overall score.
	pii_score = clamp_score(pii_score)
	regurgitation_score = clamp_score(regurgitation_score)
	membership_score = clamp_score(membership_score)
	overall_score = round((pii_score + regurgitation_score + membership_score) / 3, 2)

	# Resolve report metadata and ensure output folder exists.
	created_at = datetime.now()
	created_at_text = created_at.strftime("%Y-%m-%d %H:%M:%S")
	timestamp = created_at.strftime("%Y%m%d_%H%M%S")
	base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	reports_dir = os.path.join(base_dir, "reports")
	os.makedirs(reports_dir, exist_ok=True)

	# Build top module cards with color-coded progress bars.
	metric_cards = [
		{"label": "PII Risk", "score": pii_score},
		{"label": "Regurgitation Risk", "score": regurgitation_score},
		{"label": "Membership Inference Risk", "score": membership_score},
		{"label": "Overall", "score": overall_score},
	]
	metric_cards_html = []
	for card in metric_cards:
		score = clamp_score(card["score"])
		metric_cards_html.append(
			f"""
			<div class="metric-card">
				<div class="metric-head">
					<span>{escape_text(card['label'])}</span>
					<span class="metric-score" style="color:{score_color(score)}">{score:.2f}/100</span>
				</div>
				<div class="progress-track">
					<div class="progress-fill {score_band(score)}" style="width:{score}%;"></div>
				</div>
			</div>
			"""
		)

	# Build pure HTML/CSS bar chart for module score comparison.
	chart_bars = [
		("PII", pii_score),
		("Regurgitation", regurgitation_score),
		("Membership", membership_score),
	]
	chart_html = []
	for label, score in chart_bars:
		score = clamp_score(score)
		chart_html.append(
			f"""
			<div class="chart-item">
				<div class="chart-bar-wrap">
					<div class="chart-bar {score_band(score)}" style="height:{score}%;"></div>
				</div>
				<div class="chart-value">{score:.1f}</div>
				<div class="chart-label">{escape_text(label)}</div>
			</div>
			"""
		)

	# Module 1 breakdown: prompt-by-prompt detected PII entities.
	pii_sections = []
	for index, finding in enumerate(pii_findings or [], start=1):
		prompt_text = escape_text(finding.get("prompt", ""))
		entities = finding.get("entities", []) or []
		if entities:
			entity_rows = []
			for entity in entities:
				entity_type = escape_text(entity.get("entity_type", "UNKNOWN"))
				entity_value = escape_text(entity.get("text", ""))
				entity_rows.append(
					f"<li><span class='entity-type'>{entity_type}</span><span class='entity-value'>{entity_value}</span></li>"
				)
			entity_html = f"<ul class='entity-list'>{''.join(entity_rows)}</ul>"
		else:
			entity_html = "<p class='muted'>No PII detected</p>"

		pii_sections.append(
			f"""
			<div class="detail-card">
				<h4>Prompt {index}</h4>
				<p class="prompt-text">{prompt_text}</p>
				{entity_html}
			</div>
			"""
		)

	if not pii_sections:
		pii_sections.append("<p class='muted'>No PII findings were provided.</p>")

	# Module 2 breakdown: exact/semantic similarity and risk flag per case.
	reg_rows = []
	for index, case in enumerate(regurgitation_cases or [], start=1):
		prompt_text = escape_text(case.get("prompt", ""))
		exact_score = clamp_score(case.get("exact_score", 0))
		semantic_score = clamp_score(case.get("semantic_score", 0))
		is_risky = "YES" if case.get("is_risky", False) else "NO"
		flag_class = "flag-yes" if is_risky == "YES" else "flag-no"
		reg_rows.append(
			f"""
			<tr>
				<td>{index}</td>
				<td>{prompt_text}</td>
				<td>{exact_score:.2f}</td>
				<td>{semantic_score:.2f}</td>
				<td><span class="risk-flag {flag_class}">{is_risky}</span></td>
			</tr>
			"""
		)

	if not reg_rows:
		reg_rows.append(
			"<tr><td colspan='5' class='muted'>No regurgitation case data was provided.</td></tr>"
		)

	# Module 3 breakdown: target/random confidence tables plus summary metrics.
	membership_data = membership_data or {}
	target_scores = membership_data.get("target_scores", []) or []
	random_scores = membership_data.get("random_scores", []) or []
	target_avg = clamp_score(membership_data.get("target_avg", 0))
	random_avg = clamp_score(membership_data.get("random_avg", 0))
	gap = float(membership_data.get("gap", 0))
	risk_level = escape_text(membership_data.get("risk_level", "UNKNOWN"))

	target_rows = []
	for idx, score in enumerate(target_scores, start=1):
		target_rows.append(
			f"<tr><td>Target #{idx}</td><td>{clamp_score(score):.2f}</td></tr>"
		)
	if not target_rows:
		target_rows.append("<tr><td colspan='2' class='muted'>No target confidence data provided.</td></tr>")

	random_rows = []
	for idx, score in enumerate(random_scores, start=1):
		random_rows.append(
			f"<tr><td>Random #{idx}</td><td>{clamp_score(score):.2f}</td></tr>"
		)
	if not random_rows:
		random_rows.append("<tr><td colspan='2' class='muted'>No random confidence data provided.</td></tr>")

	html = f"""<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Spectra Detailed Audit Report</title>
	<style>
		:root {{
			--bg: #0b1020;
			--panel: #121a2f;
			--panel-2: #17213a;
			--text: #eef2ff;
			--muted: #9aa4bf;
			--border: rgba(255, 255, 255, 0.09);
			--shadow: 0 16px 48px rgba(0, 0, 0, 0.35);
			--low: #22c55e;
			--medium: #f59e0b;
			--high: #ef4444;
		}}

		* {{ box-sizing: border-box; }}

		body {{
			margin: 0;
			font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
			background:
				radial-gradient(circle at top left, rgba(91, 140, 255, 0.2), transparent 30%),
				radial-gradient(circle at top right, rgba(34, 197, 94, 0.12), transparent 25%),
				linear-gradient(180deg, #070b16 0%, #0b1020 100%);
			color: var(--text);
			min-height: 100vh;
			padding: 28px 18px 44px;
		}}

		.container {{
			max-width: 1160px;
			margin: 0 auto;
		}}

		.header {{
			background: linear-gradient(145deg, rgba(18, 26, 47, 0.96), rgba(23, 33, 58, 0.92));
			border: 1px solid var(--border);
			border-radius: 22px;
			padding: 26px;
			box-shadow: var(--shadow);
			margin-bottom: 18px;
		}}

		h1 {{
			font-size: clamp(2rem, 4vw, 3rem);
			line-height: 1.05;
			margin: 0;
		}}

		.subtitle {{
			color: var(--muted);
			margin: 6px 0 16px;
		}}

		.badge {{
			display: inline-block;
			padding: 6px 10px;
			border-radius: 999px;
			font-size: 0.75rem;
			font-weight: 800;
			letter-spacing: 0.08em;
			text-transform: uppercase;
			background: rgba(34, 197, 94, 0.2);
			border: 1px solid rgba(34, 197, 94, 0.35);
			color: #86efac;
		}}

		.meta-grid {{
			display: grid;
			grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
			gap: 12px;
			margin-top: 16px;
		}}

		.meta-card {{
			background: rgba(12, 17, 31, 0.78);
			border: 1px solid var(--border);
			border-radius: 14px;
			padding: 12px;
		}}

		.meta-label {{
			font-size: 0.76rem;
			text-transform: uppercase;
			letter-spacing: 0.08em;
			color: var(--muted);
		}}

		.meta-value {{
			margin-top: 6px;
			font-weight: 600;
		}}

		.section {{
			background: linear-gradient(180deg, rgba(18, 26, 47, 0.95), rgba(14, 20, 35, 0.95));
			border: 1px solid var(--border);
			border-radius: 18px;
			padding: 18px;
			box-shadow: var(--shadow);
			margin-bottom: 16px;
		}}

		.section-title {{
			margin: 0 0 12px;
			font-size: 1.12rem;
		}}

		.metrics-grid {{
			display: grid;
			grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
			gap: 10px;
		}}

		.metric-card {{
			background: rgba(12, 17, 31, 0.85);
			border: 1px solid var(--border);
			border-radius: 14px;
			padding: 12px;
		}}

		.metric-head {{
			display: flex;
			justify-content: space-between;
			gap: 8px;
			align-items: center;
			margin-bottom: 10px;
			font-weight: 600;
		}}

		.metric-score {{
			font-variant-numeric: tabular-nums;
		}}

		.progress-track {{
			height: 12px;
			background: rgba(255, 255, 255, 0.08);
			border-radius: 999px;
			overflow: hidden;
		}}

		.progress-fill {{
			height: 100%;
			border-radius: inherit;
		}}

		.progress-fill.low {{ background: linear-gradient(90deg, #16a34a, #22c55e); }}
		.progress-fill.medium {{ background: linear-gradient(90deg, #d97706, #f59e0b); }}
		.progress-fill.high {{ background: linear-gradient(90deg, #dc2626, #ef4444); }}

		.chart-grid {{
			display: grid;
			grid-template-columns: repeat(3, minmax(90px, 1fr));
			gap: 18px;
			align-items: end;
			height: 220px;
			margin-top: 8px;
		}}

		.chart-item {{
			display: flex;
			flex-direction: column;
			align-items: center;
			gap: 8px;
		}}

		.chart-bar-wrap {{
			height: 170px;
			width: 54px;
			background: rgba(255, 255, 255, 0.07);
			border-radius: 10px;
			overflow: hidden;
			display: flex;
			align-items: flex-end;
		}}

		.chart-bar {{
			width: 100%;
		}}

		.chart-bar.low {{ background: linear-gradient(180deg, #22c55e, #15803d); }}
		.chart-bar.medium {{ background: linear-gradient(180deg, #f59e0b, #b45309); }}
		.chart-bar.high {{ background: linear-gradient(180deg, #ef4444, #b91c1c); }}

		.chart-value {{
			font-size: 0.88rem;
			font-weight: 700;
		}}

		.chart-label {{
			font-size: 0.82rem;
			color: var(--muted);
		}}

		.detail-card {{
			background: rgba(12, 17, 31, 0.8);
			border: 1px solid var(--border);
			border-radius: 14px;
			padding: 12px;
			margin-bottom: 10px;
		}}

		.detail-card h4 {{
			margin: 0 0 6px;
			font-size: 0.98rem;
		}}

		.prompt-text {{
			margin: 0 0 8px;
			color: #d5def2;
			line-height: 1.5;
		}}

		.entity-list {{
			margin: 0;
			padding-left: 18px;
		}}

		.entity-list li {{
			margin-bottom: 6px;
		}}

		.entity-type {{
			display: inline-block;
			min-width: 120px;
			font-weight: 700;
			color: #93c5fd;
		}}

		.entity-value {{
			color: #f8fafc;
			word-break: break-word;
		}}

		table {{
			width: 100%;
			border-collapse: collapse;
			font-size: 0.92rem;
		}}

		th, td {{
			padding: 9px;
			border-bottom: 1px solid var(--border);
			vertical-align: top;
		}}

		th {{
			text-align: left;
			font-size: 0.8rem;
			text-transform: uppercase;
			letter-spacing: 0.07em;
			color: var(--muted);
		}}

		.risk-flag {{
			display: inline-flex;
			padding: 4px 8px;
			border-radius: 999px;
			font-size: 0.75rem;
			font-weight: 800;
			letter-spacing: 0.05em;
		}}

		.flag-yes {{
			background: rgba(239, 68, 68, 0.18);
			border: 1px solid rgba(239, 68, 68, 0.34);
			color: #fca5a5;
		}}

		.flag-no {{
			background: rgba(34, 197, 94, 0.18);
			border: 1px solid rgba(34, 197, 94, 0.34);
			color: #86efac;
		}}

		.two-col {{
			display: grid;
			grid-template-columns: 1fr 1fr;
			gap: 12px;
		}}

		.summary-grid {{
			display: grid;
			grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
			gap: 10px;
			margin-top: 12px;
		}}

		.summary-card {{
			background: rgba(12, 17, 31, 0.8);
			border: 1px solid var(--border);
			border-radius: 12px;
			padding: 10px;
		}}

		.summary-label {{
			font-size: 0.76rem;
			color: var(--muted);
			text-transform: uppercase;
			letter-spacing: 0.07em;
		}}

		.summary-value {{
			margin-top: 4px;
			font-weight: 700;
		}}

		.muted {{
			color: var(--muted);
		}}

		@media (max-width: 900px) {{
			.two-col {{
				grid-template-columns: 1fr;
			}}
			.chart-grid {{
				height: auto;
				grid-template-columns: 1fr;
				gap: 10px;
			}}
			.chart-item {{
				align-items: stretch;
			}}
			.chart-bar-wrap {{
				height: 14px;
				width: 100%;
				align-items: center;
			}}
			.chart-bar {{
				height: 100% !important;
			}}
		}}
	</style>
</head>
<body>
	<div class="container">
		<section class="header">
			<h1>SPECTRA</h1>
			<p class="subtitle">// Privacy Intelligence Console</p>
			<span class="badge">SYSTEM OPERATIONAL</span>
			<div class="meta-grid">
				<div class="meta-card">
					<div class="meta-label">Model Tested</div>
					<div class="meta-value">{escape_text(model_name)}</div>
				</div>
				<div class="meta-card">
					<div class="meta-label">Audit Date & Time</div>
					<div class="meta-value">{created_at_text}</div>
				</div>
				<div class="meta-card">
					<div class="meta-label">Overall Risk Score</div>
					<div class="meta-value">{overall_score:.2f}/100</div>
				</div>
			</div>
		</section>

		<section class="section">
			<h2 class="section-title">Score Overview</h2>
			<div class="metrics-grid">
				{''.join(metric_cards_html)}
			</div>
		</section>

		<section class="section">
			<h2 class="section-title">Module Score Comparison</h2>
			<div class="chart-grid">
				{''.join(chart_html)}
			</div>
		</section>

		<section class="section">
			<h2 class="section-title">Module 1: PII Detection Breakdown</h2>
			{''.join(pii_sections)}
		</section>

		<section class="section">
			<h2 class="section-title">Module 2: Regurgitation Breakdown</h2>
			<table>
				<thead>
					<tr>
						<th>#</th>
						<th>Prompt</th>
						<th>Exact Similarity</th>
						<th>Semantic Similarity</th>
						<th>Risk Flag</th>
					</tr>
				</thead>
				<tbody>
					{''.join(reg_rows)}
				</tbody>
			</table>
		</section>

		<section class="section">
			<h2 class="section-title">Module 3: Membership Inference Breakdown</h2>
			<div class="two-col">
				<div>
					<h3 class="section-title">Target Text Confidence</h3>
					<table>
						<thead><tr><th>Text</th><th>Score</th></tr></thead>
						<tbody>{''.join(target_rows)}</tbody>
					</table>
				</div>
				<div>
					<h3 class="section-title">Random Text Confidence</h3>
					<table>
						<thead><tr><th>Text</th><th>Score</th></tr></thead>
						<tbody>{''.join(random_rows)}</tbody>
					</table>
				</div>
			</div>
			<div class="summary-grid">
				<div class="summary-card">
					<div class="summary-label">Target Average</div>
					<div class="summary-value">{target_avg:.2f}</div>
				</div>
				<div class="summary-card">
					<div class="summary-label">Random Average</div>
					<div class="summary-value">{random_avg:.2f}</div>
				</div>
				<div class="summary-card">
					<div class="summary-label">Gap</div>
					<div class="summary-value">{gap:.2f}</div>
				</div>
				<div class="summary-card">
					<div class="summary-label">Risk Level</div>
					<div class="summary-value">{risk_level}</div>
				</div>
			</div>
		</section>
	</div>
</body>
</html>"""

	# Persist the detailed HTML report to the reports folder using a timestamped filename.
	cleanup_old_reports(reports_dir)
	filename = f"spectra_audit_report_{timestamp}.html"
	filepath = os.path.join(reports_dir, filename)
	with open(filepath, "w", encoding="utf-8") as report_file:
		report_file.write(html)

	return filepath
