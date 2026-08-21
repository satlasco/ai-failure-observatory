# AI Failure Observatory

🇹🇷 [Türkçe Dokümantasyon](README.tr.md)

> Behavioral safety, vulnerability probing, and product-risk auditing for Generative AI & Large Language Models.

A lightweight, local-first platform designed to detect, track, stress-test, and report on **6 critical LLM failure modes** before deployment into production workflows.

---

## 🚀 Key Features

### 1. 🧠 Core Behavioral Failure Detectors
- **Hallucinations (`hallucinations`):** Catches invented citations (academic papers, authors, fake volumes) and non-existent factual assertions.
- **Fake Confidence (`fake_confidence`):** Flags dogmatic, overconfident statements lacking appropriate epistemic hedging.
- **Context Loss (`context_loss`):** Detects short-term conversational forgetting and memory loss in multi-turn dialogues.
- **Instruction Drift (`instruction_drift`):** Catches violations of negative constraints and forbidden keyword instructions.
- **Persuasive Manipulation (`manipulation`):** Identifies deceptive steering, urgency nudges, and commercial pressure.
- **Recursive Reasoning Collapse (`recursive_reasoning_collapse`):** Flags circular logic traps and repetitive degradation.

### 2. ⚡ Live Adversarial LLM Testing
- Direct live model probing via lightweight `urllib.request` integration:
  - 🟢 **Built-in Heuristic Simulator:** Zero API key required, instant offline testing.
  - ✨ **Google Gemini:** `gemini-2.0-flash`, `gemini-1.5-pro`
  - 🧠 **OpenAI:** `gpt-4o-mini`, `gpt-4o`, `o3-mini`
  - ⚡ **Anthropic Claude:** `claude-3-5-sonnet-20241022`

### 3. 💾 Persistent Incident Storage & Real-Time Risk Index
- Every manual probe or live stress-test is automatically recorded in `data/incidents.json`.
- The Risk Dashboard dynamically updates its aggregate risk score, incident count, and severity charts based on live test results.

### 4. 📄 Executive Compliance Audit Report Export
- Generate and download structured Markdown compliance audit reports mapping detected vulnerabilities to risk levels and mitigation actions.

### 5. 🌐 Full Bilingual UI (TR ⟷ EN)
- Instant dynamic translation between English and Turkish across 100% of dashboard views, controls, and metric cards.

### 6. 🔌 Dynamic Port Conflict Management
- Starts on port `5089` by default with automatic fallback to next free port if occupied.

---

## 🛠️ Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/adacreativeco/ai-failure-observatory.git
cd ai-failure-observatory
pip install -r requirements.txt
```

### 2. Run the Observatory Server
```bash
python server.py
```
Open [http://localhost:5089](http://localhost:5089) in your browser.

### 3. Run Automated Unit Tests
```bash
python -m unittest tests/test_observatory.py
```

### 4. Run Reproducible Benchmark Evals
```bash
python experiments/reproducible_evals/run_all_evals.py
```

---

## 📂 Architecture

```
ai-failure-observatory/
├── server.py                       # HTTP server & REST API (Port 5089)
├── index.html                      # Single-page bilingual dashboard UI
├── src/
│   ├── failure_analyzer.py         # Heuristic failure detection engine
│   ├── storage.py                  # Persistent JSON incident storage
│   ├── llm_client.py               # Multi-provider live LLM probe client
│   ├── eval_generator.py           # Evaluation test case generation
│   └── utils.py                    # Text processing & token helpers
├── taxonomy/
│   ├── ai_failure_taxonomy.md      # Comprehensive failure reference
│   └── taxonomy_utils.py           # Taxonomy loader & severity helpers
├── analysis/
│   └── risk_analysis.py            # Product risk scoring formulas & reports
├── experiments/
│   ├── reproducible_evals/         # 6 benchmark reproducibility tests
│   └── synthetic/                  # Synthetic failure data generators
├── tests/
│   └── test_observatory.py         # Comprehensive unit test suite (13 tests)
├── data/                           # Incident storage directory (incidents.json)
└── requirements.txt                # Lightweight dependencies
```

---

## 📄 License

Distributed under the Apache 2.0 License. See [LICENSE](LICENSE) for details.
