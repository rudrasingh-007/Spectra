"""Spectra audit entry point."""

from modules.membership_inference import run_membership_inference
from modules.pii_detector import run_pii_detection
from modules.regurgitation_detector import run_regurgitation_detection
from utils.report_generator import generate_report


def main():
	"""Run the full Spectra audit workflow and generate a report."""

	print("Starting Spectra Audit...")

	pii_score = run_pii_detection()
	regurgitation_score = run_regurgitation_detection()
	membership_score = run_membership_inference()

	print("\nAudit Summary")
	print(f"PII risk score: {pii_score}/100")
	print(f"Regurgitation risk score: {regurgitation_score}/100")
	print(f"Membership inference risk score: {membership_score}/100")

	report_path = generate_report(
		pii_score=pii_score,
		regurgitation_score=regurgitation_score,
		membership_score=membership_score,
		model_name="gemma-3-12b-it",
	)

	print(f"\nReport generated: {report_path}")


if __name__ == "__main__":
	main()
