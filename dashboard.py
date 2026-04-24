"""Spectra dashboard: Privacy Intelligence Console."""

import glob
import json
import os
import re
import subprocess
import sys
import threading
import time
from datetime import datetime

import streamlit as st


# Configure Streamlit page metadata and base layout.
st.set_page_config(page_title="Spectra // Privacy Intelligence Console", layout="wide", page_icon="🔒")


# Shared constants for model display and report discovery.
MODEL_NAME = "gemma-3-12b-it"
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")


def get_risk_color(score: float) -> str:
	"""Return risk color based on score bands."""

	if score <= 30:
		return "#00d084"
	if score <= 70:
		return "#facc15"
	return "#ef4444"


def get_risk_label(score: float) -> str:
	"""Return risk label based on score bands."""

	if score <= 30:
		return "LOW"
	if score <= 70:
		return "MEDIUM"
	return "HIGH"


def parse_scores(output_text: str) -> dict[str, float]:
	"""Parse module scores from main.py terminal output using regex patterns."""

	patterns = {
		"pii": r"PII risk score:\s*(\d+(?:\.\d+)?)/100",
		"regurgitation": r"Regurgitation risk score:\s*(\d+(?:\.\d+)?)/100",
		"membership": r"Membership inference risk score:\s*(\d+(?:\.\d+)?)/100",
	}

	scores: dict[str, float] = {}
	for key, pattern in patterns.items():
		match = re.search(pattern, output_text)
		if match:
			scores[key] = float(match.group(1))

	if len(scores) == 3:
		scores["overall"] = round((scores["pii"] + scores["regurgitation"] + scores["membership"]) / 3, 2)

	return scores


def find_latest_report() -> tuple[str | None, datetime | None]:
	"""Return the latest report path and timestamp if any report exists."""

	report_files = glob.glob(os.path.join(REPORTS_DIR, "*.html"))
	if not report_files:
		return None, None

	latest_path = max(report_files, key=os.path.getmtime)
	report_time = datetime.fromtimestamp(os.path.getmtime(latest_path))
	return latest_path, report_time


def render_step_indicator(status_placeholder, statuses: list[str]) -> None:
	"""Render module execution states for the live audit pipeline."""

	status_icon = {
		"COMPLETE": "✅",
		"RUNNING": "🔄",
		"WAITING": "⏳",
	}

	rows = [
		f"{status_icon.get(statuses[0], '⏳')} [{statuses[0]}] Module 1: PII Detection Probing",
		f"{status_icon.get(statuses[1], '⏳')} [{statuses[1]}] Module 2: Regurgitation Detection",
		f"{status_icon.get(statuses[2], '⏳')} [{statuses[2]}] Module 3: Membership Inference",
	]

	status_placeholder.markdown("\n\n".join(rows))


def capture_process_output(process: subprocess.Popen, output_lines: list[str], output_lock: threading.Lock) -> None:
	"""Read subprocess stdout in a background thread so UI updates stay responsive."""

	if process.stdout is None:
		return

	for line in process.stdout:
		clean_line = line.rstrip("\n")
		with output_lock:
			output_lines.append(clean_line)


# Session state persists audit data across Streamlit reruns.
if "audit_output" not in st.session_state:
	st.session_state.audit_output = ""
if "scores" not in st.session_state:
	st.session_state.scores = {}
if "latest_report" not in st.session_state:
	st.session_state.latest_report = None
if "latest_report_time" not in st.session_state:
	st.session_state.latest_report_time = None
if "audit_status" not in st.session_state:
	st.session_state.audit_status = "IDLE"
if "last_exit_code" not in st.session_state:
	st.session_state.last_exit_code = None


