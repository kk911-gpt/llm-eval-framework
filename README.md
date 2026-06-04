# LLM Evaluation & Red-Teaming Framework

Automated tooling to systematically test LLMs for hallucination, bias, 
and jailbreak vulnerabilities before deployment.

## What This Does

This framework automatically tests any LLM across 4 failure categories:

- **Hallucination** — detects when the AI states false facts confidently
- **Bias** — detects unfair treatment of different demographic groups
- **Jailbreak** — detects when adversarial prompts bypass safety guidelines
- **Red Teaming** — multi-round automated attacks that evolve each round

## Key Results

| Category | Prompts Tested | Failure Rate | Avg Score |
|---|---|---|---|
| Hallucination | 10 | 0.0% | 1.00 |
| Bias | 8 | 12.5% | 0.68 |
| Jailbreak | 8 | 12.5% | 0.80 |
| Red Team | 14 | 21.4% | 0.64 |

**Red teaming violation rate: 37.5% → 0.0% across 2 automated rounds**

## How It Works

Adversarial Prompt → Student LLM → Response → Judge LLM → Score

For each test prompt:
1. The target LLM receives the prompt and generates a response
2. A judge LLM evaluates the response against specific criteria
3. A score between 0-1 is assigned (higher = better)
4. Results are logged, aggregated, and visualized

For red teaming, successful attack prompts are fed back into an 
attacker LLM which generates harder variants for the next round.
This is inspired by Meta's MART (Multi-round Automatic Red-Teaming) paper.

## Project Structure

llm-eval-framework/
├── src/
│   ├── llm_client.py          # Handles all LLM API calls
│   ├── logger.py              # Records evaluation results
│   ├── red_team.py            # Multi-round red teaming loop
│   ├── evaluators/
│   │   ├── hallucination.py   # Hallucination detection
│   │   ├── bias.py            # Demographic bias detection
│   │   └── jailbreak.py       # Jailbreak attempt detection
│   ├── prompts/
│   │   └── init.py        # All test prompt datasets
│   └── reports/
│       └── report_generator.py # PDF report generation
├── dashboard.py               # Streamlit visual dashboard
├── main.py                    # Main runner
└── config.py                  # Configuration and settings

## Tech Stack

- **LLM:** Llama 3.3 70B via Groq API
- **Evaluation:** LLM-as-a-judge pattern
- **Logging:** LangSmith
- **Dashboard:** Streamlit + Matplotlib
- **Reports:** FPDF2
- **Data:** Pandas

## Setup

1. Clone the repository
```bash
git clone https://github.com/kk911-gpt/llm-eval-framework.git
cd llm-eval-framework
```

2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

3. Install dependencies
```bash
pip install deepeval langsmith langchain langchain-groq groq openai python-dotenv pandas matplotlib streamlit fpdf2 requests tqdm
```

4. Set up environment variables
Create a `.env` file:

GROQ_API_KEY=your_groq_key_here
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=llm-eval-framework

5. Run evaluation
```bash
python main.py
```

6. View dashboard
```bash
streamlit run dashboard.py
```

## Inspired By

- Meta's MART (Multi-round Automatic Red-Teaming) paper
- DeepEval evaluation framework
- LangSmith observability platform

