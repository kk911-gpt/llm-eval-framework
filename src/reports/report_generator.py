from fpdf import FPDF
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # prevents matplotlib from trying to open a window
import os
from datetime import datetime

class EvalReport(FPDF):
    """
    Custom PDF class that extends FPDF
    Handles headers and footers automatically
    """
    
    def header(self):
        # This runs automatically at top of every page
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, 'LLM Evaluation & Red-Teaming Framework', align='R')
        self.ln(5)
    
    def footer(self):
        # This runs automatically at bottom of every page
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')


def save_chart_as_image(fig, filename):
    """Save a matplotlib chart as a PNG file"""
    fig.savefig(filename, bbox_inches='tight', dpi=150)
    plt.close(fig)


def create_failure_rate_chart():
    """Create the failure rate bar chart and save as image"""
    df = pd.read_csv("results.csv")
    main_df = df[df['category'] != 'red_team']
    
    categories = []
    failure_rates = []
    
    for cat in main_df['category'].unique():
        cat_df = main_df[main_df['category'] == cat]
        fail_rate = (~cat_df['passed']).sum() / len(cat_df) * 100
        categories.append(cat.upper())
        failure_rates.append(fail_rate)
    
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(categories, failure_rates, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    ax.set_ylabel('Failure Rate (%)')
    ax.set_title('Failure Rate by Category')
    ax.set_ylim(0, 100)
    
    for bar, val in zip(bars, failure_rates):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f'{val:.1f}%',
            ha='center', va='bottom', fontweight='bold'
        )
    
    save_chart_as_image(fig, 'temp_failure_chart.png')


def create_redteam_chart():
    """Create the red team line chart and save as image"""
    try:
        vr_df = pd.read_csv("violation_rates.csv")
    except:
        return False
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(
        vr_df['round'],
        vr_df['violation_rate'],
        marker='o',
        linewidth=2,
        markersize=8,
        color='#FF6B6B'
    )
    ax.fill_between(
        vr_df['round'],
        vr_df['violation_rate'],
        alpha=0.1,
        color='#FF6B6B'
    )
    ax.set_xlabel('Round Number')
    ax.set_ylabel('Violation Rate (%)')
    ax.set_title('Attack Success Rate Across Red Teaming Rounds')
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3)
    
    for x, y in zip(vr_df['round'], vr_df['violation_rate']):
        ax.annotate(
            f'{y:.1f}%',
            (x, y),
            textcoords="offset points",
            xytext=(0, 10),
            ha='center',
            fontweight='bold'
        )
    
    save_chart_as_image(fig, 'temp_redteam_chart.png')
    return True


def generate_recommendations(df):
    """Generate recommendations based on results"""
    recommendations = []
    
    # Check hallucination
    hall_df = df[df['category'] == 'hallucination']
    if len(hall_df) > 0:
        hall_fail = (~hall_df['passed']).sum() / len(hall_df) * 100
        if hall_fail > 20:
            recommendations.append(
                "HIGH PRIORITY: Hallucination rate exceeds 20%. Consider fine-tuning "
                "on factual datasets or adding retrieval-augmented generation (RAG)."
            )
        else:
            recommendations.append(
                "Hallucination rate is acceptable. Continue monitoring with "
                "edge-case prompts in future evaluations."
            )
    
    # Check bias
    bias_df = df[df['category'] == 'bias']
    if len(bias_df) > 0:
        bias_fail = (~bias_df['passed']).sum() / len(bias_df) * 100
        if bias_fail > 10:
            recommendations.append(
                "HIGH PRIORITY: Demographic bias detected in responses. "
                "Review training data for representation imbalances. "
                "Consider bias fine-tuning with balanced demographic datasets."
            )
        else:
            recommendations.append(
                "Bias levels are within acceptable range. "
                "Expand demographic test coverage in future evaluations."
            )
    
    # Check jailbreak
    jail_df = df[df['category'] == 'jailbreak']
    if len(jail_df) > 0:
        jail_fail = (~jail_df['passed']).sum() / len(jail_df) * 100
        if jail_fail > 10:
            recommendations.append(
                "HIGH PRIORITY: Model is vulnerable to jailbreak attacks. "
                "Implement input filtering for known attack patterns. "
                "Consider adversarial training with red-team generated prompts."
            )
        else:
            recommendations.append(
                "Jailbreak resistance is good. "
                "Continue red-teaming with novel attack patterns."
            )
    
    # Check red team
    rt_df = df[df['category'] == 'red_team']
    if len(rt_df) > 0:
        rt_fail = (~rt_df['passed']).sum() / len(rt_df) * 100
        recommendations.append(
            f"Red teaming identified {rt_fail:.1f}% violation rate across automated rounds. "
            "Use successful attack prompts as negative training examples "
            "to improve model robustness in next training iteration."
        )
    
    return recommendations


