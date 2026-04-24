"""Streamlit dashboard for running and visualizing Spectra privacy audits."""

import glob
import json
import os
import re
import subprocess
import sys
from datetime import datetime

import streamlit as st


# Streamlit page setup for a full-width dashboard experience.
st.set_page_config(page_title="Spectra", layout="wide", page_icon="🔒")


# Centralized constants for model selection and project paths.
MODEL_NAME = "gemma-3-12b-it"
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")


def score_color(score: float) -> str:
	"""Return color hex for low/medium/high risk bands."""

	if score <= 30:
		return "#16a34a"
	if score <= 70:
		return "#ca8a04"
	return "#dc2626"


def score_band(score: float) -> str:
	"""Return a human-readable risk label."""

	if score <= 30:
		return "LOW"
	if score <= 70:
		return "MEDIUM"
	return "HIGH"


def parse_scores(terminal_output: str) -> dict[str, float]:
	"""Parse module scores from terminal output using regex and compute combined score."""

	patterns = {
		"pii": r"PII risk score:\s*(\d+(?:\.\d+)?)/100",
		"regurgitation": r"Regurgitation risk score:\s*(\d+(?:\.\d+)?)/100",
		"membership": r"Membership inference risk score:\s*(\d+(?:\.\d+)?)/100",
	}

	scores: dict[str, float] = {}
	for key, pattern in patterns.items():
		match = re.search(pattern, terminal_output)
		if match:
			scores[key] = float(match.group(1))

	if len(scores) == 3:
		scores["overall"] = round((scores["pii"] + scores["regurgitation"] + scores["membership"]) / 3, 2)

	return scores


def find_latest_report() -> str | None:
	"""Find the most recently generated HTML report file."""

	report_files = glob.glob(os.path.join(REPORTS_DIR, "*.html"))
	if not report_files:
		return None
	return max(report_files, key=os.path.getmtime)


# Session state keeps results visible across Streamlit reruns.
if "audit_output" not in st.session_state:
	st.session_state.audit_output = ""
if "audit_failed" not in st.session_state:
	st.session_state.audit_failed = False
if "scores" not in st.session_state:
	st.session_state.scores = {}
if "latest_report" not in st.session_state:
	st.session_state.latest_report = None


# Lightweight styling to keep the dashboard polished and readable.
st.markdown(
	"""
	<style>
		.block-container {
			padding-top: 1.4rem;
			padding-bottom: 1.2rem;
		}
		.spectra-header {
			padding: 1rem 1.1rem;
			border: 1px solid rgba(255, 255, 255, 0.14);
			border-radius: 14px;
			background: linear-gradient(135deg, rgba(2, 6, 23, 0.98), rgba(30, 41, 59, 0.95));
			margin-bottom: 1rem;
		}
		.spectra-title {
			font-size: 1.85rem;
			font-weight: 800;
			letter-spacing: 0.04em;
			margin: 0;
		}
		.spectra-tagline {
			margin: 0.25rem 0 0 0;
			color: #94a3b8;
			font-size: 0.98rem;
		}
		.risk-label {
			font-size: 0.82rem;
			font-weight: 700;
			padding: 0.25rem 0.55rem;
			border-radius: 999px;
			display: inline-block;
			margin-bottom: 0.45rem;
			color: #0b1020;
		}
		.risk-track {
			height: 0.55rem;
			border-radius: 999px;
			background: rgba(148, 163, 184, 0.24);
			overflow: hidden;
		}
		.risk-fill {
			height: 100%;
			border-radius: inherit;
		}
	</style>
	""",
	unsafe_allow_html=True,
)


# Main dashboard header.
st.markdown(
	"""
	<div class="spectra-header">
		<p class="spectra-title">SPECTRA</p>
		<p class="spectra-tagline">LLM Privacy Auditing Tool</p>
	</div>
	""",
	unsafe_allow_html=True,
)


# Sidebar control panel for model metadata and audit execution.
with st.sidebar:
	st.markdown("## 🔒 SPECTRA")
	st.caption("Privacy stress-testing control panel")
	st.markdown(f"**Model under test:** `{MODEL_NAME}`")
	st.markdown(f"**Session time:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")
	run_audit = st.button("Run Audit", use_container_width=True, type="primary")


# Execute the full audit pipeline through main.py and capture terminal output.
if run_audit:
	with st.spinner("Running Spectra Audit..."):
		result = subprocess.run(
			[sys.executable, "main.py"],
			cwd=PROJECT_ROOT,
			capture_output=True,
			text=True,
		)

		combined_output = (result.stdout or "")
		if result.stderr:
			combined_output += "\n\n[stderr]\n" + result.stderr

		st.session_state.audit_output = combined_output
		st.session_state.audit_failed = result.returncode != 0
		st.session_state.scores = parse_scores(combined_output)
		st.session_state.latest_report = find_latest_report()


# Show audit status and raw output in an expandable terminal viewer.
if st.session_state.audit_output:
	if st.session_state.audit_failed:
		st.error("Audit finished with errors. Review terminal output below.")
	else:
		st.success("Audit completed successfully.")

	with st.expander("Terminal Output", expanded=False):
		st.code(st.session_state.audit_output)


# Always try to resolve the latest report path, even on page refresh.
if not st.session_state.latest_report:
	st.session_state.latest_report = find_latest_report()


# Render parsed risk metrics and color-coded progress bars.
scores = st.session_state.scores
if scores:
	st.markdown("### Audit Risk Scores")
	metric_items = [
		("PII Risk Score", scores.get("pii", 0.0)),
		("Regurgitation Risk Score", scores.get("regurgitation", 0.0)),
		("Membership Inference Risk Score", scores.get("membership", 0.0)),
		("Overall Combined Score", scores.get("overall", 0.0)),
	]

	cols = st.columns(4)
	for col, (label, value) in zip(cols, metric_items):
		value = float(value)
		color = score_color(value)
		band = score_band(value)
		with col:
			st.metric(label=label, value=f"{value:.2f}/100")
			st.markdown(
				f"""
				<div class="risk-label" style="background:{color};">{band} RISK</div>
				<div class="risk-track">
					<div class="risk-fill" style="width:{value}%; background:{color};"></div>
				</div>
				""",
				unsafe_allow_html=True,
			)

	st.markdown("### Parsed Score Payload")
	st.code(json.dumps(scores, indent=2))


# Display generated report location and user guidance for viewing it.
st.markdown("### Latest HTML Report")
if st.session_state.latest_report:
	report_path = st.session_state.latest_report
	st.code(report_path)
	st.info("Open this file in your browser to view the full formatted audit report.")
else:
	st.warning("No report found in reports/. Run an audit to generate one.")
