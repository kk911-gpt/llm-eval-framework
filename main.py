from src.llm_client import get_response
from src.logger import log_result
from src.evaluators.hallucination import evaluate_hallucination
from src.evaluators.bias import evaluate_bias
from src.evaluators.jailbreak import evaluate_jailbreak
from src.red_team import run_full_red_team
from src.prompts import HALLUCINATION_PROMPTS, BIAS_PROMPTS, JAILBREAK_PROMPTS
from config import FAILURE_THRESHOLD, MAX_HALLUCINATION, MAX_BIAS, MAX_JAILBREAK
import pandas as pd
from tqdm import tqdm

results = []

# ─────────────────────────────────────────
# PART 1: HALLUCINATION
# ─────────────────────────────────────────
print("\n🚀 LLM Evaluation Framework — Day 5")
print("=" * 50)
print("PART 1: Hallucination Detection")
print("=" * 50)

for item in tqdm(HALLUCINATION_PROMPTS[:MAX_HALLUCINATION], desc="Hallucination"):
    response = get_response(item["prompt"])
    eval_result = evaluate_hallucination(
        prompt=item["prompt"],
        response=response,
        ground_truth=item["ground_truth"]
    )
    result = log_result(
        prompt=item["prompt"],
        response=response,
        category=eval_result["category"],
        score=eval_result["score"],
        passed=eval_result["passed"]
    )
    result["judge_reasoning"] = eval_result.get("judge_reasoning", "")
    results.append(result)

# ─────────────────────────────────────────
# PART 2: BIAS
# ─────────────────────────────────────────
print("\n" + "=" * 50)
print("PART 2: Bias Detection")
print("=" * 50)

for item in tqdm(BIAS_PROMPTS[:MAX_BIAS], desc="Bias"):
    response1 = get_response(item["prompt1"])
    response2 = get_response(item["prompt2"])
    eval_result = evaluate_bias(
        prompt1=item["prompt1"],
        prompt2=item["prompt2"],
        response1=response1,
        response2=response2,
        demographic=item["demographic"]
    )
    result = log_result(
        prompt=f"{item['prompt1']} vs {item['prompt2']}",
        response=f"R1: {response1[:100]} | R2: {response2[:100]}",
        category=eval_result["category"],
        score=eval_result["score"],
        passed=eval_result["passed"]
    )
    result["judge_reasoning"] = eval_result.get("judge_reasoning", "")
    results.append(result)

# ─────────────────────────────────────────
# PART 3: JAILBREAK
# ─────────────────────────────────────────
print("\n" + "=" * 50)
print("PART 3: Jailbreak Detection")
print("=" * 50)

for item in tqdm(JAILBREAK_PROMPTS[:MAX_JAILBREAK], desc="Jailbreak"):
    response = get_response(item["prompt"])
    eval_result = evaluate_jailbreak(
        prompt=item["prompt"],
        response=response
    )
    result = log_result(
        prompt=item["prompt"],
        response=response,
        category=eval_result["category"],
        score=eval_result["score"],
        passed=eval_result["passed"]
    )
    result["judge_reasoning"] = eval_result.get("judge_reasoning", "")
    result["jailbroken"] = eval_result.get("jailbroken", False)
    results.append(result)

# ─────────────────────────────────────────
# PART 4: RED TEAMING LOOP
# ─────────────────────────────────────────
print("\n" + "=" * 50)
print("PART 4: Multi-Round Red Teaming")
print("=" * 50)

red_team_results, violation_rates = run_full_red_team(num_rounds=4)
results.extend(red_team_results)

# ─────────────────────────────────────────
# SAVE ALL RESULTS
# ─────────────────────────────────────────
df = pd.DataFrame(results)
df.to_csv("results.csv", index=False)

# Save violation rates separately for dashboard
vr_df = pd.DataFrame({
    "round": list(range(1, len(violation_rates) + 1)),
    "violation_rate": violation_rates
})
vr_df.to_csv("violation_rates.csv", index=False)

# ─────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────
print("\n" + "=" * 50)
print("✅ COMPLETE EVALUATION DONE")
print("=" * 50)

print(f"\nTotal prompts tested: {len(results)}")

print("\n📊 Results by Category:")
for category in df['category'].unique():
    cat_df = df[df['category'] == category]
    fail_rate = (~cat_df['passed']).sum() / len(cat_df) * 100
    avg_score = cat_df['score'].mean()
    print(f"\n  {category.upper()}")
    print(f"    Average score:  {avg_score:.2f}")
    print(f"    Failure rate:   {fail_rate:.1f}%")
    print(f"    Total tested:   {len(cat_df)}")

print("\n📈 Red Team Violation Rates by Round:")
for i, rate in enumerate(violation_rates, 1):
    bar = "█" * int(rate / 5)
    print(f"  Round {i}: {rate:5.1f}% {bar}")

print("\nRun: streamlit run dashboard.py")

# ─────────────────────────────────────────
# GENERATE PDF REPORT
# ─────────────────────────────────────────
from src.reports.report_generator import generate_pdf_report
generate_pdf_report()