# Dark, card-based design with security-console styling and accent glow.
st.markdown(
	"""
	<style>
		@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;700;800&display=swap');

		html, body, [class*="css"] {
			font-family: 'Inter', sans-serif;
		}

		.stApp {
			background:
				radial-gradient(circle at 5% 0%, rgba(34, 211, 238, 0.10), transparent 25%),
				radial-gradient(circle at 95% 0%, rgba(0, 208, 132, 0.08), transparent 23%),
				linear-gradient(180deg, #05070f 0%, #0a1020 100%);
		}

		.block-container {
			padding-top: 1.2rem;
			padding-bottom: 1.8rem;
		}

		.console-header {
			background: linear-gradient(130deg, rgba(7, 12, 24, 0.98), rgba(13, 23, 44, 0.95));
			border: 1px solid rgba(56, 189, 248, 0.25);
			border-radius: 18px;
			padding: 1.25rem 1.4rem;
			box-shadow: 0 0 0 1px rgba(56, 189, 248, 0.10), 0 16px 44px rgba(0, 0, 0, 0.45);
			margin-top: 1.5rem;
			margin-bottom: 1rem;
		}

		.console-title {
			font-size: clamp(1.9rem, 3vw, 2.9rem);
			font-weight: 800;
			letter-spacing: 0.1em;
			margin: 0;
			color: #e5f4ff;
		}

		.console-subtitle {
			margin: 0.25rem 0 0;
			color: #9fb5cb;
			font-size: 0.98rem;
		}

		.status-badge {
			display: inline-block;
			margin-top: 0.55rem;
			padding: 0.28rem 0.65rem;
			border-radius: 999px;
			font-size: 0.78rem;
			font-weight: 800;
			letter-spacing: 0.06em;
			background: rgba(0, 208, 132, 0.18);
			border: 1px solid rgba(0, 208, 132, 0.38);
			color: #00d084;
		}

		.terminal-card {
			background: linear-gradient(160deg, rgba(4, 10, 20, 0.96), rgba(12, 16, 28, 0.96));
			border: 1px solid rgba(56, 189, 248, 0.20);
			border-radius: 14px;
			padding: 0.95rem;
			margin-bottom: 0.65rem;
			font-family: 'JetBrains Mono', monospace;
		}

		.terminal-title {
			font-size: 0.83rem;
			color: #67e8f9;
			margin-bottom: 0.6rem;
			letter-spacing: 0.08em;
		}

		.step-row {
			display: flex;
			gap: 0.55rem;
			padding: 0.15rem 0;
			font-size: 0.88rem;
		}

		.step-state {
			font-weight: 700;
			min-width: 90px;
		}

		.step-label {
			color: #c8d8e8;
		}

		.metric-card {
			background: linear-gradient(160deg, rgba(8, 13, 24, 0.98), rgba(11, 20, 36, 0.96));
			border: 1px solid rgba(148, 163, 184, 0.22);
			border-radius: 14px;
			padding: 0.9rem;
			height: 100%;
		}

		.metric-label {
			color: #a4b6cb;
			font-size: 0.82rem;
			text-transform: uppercase;
			letter-spacing: 0.08em;
		}

		.metric-score {
			font-size: 1.65rem;
			font-weight: 800;
			margin: 0.2rem 0 0.35rem;
			line-height: 1.1;
		}

		.metric-risk-badge {
			display: inline-block;
			padding: 0.18rem 0.45rem;
			border-radius: 999px;
			font-size: 0.72rem;
			font-weight: 800;
			letter-spacing: 0.05em;
			margin-bottom: 0.5rem;
			color: #03111f;
		}

		.metric-track {
			height: 0.52rem;
			border-radius: 999px;
			background: rgba(148, 163, 184, 0.22);
			overflow: hidden;
		}

		.metric-fill {
			height: 100%;
			border-radius: inherit;
		}

		.terminal-box {
			font-family: 'JetBrains Mono', monospace;
			padding: 0.85rem;
			border-radius: 10px;
			background: rgba(15, 23, 42, 0.9);
			border: 1px solid rgba(103, 232, 249, 0.25);
			color: #d8ebff;
		}
	</style>
	""",
	unsafe_allow_html=True,
)


# Main branding header.
st.markdown(
	"""
	<div class="console-header">
		<h1 class="console-title">SPECTRA</h1>
		<p class="console-subtitle">// Privacy Intelligence Console</p>
		<span class="status-badge">SYSTEM OPERATIONAL</span>
	</div>
	""",
	unsafe_allow_html=True,
)


# Sidebar contains control panel details and run trigger.
with st.sidebar:
	st.markdown("## Spectra Control")
	st.caption("Security-focused model privacy operations")
	st.markdown("### Model Under Test")
	st.markdown(f"<div class='terminal-box'>{MODEL_NAME}</div>", unsafe_allow_html=True)

	now = datetime.now()
	st.markdown("### Session Info")
	st.markdown(f"**Date:** {now.strftime('%Y-%m-%d')}")
	st.markdown(f"**Time:** {now.strftime('%H:%M:%S')}")

	audit_status = st.session_state.audit_status
	status_color = "#94a3b8"
	if audit_status == "RUNNING":
		status_color = "#22d3ee"
	elif audit_status == "COMPLETE":
		status_color = "#00d084"

	st.markdown("### Audit Status")
	st.markdown(
		f"<div class='terminal-box'><span style='color:{status_color}; font-weight:700;'>[{audit_status}]</span></div>",
		unsafe_allow_html=True,
	)

	run_audit = st.button("Run Audit", use_container_width=True, type="primary")


# Create reusable placeholders for live execution and results areas.
execution_area = st.container()
results_area = st.container()
report_area = st.container()


