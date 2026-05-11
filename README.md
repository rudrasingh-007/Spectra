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
SYSTEM         : LLM Privacy Auditing Tool
VERSION        : 1.0
STATUS         : OPERATIONAL
CLASSIFICATION : OPEN SOURCE
TARGET         : Large Language Models
```

"Spectra systematically interrogates language models to surface latent privacy exposure before deployment."

## DASHBOARD PREVIEW
![Spectra Dashboard](assets/dashboard_preview.png)

## OVERVIEW

Spectra is a Python-based LLM privacy auditing toolkit that stress-tests language models against three high-impact privacy attack vectors. It runs targeted probes, computes weighted risk scores, captures structured findings, and generates a detailed HTML audit report with Streamlit-based live execution visibility.

## FEATURES

```text
[MODULE-1]  PII Detection Probing          8 adversarial prompts across social engineering vectors
[MODULE-2]  Regurgitation Detection        Exact + semantic similarity against 8 sensitive documents
[MODULE-3]  Membership Inference Heuristic    Confidence gap analysis across target vs random corpora
[CORE]      Weighted Risk Scoring          Entity-type weighted scoring with critical/high/low tiers
[CORE]      Detailed HTML Report           Per-prompt breakdowns, similarity tables, CSS bar charts
[CORE]      Live Streamlit Dashboard       Real-time execution with step indicators and progress bar
[CORE]      Error Handling + Logging       Per-call exception handling with spectra.log audit trail
[CORE]      Auto Report Cleanup            Keeps last 5 reports, auto-deletes older ones
```

## AUDIT PIPELINE

```text
[PROMPT ENGINE] → [PII DETECTOR] → [REGURGITATION DETECTOR] → [MEMBERSHIP INFERENCE] → [REPORT GENERATOR] → [DASHBOARD]
```

## PIPELINE ARCHITECTURE

```text
INPUT LAYER
	└── Prompt Engine  →  8 adversarial prompts per module

PROCESSING LAYER
	├── PII Detector         →  Presidio entity recognition + weighted scoring
	├── Regurgitation Det.   →  RapidFuzz exact + sentence-transformers semantic
	└── Membership Inference →  Confidence gap analysis, hybrid scoring

OUTPUT LAYER
	├── HTML Report    →  Detailed per-module breakdown with charts
	├── Dashboard      →  Streamlit live control panel
	└── spectra.log    →  Structured audit trail
```

| Stage | Component | Description |
|---|---|---|
| 1 | PII Detector | Multi-prompt PII probing with weighted entity scoring |
| 2 | Regurgitation Detector | Exact and semantic similarity checks against sensitive corpus |
| 3 | Membership Inference | Target vs random confidence gap analysis |
| 4 | Report Generator | Detailed standalone HTML report with module breakdowns |
| 5 | Streamlit Dashboard | Live execution panel, progress states, and result visualization |

## CORE MODULES

```text
[+] PII Detection Probing
		Uses crafted extraction prompts and Presidio entity analysis to detect leaked emails,
		phone numbers, names, addresses, and identifier patterns.

[+] Verbatim Regurgitation Detection
		Tests whether the model reproduces sensitive-style text using exact similarity
		(RapidFuzz) and semantic similarity (Sentence Transformers).

[+] Membership Inference Heuristic
		Compares completion confidence between likely-seen corpus text and random nonsense
		text to estimate potential membership inference signal.
```

## RISK CLASSIFICATION MATRIX

```text
CRITICAL   PII Score ----------- 100/100   Privacy breach confirmed. Halt deployment.
HIGH       MEM Score ----------- 060/100   Significant exposure. Audit before production.
MEDIUM     REG Score ----------- 020/100   Moderate signal. Investigate findings.
LOW        ALL Score ----------- 010/100   Minimal exposure. Monitor across updates.
```

## PRIVACY THREAT SURFACE

| Vector | Method | Tool |
|--------|--------|------|
| PII Extraction | Adversarial prompting | Presidio + weighted scoring |
| Semantic Regurgitation | Meaning-based similarity | sentence-transformers |
| Verbatim Reproduction | Exact text matching | rapidfuzz |
| Membership Inference | Confidence gap analysis | hybrid exact + semantic |
| Social Engineering | Role-play prompt injection | custom prompt engine |

## SCREENSHOTS

### Spectra Dashboard — Audit Results
![Spectra Dashboard — Audit Results](assets/dashboard_preview.png)

### Spectra Dashboard — Live Audit Execution
![Spectra Dashboard — Live Audit Execution](assets/dashboard_running.png)

### Spectra HTML Audit Report
![Spectra HTML Audit Report](assets/report_preview.png)

### Spectra Terminal Output with Logging
![Spectra Terminal Output with Logging](assets/terminal_preview.png)

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
| streamlit | Future dashboard interface |
| Supported Models | gemini-3.1-flash-lite, gemini-2.5-flash, gemini-2.5-flash-lite |

## SYSTEM STRUCTURE

```text
Spectra/
├─ main.py
├─ dashboard.py
├─ modules/
│  ├─ pii_detector.py
│  ├─ regurgitation_detector.py
│  └─ membership_inference.py
├─ utils/
│  └─ report_generator.py
├─ reports/
├─ prompts/
├─ assets/
└─ requirements.txt
```

## DEPLOYMENT

```bash
# 1) Clone
git clone https://github.com/<your-username>/Spectra.git
cd Spectra

# 2) Virtual environment
python -m venv venv

# 3) Activate (Windows PowerShell)
venv\Scripts\Activate.ps1

# macOS/Linux alternative
# source venv/bin/activate

# 4) Dependencies
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

Run the CLI audit:

```bash
python main.py
```

Run the live dashboard:

```bash
streamlit run dashboard.py
```

## Sample Output

```text
[+] Starting Spectra Audit...
[+] Running: PII Detection
[+] Running: Verbatim Regurgitation Detection
[+] Running: Membership Inference Heuristic
[+] Audit complete
[+] Report generated at: reports/spectra_audit_report_YYYYMMDD_HHMMSS.html
```

The HTML report includes model metadata, audit timestamp, per-module visual risk bars, and a combined risk score.

## Research References

1. Carlini et al. (2021), *Extracting Training Data from Large Language Models*.
2. Shokri et al. (2017), *Membership Inference Attacks against Machine Learning Models*.
3. Differential Privacy literature and foundational privacy-preserving ML research.

Note: This project implements heuristic approximations inspired by the above research. It does not fully replicate the cryptographic methods described in these papers.

## ROADMAP

```text
[COMPLETE]  v1.0 — Core 3-module privacy risk evaluation pipeline with HTML report and Streamlit dashboard
[QUEUED]    v4.0 — OpenAI support, PDF export, multi-model comparison
[QUEUED]    v5.0 — Scheduled audits, API endpoint, fine-tuned PII classifier
```

## CONTRIBUTING

```text
>> Fork the repository
>> Create a feature branch
>> Keep changes modular and testable
>> Open a pull request with clear rationale and sample output
```

## LICENSE

MIT License

## Disclaimer

This project is for **educational and research use only**. Use responsibly, with explicit authorization, and in compliance with applicable legal and organizational requirements.

## Author

**Rudra Singh**  
Cybersecurity Aspirant

```text
[ SPECTRA ] — INTERROGATE. MEASURE. SECURE. — OPEN SOURCE
```