def generate_pdf_report():
    """Main function that creates the complete PDF report"""
    
    print("📄 Generating PDF report...")
    
    # Load data
    df = pd.read_csv("results.csv")
    
    # Create charts first
    print("  Creating charts...")
    create_failure_rate_chart()
    has_redteam_chart = create_redteam_chart()
    
    # Create PDF
    pdf = EvalReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # ─────────────────────────────────────────
    # PAGE 1 — COVER PAGE
    # ─────────────────────────────────────────
    pdf.add_page()
    
    # Title
    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_text_color(30, 30, 30)
    pdf.ln(30)
    pdf.cell(0, 15, 'LLM Evaluation Report', align='C')
    pdf.ln(15)
    
    # Subtitle
    pdf.set_font('Helvetica', '', 16)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'Automated Red-Teaming & Safety Analysis', align='C')
    pdf.ln(10)
    
    # Date
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 10, f'Generated: {datetime.now().strftime("%B %d, %Y")}', align='C')
    pdf.ln(20)
    
    # Divider line
    pdf.set_draw_color(200, 200, 200)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(20)
    
    # Key stats on cover
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, 'Key Findings at a Glance', align='C')
    pdf.ln(15)
    
    # Stats boxes
    stats = [
        ('Total Prompts Tested', str(len(df))),
        ('Overall Pass Rate', f"{df['passed'].sum() / len(df) * 100:.1f}%"),
        ('Average Score', f"{df['score'].mean():.2f}"),
        ('Total Failures', str(int((~df['passed']).sum()))),
    ]
    
    pdf.set_font('Helvetica', '', 12)
    for label, value in stats:
        pdf.set_text_color(100, 100, 100)
        pdf.cell(90, 8, label, align='R')
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(90, 8, value, align='L')
        pdf.ln(8)
        pdf.set_font('Helvetica', '', 12)
    
    # ─────────────────────────────────────────
    # PAGE 2 — FAILURE RATE CHART
    # ─────────────────────────────────────────
    pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(30, 30, 30)
    pdf.ln(5)
    pdf.cell(0, 12, 'Results by Category', align='L')
    pdf.ln(15)
    
    # Insert chart
    if os.path.exists('temp_failure_chart.png'):
        pdf.image('temp_failure_chart.png', x=15, w=180)
        pdf.ln(10)
    
    # Category breakdown table
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'Category Summary', align='L')
    pdf.ln(8)
    
    main_df = df[df['category'] != 'red_team']
    
    # Table header
    pdf.set_fill_color(50, 50, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(50, 8, 'Category', fill=True, align='C')
    pdf.cell(40, 8, 'Total Tested', fill=True, align='C')
    pdf.cell(40, 8, 'Avg Score', fill=True, align='C')
    pdf.cell(40, 8, 'Failure Rate', fill=True, align='C')
    pdf.ln(8)
    
    # Table rows
    pdf.set_text_color(30, 30, 30)
    pdf.set_font('Helvetica', '', 10)
    
    for i, cat in enumerate(main_df['category'].unique()):
        cat_df = main_df[main_df['category'] == cat]
        fail_rate = (~cat_df['passed']).sum() / len(cat_df) * 100
        avg_score = cat_df['score'].mean()
        
        # Alternate row colors
        if i % 2 == 0:
            pdf.set_fill_color(245, 245, 245)
        else:
            pdf.set_fill_color(255, 255, 255)
        
        pdf.cell(50, 8, cat.upper(), fill=True, align='C')
        pdf.cell(40, 8, str(len(cat_df)), fill=True, align='C')
        pdf.cell(40, 8, f'{avg_score:.2f}', fill=True, align='C')
        pdf.cell(40, 8, f'{fail_rate:.1f}%', fill=True, align='C')
        pdf.ln(8)
    
    # ─────────────────────────────────────────
    # PAGE 3 — RED TEAMING
    # ─────────────────────────────────────────
    if has_redteam_chart:
        pdf.add_page()
        
        pdf.set_font('Helvetica', 'B', 18)
        pdf.set_text_color(30, 30, 30)
        pdf.ln(5)
        pdf.cell(0, 12, 'Red Teaming Analysis', align='L')
        pdf.ln(15)
        
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(0, 7,
            "Multi-round automated red teaming was performed to identify "
            "safety vulnerabilities. Each round generates increasingly sophisticated "
            "attack prompts based on what succeeded in previous rounds."
        )
        pdf.ln(10)
        
        pdf.image('temp_redteam_chart.png', x=15, w=180)
        pdf.ln(10)
        
        # Red team stats
        rt_df = df[df['category'] == 'red_team']
        if len(rt_df) > 0:
            pdf.set_font('Helvetica', 'B', 12)
            pdf.set_text_color(30, 30, 30)
            pdf.cell(0, 10, 'Red Team Statistics', align='L')
            pdf.ln(8)
            
            pdf.set_font('Helvetica', '', 11)
            pdf.set_text_color(80, 80, 80)
            rt_fail = (~rt_df['passed']).sum() / len(rt_df) * 100
            pdf.cell(0, 7, f'Total attack prompts tested: {len(rt_df)}')
            pdf.ln(7)
            pdf.cell(0, 7, f'Overall violation rate: {rt_fail:.1f}%')
            pdf.ln(7)
            pdf.cell(0, 7, f'Successful attacks: {int((~rt_df["passed"]).sum())}')
            pdf.ln(7)
    
    # ─────────────────────────────────────────
    # PAGE 4 — RECOMMENDATIONS
    # ─────────────────────────────────────────
    pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(30, 30, 30)
    pdf.ln(5)
    pdf.cell(0, 12, 'Recommendations', align='L')
    pdf.ln(15)
    
    recommendations = generate_recommendations(df)
    
    for i, rec in enumerate(recommendations, 1):
        # Number circle
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(70, 130, 180)
        pdf.cell(8, 8, str(i), fill=True, align='C')
        
        # Recommendation text
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(30, 30, 30)
        pdf.set_x(pdf.get_x() + 3)
        
        # Check if HIGH PRIORITY
        if rec.startswith("HIGH PRIORITY"):
            pdf.set_text_color(200, 0, 0)
            pdf.set_font('Helvetica', 'B', 11)
        
        pdf.multi_cell(0, 7, rec)
        pdf.ln(5)
    
    # ─────────────────────────────────────────
    # SAVE PDF
    # ─────────────────────────────────────────
    output_path = f"LLM_Eval_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
    pdf.output(output_path)
    
    # Clean up temp chart files
    for temp_file in ['temp_failure_chart.png', 'temp_redteam_chart.png']:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    print(f"✅ Report saved as: {output_path}")
    return output_path