# Trigger end-to-end audit execution when button is clicked.
if run_audit:
	st.session_state.audit_status = "RUNNING"
	st.session_state.audit_output = ""
	st.session_state.scores = {}
	st.session_state.last_exit_code = None

	with execution_area:
		st.subheader("Audit Execution")
		step_placeholder = st.empty()
		progress_placeholder = st.empty()
		output_preview = st.empty()

		step_statuses = ["RUNNING", "WAITING", "WAITING"]
		render_step_indicator(step_placeholder, step_statuses)
		module_progress = progress_placeholder.progress(0.02)

		with st.spinner("Running Spectra Audit..."):
			process = subprocess.Popen(
				[sys.executable, "main.py"],
				cwd=PROJECT_ROOT,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
				text=True,
				bufsize=1,
			)

			output_lines: list[str] = []
			output_lock = threading.Lock()
			reader_thread = threading.Thread(
				target=capture_process_output,
				args=(process, output_lines, output_lock),
				daemon=True,
			)
			reader_thread.start()

			start_time = time.time()
			while process.poll() is None:
				elapsed = time.time() - start_time

				# Simulate module status progression using elapsed time windows.
				if elapsed < 40:
					step_statuses = ["RUNNING", "WAITING", "WAITING"]
					progress_value = min(0.33, elapsed / 120)
				elif elapsed < 90:
					step_statuses = ["COMPLETE", "RUNNING", "WAITING"]
					progress_value = min(0.66, 0.33 + (elapsed - 40) / 150)
				elif elapsed < 130:
					step_statuses = ["COMPLETE", "COMPLETE", "RUNNING"]
					progress_value = min(0.95, 0.66 + (elapsed - 90) / 100)
				else:
					step_statuses = ["COMPLETE", "COMPLETE", "RUNNING"]
					progress_value = 0.98

				render_step_indicator(step_placeholder, step_statuses)
				module_progress.progress(progress_value)

				with output_lock:
					preview_text = "\n".join(output_lines[-16:])
				output_preview.code(preview_text, language="text")

				time.sleep(2)

			# Finalize UI state once process ends.
			reader_thread.join(timeout=2)
			step_statuses = ["COMPLETE", "COMPLETE", "COMPLETE"]
			render_step_indicator(step_placeholder, step_statuses)
			module_progress.progress(1.0)
			with output_lock:
				output_preview.code("\n".join(output_lines[-16:]), language="text")

			exit_code = process.wait()
			combined_output = "\n".join(output_lines)

			st.session_state.audit_output = combined_output
			st.session_state.last_exit_code = exit_code
			st.session_state.scores = parse_scores(combined_output)
			st.session_state.latest_report, st.session_state.latest_report_time = find_latest_report()
			st.session_state.audit_status = "COMPLETE"

		if st.session_state.last_exit_code == 0:
			st.success("Audit completed successfully.")
		else:
			st.error(f"Audit completed with errors (exit code {st.session_state.last_exit_code}).")


# Ensure latest report metadata remains visible across refreshes.
if not st.session_state.latest_report:
	st.session_state.latest_report, st.session_state.latest_report_time = find_latest_report()


# Render score cards and terminal-style result diagnostics.
with results_area:
	st.subheader("Audit Results")

	scores = st.session_state.scores
	if scores:
		metrics = [
			("PII Risk", float(scores.get("pii", 0.0))),
			("Regurgitation Risk", float(scores.get("regurgitation", 0.0))),
			("Membership Inference Risk", float(scores.get("membership", 0.0))),
			("Overall", float(scores.get("overall", 0.0))),
		]

		columns = st.columns(4)
		for col, (label, value) in zip(columns, metrics):
			risk_color = get_risk_color(value)
			risk_label = get_risk_label(value)
			with col:
				st.markdown(
					f"""
					<div class="metric-card">
						<div class="metric-label">{label}</div>
						<div class="metric-score" style="color:{risk_color};">{value:.2f}/100</div>
						<div class="metric-risk-badge" style="background:{risk_color};">{risk_label}</div>
						<div class="metric-track">
							<div class="metric-fill" style="width:{value}%; background:{risk_color};"></div>
						</div>
					</div>
					""",
					unsafe_allow_html=True,
				)

		with st.expander("Raw Terminal Output", expanded=False):
			st.code(st.session_state.audit_output or "No terminal output captured.", language="text")

		st.markdown("#### Parsed Score Payload")
		st.code(json.dumps(scores, indent=2), language="json")
	else:
		st.info("No score data available yet. Run an audit to populate results.")


# Show generated report details with terminal-like visual presentation.
with report_area:
	st.subheader("Latest Report")
	if st.session_state.latest_report:
		report_timestamp = "Unknown"
		if st.session_state.latest_report_time is not None:
			report_timestamp = st.session_state.latest_report_time.strftime("%Y-%m-%d %H:%M:%S")

		st.markdown(
			f"""
			<div class="terminal-box">
				<p style="margin:0 0 0.45rem 0; color:#67e8f9;">LATEST_REPORT_PATH</p>
				<p style="margin:0 0 0.6rem 0;">{st.session_state.latest_report}</p>
				<p style="margin:0; color:#9fb5cb;">Generated: {report_timestamp}</p>
			</div>
			""",
			unsafe_allow_html=True,
		)
		st.info("Open the HTML report path in your browser to view the complete formatted audit dashboard.")
	else:
		st.warning("No HTML report found in reports/. Run an audit to generate one.")
