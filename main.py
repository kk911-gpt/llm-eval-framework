from src.llm_client import get_response
from src.logger import log_result
from src.evaluators.hallucination import evaluate_hallucination
from src.evaluators.bias import evaluate_bias
from src.evaluators.jailbreak import evaluate_jailbreak
from src.red_team import run_full_red_team
from src.evaluators.toxicity import evaluate_toxicity
from src.evaluators.prompt_injection import evaluate_prompt_injection
from src.prompts import HALLUCINATION_PROMPTS, BIAS_PROMPTS, JAILBREAK_PROMPTS, TOXICITY_PROMPTS, INJECTION_PROMPTS
from config import FAILURE_THRESHOLD, MAX_HALLUCINATION, MAX_BIAS, MAX_JAILBREAK, MAX_TOXICITY, MAX_INJECTION
import pandas as pd
from tqdm import tqdm

results = []

# ─────────────────────────────────────────
# PART 1: HALLUCINATION
# ─────────────────────────────────────────
print("\n🚀 LLM Evaluation Framework  ")
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
# PART 4: TOXICITY DETECTION
# ─────────────────────────────────────────
print("\n" + "=" * 50)
print("PART 4: Toxicity Detection")
print("=" * 50)

for item in tqdm(TOXICITY_PROMPTS[:MAX_TOXICITY], desc="Toxicity"):
    # Get AI response
    response = get_response(item["prompt"])
    
    # Judge the response for toxic content
    eval_result = evaluate_toxicity(
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
    result["toxic"] = eval_result.get("toxic", False)
    result["toxicity_type"] = eval_result.get("toxicity_type", "NONE")
    results.append(result)

# ─────────────────────────────────────────
# PART 5: PROMPT INJECTION DETECTION
# ─────────────────────────────────────────
print("\n" + "=" * 50)
print("PART 5: Prompt Injection Detection")
print("=" * 50)

for item in tqdm(INJECTION_PROMPTS[:MAX_INJECTION], desc="Prompt Injection"):
    # Combine task and content into one prompt
    full_prompt = f"""
    Your task: {item['system_task']}
    
    Content to process:
    {item['injected_content']}
    """
    
    # Get AI response
    response = get_response(full_prompt)
    
    # Judge if injection succeeded
    eval_result = evaluate_prompt_injection(
        system_task=item["system_task"],
        injected_content=item["injected_content"],
        response=response
    )
    
    result = log_result(
        prompt=item["system_task"],
        response=response,
        category=eval_result["category"],
        score=eval_result["score"],
        passed=eval_result["passed"]
    )
    result["judge_reasoning"] = eval_result.get("judge_reasoning", "")
    result["injected"] = eval_result.get("injected", False)
    results.append(result)

# ─────────────────────────────────────────
# PART 6: RED TEAMING LOOP
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