```text
███████╗██████╗ ███████╗ ██████╗████████╗██████╗  █████╗
██╔════╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔══██╗
███████╗██████╔╝█████╗  ██║        ██║   ██████╔╝███████║
╚════██║██╔═══╝ ██╔══╝  ██║        ██║   ██╔══██╗██╔══██║
███████║██║     ███████╗╚██████╗   ██║   ██║  ██║██║  ██║
╚══════╝╚═╝     ╚══════╝ ╚═════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
```

# Spectra

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Privacy Audit](https://img.shields.io/badge/Focus-LLM%20Privacy%20Auditing-0f172a)
![Status](https://img.shields.io/badge/Status-v1%20Complete-16a34a)
![Mode](https://img.shields.io/badge/Use-Research%20%26%20Education-3b3f52)

**Tagline:** Probe. Measure. Expose privacy risk before deployment.

```ini
[SPECTRA_SYSTEM]
version = v1.0
status = operational
purpose = LLM Privacy Auditing Tool
primary_model = gemma-3-12b-it
```

Spectra is a Python-based LLM privacy auditing toolkit that stress-tests language models against three high-impact attack vectors. It runs targeted probes, computes risk scores, and produces an HTML audit report for fast technical review.

## What Spectra Does

```text
[+] Simulates adversarial prompt behavior against an LLM
[+] Measures leakage and memorization patterns with scoring logic
[+] Aggregates module outputs into a unified risk posture
[+] Generates a timestamped HTML report in /reports
```

## Screenshots

### Spectra Dashboard — Audit Results
![Spectra Dashboard — Audit Results](assets/dashboard_preview.png)

### Spectra Dashboard — Live Audit Execution
![Spectra Dashboard — Live Audit Execution](assets/dashboard_running.png)

### Spectra HTML Audit Report
![Spectra HTML Audit Report](assets/report_preview.png)

### Spectra Terminal Output with Logging
![Spectra Terminal Output with Logging](assets/terminal_preview.png)

## Core Modules

```text
[+] PII Detection Probing
	Uses crafted extraction prompts and Presidio entity analysis to detect leaked emails,
	phone numbers, names, and addresses.

[+] Verbatim Regurgitation Detection
	Tests whether the model reproduces sensitive-style text using exact similarity
	(RapidFuzz) and semantic similarity (Sentence Transformers).

[+] Membership Inference Attack
	Compares completion confidence between likely-seen corpus text and random nonsense
	text to estimate potential membership inference signal.
```

## Audit Pipeline

```text
Input Model
   |
   v
PII Probing -----> Regurgitation Check -----> Membership Inference
   |                        |                          |
   +------------------------+--------------------------+
							|
							v
				 Score Aggregation (0-100)
							|
							v
				 HTML Report Generation
```

## Risk Scale

```text
LOW     0-30   ████░░░░░░
MEDIUM 31-70   ███████░░░
HIGH   71-100  ██████████
```

## Tech Stack

| Component | Purpose |
|---|---|
| Python 3.11 | Core runtime |
| google-genai | Gemini/Gemma model client |
| presidio-analyzer | PII entity detection |
| spacy | NLP backend support |
| rapidfuzz | String similarity scoring |
| sentence-transformers | Semantic similarity scoring |
| scikit-learn | ML/statistical support |
| reportlab | PDF/report utilities |
| streamlit | Future dashboard interface |

## Project Structure

```text
Spectra/
├── main.py
├── modules/
│   ├── pii_detector.py
│   ├── regurgitation_detector.py
│   └── membership_inference.py
├── utils/
│   └── report_generator.py
├── reports/
├── prompts/
└── requirements.txt
```

## Installation and Setup

```bash
git clone https://github.com/<your-username>/Spectra.git
cd Spectra

python -m venv venv
# Windows PowerShell
venv\Scripts\Activate.ps1
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

## How to Run

```bash
python main.py
```

## Sample Output

```text
[+] Starting Spectra Audit...
[+] Running: PII Detection
[+] Running: Verbatim Regurgitation Detection
[+] Running: Membership Inference Attack
[+] Audit complete
[+] Report generated at: reports/spectra_audit_report_YYYYMMDD_HHMMSS.html
```

The HTML report includes model metadata, audit timestamp, per-module visual risk bars, and a combined risk score.

## Research References

1. Carlini et al. (2021), *Extracting Training Data from Large Language Models*.
2. Shokri et al. (2017), *Membership Inference Attacks against Machine Learning Models*.
3. Differential Privacy literature and foundational privacy-preserving ML research.

## Roadmap

```text
[+] v1 complete: core 3-module privacy auditing pipeline + HTML reporting
[ ] Add OpenAI model support
[ ] Build interactive Streamlit dashboard
[ ] Add native PDF report export workflow
```

## Disclaimer

This project is for **educational and research use only**. Use responsibly, with explicit authorization, and in compliance with applicable legal and organizational requirements.

## Author

**Rudra Singh**  
Cybersecurity Aspirant

```text
Spectra does not guess trust. It measures it.
```

