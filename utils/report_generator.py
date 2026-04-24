"""HTML report generation helpers for Spectra audit results."""

import json
import os
from datetime import datetime


def generate_report(pii_score, regurgitation_score, membership_score, model_name):
	"""Create and save a professional HTML audit report and return its file path."""

	# Combine the three module scores into one overall risk score.
	combined_score = round((pii_score + regurgitation_score + membership_score) / 3, 2)
	created_at = datetime.now()
	created_at_text = created_at.strftime("%Y-%m-%d %H:%M:%S")
	timestamp = created_at.strftime("%Y%m%d_%H%M%S")

	# Choose the folder where the report should be written and make sure it exists.
	base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	reports_dir = os.path.join(base_dir, "reports")
	os.makedirs(reports_dir, exist_ok=True)

	# Score cards drive the progress bars and color thresholds in the report.
	score_cards = [
		{"label": "PII Leakage Risk", "score": pii_score},
		{"label": "Regurgitation Risk", "score": regurgitation_score},
		{"label": "Membership Inference Risk", "score": membership_score},
	]

	def score_band(score):
		if score <= 30:
			return "low"
		if score <= 70:
			return "medium"
		return "high"

	def score_color(score):
		band = score_band(score)
		if band == "low":
			return "#2ecc71"
		if band == "medium":
			return "#f1c40f"
		return "#e74c3c"

	def escape_text(value):
		return json.dumps(str(value))[1:-1]

	# Build the visual score bars and summary cards.
	bar_sections = []
	for card in score_cards:
		score = max(0, min(100, float(card["score"])))
		bar_sections.append(
			f"""
			<div class="score-card">
				<div class="score-header">
					<span>{escape_text(card['label'])}</span>
					<span class="score-value" style="color: {score_color(score)};">{score:.0f}/100</span>
				</div>
				<div class="progress-track">
					<div class="progress-fill {score_band(score)}" style="width: {score}%;"></div>
				</div>
			</div>
			"""
		)

	overall_band = score_band(combined_score)
	overall_color = score_color(combined_score)

	html = f"""<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Spectra Audit Report</title>
	<style>
		:root {{
			--bg: #0b1020;
			--panel: #121a2f;
			--panel-2: #17213a;
			--text: #eef2ff;
			--muted: #9aa4bf;
			--border: rgba(255, 255, 255, 0.08);
			--shadow: 0 18px 50px rgba(0, 0, 0, 0.35);
			--low: #2ecc71;
			--medium: #f1c40f;
			--high: #e74c3c;
		}}

		* {{ box-sizing: border-box; }}

		body {{
			margin: 0;
			font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
			background:
				radial-gradient(circle at top left, rgba(91, 140, 255, 0.22), transparent 28%),
				radial-gradient(circle at top right, rgba(46, 204, 113, 0.12), transparent 24%),
				linear-gradient(180deg, #070b16 0%, #0b1020 100%);
			color: var(--text);
			min-height: 100vh;
			padding: 32px 18px 48px;
		}}

		.container {{
			max-width: 1080px;
			margin: 0 auto;
		}}

		.hero {{
			background: linear-gradient(145deg, rgba(18, 26, 47, 0.96), rgba(23, 33, 58, 0.92));
			border: 1px solid var(--border);
			border-radius: 24px;
			padding: 30px;
			box-shadow: var(--shadow);
			margin-bottom: 22px;
		}}

		.eyebrow {{
			text-transform: uppercase;
			letter-spacing: 0.18em;
			color: var(--muted);
			font-size: 0.78rem;
			margin-bottom: 12px;
		}}

		h1 {{
			margin: 0 0 10px;
			font-size: clamp(2rem, 4vw, 3.25rem);
			line-height: 1.05;
		}}

		.subtitle {{
			margin: 0;
			color: var(--muted);
			font-size: 1rem;
			max-width: 72ch;
		}}

		.meta-grid {{
			display: grid;
			grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
			gap: 16px;
			margin-bottom: 22px;
		}}

		.meta-card, .score-card, .overall-card {{
			background: linear-gradient(180deg, rgba(18, 26, 47, 0.96), rgba(14, 20, 35, 0.96));
			border: 1px solid var(--border);
			border-radius: 20px;
			box-shadow: var(--shadow);
		}}

		.meta-card {{ padding: 18px 20px; }}

		.meta-label {{
			color: var(--muted);
			font-size: 0.82rem;
			text-transform: uppercase;
			letter-spacing: 0.08em;
			margin-bottom: 6px;
		}}

		.meta-value {{
			font-size: 1.05rem;
			font-weight: 600;
			word-break: break-word;
		}}

		.section-title {{
			margin: 0 0 14px;
			font-size: 1.15rem;
		}}

		.scores {{
			display: grid;
			gap: 14px;
		}}

		.score-card {{ padding: 18px 20px 20px; }}

		.score-header {{
			display: flex;
			justify-content: space-between;
			gap: 12px;
			align-items: center;
			margin-bottom: 12px;
			font-weight: 600;
		}}

		.score-value {{ font-variant-numeric: tabular-nums; }}

		.progress-track {{
			width: 100%;
			height: 14px;
			background: rgba(255, 255, 255, 0.07);
			border-radius: 999px;
			overflow: hidden;
		}}

		.progress-fill {{
			height: 100%;
			border-radius: inherit;
			transition: width 0.4s ease;
		}}

		.progress-fill.low {{ background: linear-gradient(90deg, #1fbf75, #2ecc71); }}
		.progress-fill.medium {{ background: linear-gradient(90deg, #d9b10c, #f1c40f); }}
		.progress-fill.high {{ background: linear-gradient(90deg, #d94a42, #e74c3c); }}

		.overall-card {{
			margin-top: 22px;
			padding: 24px 22px;
			display: grid;
			gap: 12px;
		}}

		.overall-top {{
			display: flex;
			justify-content: space-between;
			gap: 16px;
			align-items: center;
			flex-wrap: wrap;
		}}

		.overall-score {{
			font-size: clamp(2rem, 5vw, 3rem);
			font-weight: 800;
			color: {overall_color};
			font-variant-numeric: tabular-nums;
		}}

		.note {{
			color: var(--muted);
			font-size: 0.95rem;
			line-height: 1.6;
			margin: 0;
		}}

		.tag {{
			display: inline-flex;
			align-items: center;
			padding: 6px 10px;
			border-radius: 999px;
			font-size: 0.8rem;
			font-weight: 700;
			letter-spacing: 0.04em;
			text-transform: uppercase;
			color: #07111f;
			background: {overall_color};
		}}

		@media (max-width: 640px) {{
			body {{ padding: 18px 12px 28px; }}
			.hero, .overall-card {{ padding: 20px 16px; }}
			.score-card {{ padding: 16px; }}
		}}
	</style>
</head>
<body>
	<div class="container">
		<section class="hero">
			<div class="eyebrow">Spectra Privacy Audit Report</div>
			<h1>LLM Risk Assessment</h1>
			<p class="subtitle">This report summarizes leakage, regurgitation, and membership inference risk for the tested model in a single, easy-to-review dashboard.</p>
		</section>

		<section class="meta-grid">
			<div class="meta-card">
				<div class="meta-label">Model Tested</div>
				<div class="meta-value">{escape_text(model_name)}</div>
			</div>
			<div class="meta-card">
				<div class="meta-label">Audit Date & Time</div>
				<div class="meta-value">{created_at_text}</div>
			</div>
			<div class="meta-card">
				<div class="meta-label">Overall Risk</div>
				<div class="meta-value">{combined_score:.2f}/100</div>
			</div>
		</section>

		<section>
			<h2 class="section-title">Module Scores</h2>
			<div class="scores">
				{''.join(bar_sections)}
			</div>
		</section>

		<section class="overall-card">
			<div class="overall-top">
				<div>
					<h2 class="section-title" style="margin-bottom: 6px;">Combined Risk Summary</h2>
					<p class="note">The overall score is the average of the three module scores and is intended to provide a quick executive view of the model's privacy exposure.</p>
				</div>
				<div class="tag">{overall_band} risk</div>
			</div>
			<div class="overall-score">{combined_score:.2f}/100</div>
			<div class="progress-track">
				<div class="progress-fill {overall_band}" style="width: {combined_score}%;"></div>
			</div>
		</section>
	</div>
</body>
</html>"""

	# Persist the HTML report to the reports folder with a timestamped filename.
	filename = f"spectra_audit_report_{timestamp}.html"
	filepath = os.path.join(reports_dir, filename)
	with open(filepath, "w", encoding="utf-8") as report_file:
		report_file.write(html)

	return filepath
