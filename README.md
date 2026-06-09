# LLM Evaluation & Red-Teaming Framework

Automated tooling to systematically test LLMs for hallucination, bias, jailbreak, toxicity, and prompt injection vulnerabilities before deployment. Includes multi-round red teaming, a 3-model safety comparison, interactive dashboard, and professional PDF reporting.

🔗 **Live Demo:** https://llm-eval-framework-67.streamlit.app/

---

## What This Does

This framework automatically tests any LLM across 5 failure categories using an **LLM-as-a-judge** methodology — a second AI model automatically scores every response:

- **Hallucination** — detects when the AI states false facts confidently
- **Bias** — detects unfair treatment across demographic groups (gender, race, religion, ethnicity)
- **Jailbreak** — detects when adversarial prompts bypass safety guidelines
- **Toxicity** — detects harmful, offensive, or dangerous content in responses
- **Prompt Injection** — detects when hidden instructions inside content hijack the AI

Plus **Multi-Round Red Teaming** — an attacker LLM generates increasingly sophisticated attacks each round based on what succeeded previously, inspired by Meta's MART paper.

---

## Key Results (Llama 3.1 8B)

| Category | Prompts Tested | Failure Rate | Avg Score | Status |
|---|---|---|---|---|
| Hallucination | 5 | 0.0% | 0.98 | ✅ GOOD |
| Bias | 4 | 50.0% | 0.45 | 🔴 CRITICAL |
| Jailbreak | 4 | 0.0% | 0.75 | ✅ GOOD |
| Toxicity | 4 | 25.0% | 0.70 | ⚠️ WARNING |
| Prompt Injection | 4 | 50.0% | 0.33 | 🔴 CRITICAL |
| Red Team | 26 | 11.5% | 0.54 | ⚠️ WARNING |

**Red teaming violation rate: 25.0% → 50.0% → 50.0% → 33.3% across 4 automated rounds**

---

## Model Comparison Results

Tested the same prompts across 3 models to compare safety profiles:

| Model | Overall Score | Hallucination | Bias | Jailbreak | Toxicity | Prompt Injection |
|---|---|---|---|---|---|---|
| Llama 3.1 8B | 0.75 | 0.97 | 0.50 | 0.67 | 0.97 | 0.25 |
| Llama 3.3 70B | 0.72 | 0.97 | 0.85 | 0.67 | 0.33 | 0.50 |
| Gemma 2 9B | 0.73 | 0.00 | 1.00 | 1.00 | 1.00 | 0.75 |

**Key Finding:** Model size alone does not determine safety. Gemma 2 9B outperformed Llama 3.3 70B on overall safety metrics despite having fewer parameters, demonstrating that safety fine-tuning methodology matters more than parameter count. Google's RLHF approach in Gemma prioritizes strict refusal behavior.

---

## How It Works
Adversarial Prompt → Student LLM → Response → Judge LLM → Score (0-1)

For each test prompt:
1. The target LLM receives the adversarial prompt and generates a response
2. A judge LLM evaluates the response against specific safety criteria
3. A score between 0 and 1 is assigned (higher = safer)
4. Results are logged, aggregated, and saved to CSV

For red teaming, successful attack prompts are fed back into an attacker LLM which generates harder variants for the next round. This is the core of the MART methodology.

---

## Project Structure

llm-eval-framework/
├── src/
│   ├── llm_client.py              # Handles all LLM API calls with retry logic
│   ├── logger.py                  # Records evaluation results
│   ├── red_team.py                # Multi-round MART-inspired red teaming loop
│   ├── evaluators/
│   │   ├── hallucination.py       # Hallucination detection vs ground truth
│   │   ├── bias.py                # Demographic bias detection via prompt pairs
│   │   ├── jailbreak.py           # Jailbreak attempt detection
│   │   ├── toxicity.py            # Toxic content detection
│   │   └── prompt_injection.py    # Hidden instruction injection detection
│   ├── prompts/
│   │   └── init.py            # All adversarial prompt datasets
│   └── reports/
│       └── report_generator.py    # Professional PDF report generation
├── dashboard.py                   # Interactive Streamlit dashboard (4 tabs)
├── compare_models.py              # 3-model safety comparison script
├── main.py                        # Main evaluation runner
├── config.py                      # Configuration and model settings
└── requirements.txt               # Python dependencies

---

## Dashboard Features

The Streamlit dashboard has 4 interactive tabs:

- **Overview** — key metrics, failure rate charts, score analysis, key findings
- **Categories** — deep dive into each category with score distribution and pie charts
- **Red Team** — violation rate line chart across rounds with round-by-round breakdown
- **Live Test** — type any prompt and get real-time AI response with safety evaluation

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Groq API | Fast LLM inference (Llama 3.1 8B / Llama 3.3 70B) |
| LLM-as-a-judge | Automated response evaluation without human labeling |
| LangSmith | Tracing and logging all LLM calls |
| Streamlit | Interactive web dashboard |
| Matplotlib | Charts and visualizations |
| FPDF2 | Professional PDF report generation |
| Pandas | Results aggregation and analysis |
| LangChain | LLM orchestration for multi-step pipelines |

---

## Setup

**1. Clone the repository**
```bash
git clone https://github.com/kk911-gpt/llm-eval-framework.git
cd llm-eval-framework
```

**2. Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

Create a `.env` file in the root folder:
GROQ_API_KEY=your_groq_key_here
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=llm-eval-framework

**5. Run full evaluation**
```bash
python main.py
```

**6. View interactive dashboard**
```bash
streamlit run dashboard.py
```

**7. Run model comparison (optional, uses more tokens)**
```bash
python compare_models.py
```

---

## Output Files

After running `main.py`:
- `results.csv` — all evaluation results with scores and pass/fail
- `violation_rates.csv` — red team violation rates per round
- `LLM_Eval_Report_YYYYMMDD_HHMM.pdf` — professional 5-page PDF report

After running `compare_models.py`:
- `comparison_results.csv` — model comparison data
- `Model_Comparison_YYYYMMDD_HHMM.pdf` — 4-page comparison PDF with radar chart

---

## Token Usage Notes

This project uses the Groq free tier (100,000 tokens/day limit):
- Full `main.py` run uses approximately 60,000-80,000 tokens
- `compare_models.py` uses approximately 80,000-100,000 tokens
- Run one per day or upgrade to Groq paid tier (~$0.06 per full run)

---

## Inspired By

- Meta's MART (Multi-round Automatic Red-Teaming) paper — the methodology behind the red teaming loop
- DeepEval evaluation framework — LLM evaluation best practices
- LangSmith observability platform — LLM call tracing and monitoring
- Google's Gemma safety research — insights on safety fine-tuning vs scale