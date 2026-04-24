# Spectra

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-1f8b4c)
![License](https://img.shields.io/badge/Use-Research%20%26%20Education-3b3f52)

**Tagline:** Privacy stress-testing for modern language models.

Spectra is an **LLM Privacy Auditing Tool** built in Python. It probes AI language models using targeted prompts and similarity-based analysis to identify privacy risks across three core attack vectors. The tool produces module-level risk scores and generates a professional HTML audit report for review.

## What Spectra Does

Spectra simulates realistic adversarial behavior against a selected LLM and evaluates how the model responds under privacy-sensitive conditions. It helps researchers and practitioners quickly assess whether a model appears vulnerable to leaking sensitive information, memorized text, or signs of training-data membership.

## Core Modules

### 1. PII Detection Probing

This module sends crafted extraction-style prompts designed to coax private details (for example: emails, phone numbers, names, and addresses) from the model output. Responses are scanned with Presidio to detect and classify potential PII entities.

### 2. Verbatim Regurgitation Detection

This module tests whether the model reproduces sensitive-looking content with high fidelity. It compares model outputs against known reference texts using:

- exact-text similarity (RapidFuzz)
- semantic similarity (Sentence Transformers)

High similarity scores are flagged as potential memorization/regurgitation risk.

### 3. Membership Inference Attack

This module evaluates whether the model shows stronger completion confidence on likely-in-training text versus random nonsense text. A significant confidence gap can indicate potential membership inference risk.

## Tech Stack

| Component | Purpose |
|---|---|
| Python 3.11 | Core language/runtime |
| google-genai | Gemini/Gemma model client integration |
| presidio-analyzer | PII detection and entity classification |
| spaCy | NLP support for Presidio pipelines |
| rapidfuzz | Fast exact/fuzzy text similarity |
| sentence-transformers | Embedding-based semantic similarity |
| scikit-learn | Supporting ML/statistical utilities |
| reportlab | Report export utilities |
| streamlit | Optional dashboard/UI layer |

## Installation and Run

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/Spectra.git
cd Spectra
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set API key in `.env`

```env
GEMINI_API_KEY=your_api_key_here
```

### 5. Run Spectra

```bash
python main.py
```

## Sample Output

When the audit completes, Spectra prints module risk scores in the terminal and generates a timestamped HTML report in the `reports/` directory.

Example report file:

`reports/spectra_audit_report_YYYYMMDD_HHMMSS.html`

The report includes:

- model name tested
- audit date and time
- per-module risk bars (green/yellow/red thresholds)
- overall combined risk score

## Research References

1. Carlini et al. (2021), *Extracting Training Data from Large Language Models*.
2. Shokri et al. (2017), *Membership Inference Attacks against Machine Learning Models*.
3. Differential Privacy literature (foundational works on privacy-preserving learning and formal guarantees).

## Disclaimer

Spectra is intended **for educational and research purposes only**. It should be used responsibly, with proper authorization, and in compliance with applicable laws, regulations, and organizational policies.

## Author

**Rudra Singh**  
Cybersecurity Aspirant

