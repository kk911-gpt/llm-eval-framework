import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="LLM Eval Framework",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 LLM Evaluation & Red-Teaming Framework")
st.markdown("Automated testing for hallucination, bias, and jailbreak failures")

# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────
try:
    df = pd.read_csv("results.csv")
except:
    st.error("No results found. Run main.py first.")
    st.stop()

try:
    vr_df = pd.read_csv("violation_rates.csv")
    has_redteam = True
except:
    has_redteam = False

# ─────────────────────────────────────────
# TOP METRICS
# ─────────────────────────────────────────
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Prompts Tested", len(df))
with col2:
    overall_pass = f"{df['passed'].sum() / len(df) * 100:.1f}%"
    st.metric("Overall Pass Rate", overall_pass)
with col3:
    st.metric("Average Score", f"{df['score'].mean():.2f}")
with col4:
    st.metric("Total Failures", int((~df['passed']).sum()))

# ─────────────────────────────────────────
# CATEGORY CHARTS
# ─────────────────────────────────────────
st.markdown("---")
st.subheader("📊 Results by Category")

col1, col2 = st.columns(2)

# Filter out red_team from category charts
main_df = df[df['category'] != 'red_team']

with col1:
    st.markdown("**Failure Rate by Category**")
    category_stats = []
    for cat in main_df['category'].unique():
        cat_df = main_df[main_df['category'] == cat]
        fail_rate = (~cat_df['passed']).sum() / len(cat_df) * 100
        category_stats.append({
            "category": cat.upper(),
            "failure_rate": fail_rate
        })
    stats_df = pd.DataFrame(category_stats)

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(
        stats_df['category'],
        stats_df['failure_rate'],
        color=['#FF6B6B', '#4ECDC4', '#45B7D1']
    )
    ax.set_ylabel("Failure Rate (%)")
    ax.set_title("Failure Rate by Category")
    ax.set_ylim(0, 100)
    for bar, val in zip(bars, stats_df['failure_rate']):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f'{val:.1f}%',
            ha='center', va='bottom', fontweight='bold'
        )
    st.pyplot(fig)

with col2:
    st.markdown("**Average Score by Category**")
    avg_scores = []
    for cat in main_df['category'].unique():
        cat_df = main_df[main_df['category'] == cat]
        avg_scores.append({
            "category": cat.upper(),
            "avg_score": cat_df['score'].mean()
        })
    avg_df = pd.DataFrame(avg_scores)

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    bars2 = ax2.bar(
        avg_df['category'],
        avg_df['avg_score'],
        color=['#FF6B6B', '#4ECDC4', '#45B7D1']
    )
    ax2.set_ylabel("Average Score (0-1)")
    ax2.set_title("Average Score by Category")
    ax2.set_ylim(0, 1)
    for bar, val in zip(bars2, avg_df['avg_score']):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f'{val:.2f}',
            ha='center', va='bottom', fontweight='bold'
        )
    st.pyplot(fig2)

# ─────────────────────────────────────────
# RED TEAM VIOLATION RATE CHART
# ─────────────────────────────────────────
if has_redteam:
    st.markdown("---")
    st.subheader("🔴 Red Teaming — Violation Rate Across Rounds")
    st.markdown("Shows how attack success rate changes as attacks get more sophisticated each round")

    fig3, ax3 = plt.subplots(figsize=(10, 4))
    ax3.plot(
        vr_df['round'],
        vr_df['violation_rate'],
        marker='o',
        linewidth=2,
        markersize=8,
        color='#FF6B6B'
    )
    ax3.fill_between(
        vr_df['round'],
        vr_df['violation_rate'],
        alpha=0.1,
        color='#FF6B6B'
    )
    ax3.set_xlabel("Round Number")
    ax3.set_ylabel("Violation Rate (%)")
    ax3.set_title("Attack Success Rate Across Red Teaming Rounds")
    ax3.set_xticks(vr_df['round'])
    ax3.set_ylim(0, 100)
    ax3.grid(True, alpha=0.3)

    for x, y in zip(vr_df['round'], vr_df['violation_rate']):
        ax3.annotate(
            f'{y:.1f}%',
            (x, y),
            textcoords="offset points",
            xytext=(0, 10),
            ha='center',
            fontweight='bold'
        )
    st.pyplot(fig3)

# ─────────────────────────────────────────
# DETAILED RESULTS TABLE
# ─────────────────────────────────────────
st.markdown("---")
st.subheader("📋 Detailed Results")

category_filter = st.selectbox(
    "Filter by category:",
    ["ALL"] + list(df['category'].unique())
)

filtered_df = df if category_filter == "ALL" else df[df['category'] == category_filter]

def highlight_row(row):
    if row['passed']:
        return ['background-color: #d4edda'] * len(row)
    else:
        return ['background-color: #f8d7da'] * len(row)

display_cols = ['category', 'prompt', 'score', 'passed']
st.dataframe(
    filtered_df[display_cols].style.apply(highlight_row, axis=1),
    use_container_width=True
)

# ─────────────────────────────────────────
# WORST PERFORMING
# ─────────────────────────────────────────
st.markdown("---")
st.subheader("⚠️ Worst Performing Prompts")
worst = df.nsmallest(5, 'score')[display_cols]
st.dataframe(worst, use_container_width=True)