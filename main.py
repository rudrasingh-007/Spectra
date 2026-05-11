"""Spectra audit entry point."""

import argparse
import logging

from modules.membership_inference import run_membership_inference
from modules.pii_detector import run_pii_detection
from modules.regurgitation_detector import run_regurgitation_detection
from utils.report_generator import generate_report


def setup_logger() -> logging.Logger:
	"""Configure a logger that writes to console and spectra.log."""

	logger = logging.getLogger("spectra")
	if logger.handlers:
		return logger

	logger.setLevel(logging.INFO)
	formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

	console_handler = logging.StreamHandler()
	console_handler.setLevel(logging.INFO)
	console_handler.setFormatter(formatter)

	file_handler = logging.FileHandler("spectra.log", encoding="utf-8")
	file_handler.setLevel(logging.INFO)
	file_handler.setFormatter(formatter)

	logger.addHandler(console_handler)
	logger.addHandler(file_handler)
	logger.propagate = False
	return logger


def main():
	"""Run the full Spectra audit workflow and generate a report."""

	logger = setup_logger()
	parser = argparse.ArgumentParser()
	parser.add_argument("--model")
	args = parser.parse_args()

	available_models = [
		"gemini-2.5-flash",
		"gemini-2.5-flash-lite-preview-06-17",
		"gemini-3.1-flash-lite",
		"gemma-3-12b-it",
	]

	if args.model in available_models:
		selected_model = args.model
	else:
		print("Select a model:")
		for index, model_name in enumerate(available_models, start=1):
			print(f"{index}. {model_name}")

		try:
			selection = int(input("Choose a model by number: "))
			selected_model = available_models[selection - 1]
		except Exception:
			selected_model = "gemini-3.1-flash-lite"

	print("Starting Spectra Audit...")
	logger.info("Starting Spectra Audit workflow")

	try:
		logger.info("Starting Module 1: PII Detection")
		pii_score, pii_findings = run_pii_detection(model=selected_model)
		logger.info("Completed Module 1: PII Detection (score=%s)", pii_score)
	except Exception:
		logger.exception("Module 1 failed. Continuing with safe defaults.")
		pii_score, pii_findings = 0, []

	try:
		logger.info("Starting Module 2: Regurgitation Detection")
		regurgitation_score, regurgitation_cases = run_regurgitation_detection(model=selected_model)
		logger.info("Completed Module 2: Regurgitation Detection (score=%s)", regurgitation_score)
	except Exception:
		logger.exception("Module 2 failed. Continuing with safe defaults.")
		regurgitation_score, regurgitation_cases = 0, []

	try:
		logger.info("Starting Module 3: Membership Inference")
		membership_score, membership_data = run_membership_inference(model=selected_model)
		logger.info("Completed Module 3: Membership Inference (score=%s)", membership_score)
	except Exception:
		logger.exception("Module 3 failed. Continuing with safe defaults.")
		membership_score, membership_data = 0, {}

	print("\nAudit Summary")
	print(f"PII risk score: {pii_score}/100")
	print(f"Regurgitation risk score: {regurgitation_score}/100")
	print(f"Membership inference risk score: {membership_score}/100")

	report_path = generate_report(
		pii_score=pii_score,
		pii_findings=pii_findings,
		regurgitation_score=regurgitation_score,
		regurgitation_cases=regurgitation_cases,
		membership_score=membership_score,
		membership_data=membership_data,
		model_name=selected_model,
	)
	logger.info("Report generated at %s", report_path)

	print(f"\nReport generated: {report_path}")


if __name__ == "__main__":
	main()
