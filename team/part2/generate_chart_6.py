import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

# --- AESTHETIC SETTINGS ---
sns.set_theme(style="whitegrid", font="sans-serif")
c_base = "#93fa64"        # Vibrant Green
c_pastel_mid = "#86efac"   
c_dark_accent = "#166534"  
c_alert = "#fca5a5"        
c_alert_dark = "#991b1b"   

plt.rcParams.update({
    "font.size": 12, "axes.titlesize": 16, "axes.titleweight": "bold",
    "axes.labelsize": 12, "axes.labelweight": "bold", "axes.labelcolor": c_dark_accent,
    "xtick.color": c_dark_accent, "ytick.color": c_dark_accent, "text.color": c_dark_accent,
    "figure.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.3,
    "axes.edgecolor": "#cbd5e1", "axes.linewidth": 1.5, "grid.color": "#f1f5f9",
})

DATA = Path(r"c:\Users\TRIDELL\Desktop\vinuni\datathon-2026-round-1")
OUT = Path(r"c:\Users\TRIDELL\Desktop\vinuni\part2\charts_final")
os.makedirs(OUT, exist_ok=True)

def annotate_chart(ax, text, xy, xytext, color, arrow_color):
    ax.annotate(text, xy=xy, xytext=xytext,
                arrowprops=dict(arrowstyle="->", color=arrow_color, lw=2, connectionstyle="arc3,rad=0.1"),
                color=color, fontweight="bold", ha="center", fontsize=11,
                bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor=color, alpha=0.9, lw=1.5))

print("Generating Chart 6: Loyalty Collapse...")
orders = pd.read_csv(DATA / 'orders.csv', usecols=['customer_id', 'order_date'], parse_dates=['order_date'])

cust_first = orders.groupby('customer_id')['order_date'].min().reset_index()
cust_first['cohort_year'] = cust_first['order_date'].dt.year
orders = orders.merge(cust_first[['customer_id', 'cohort_year']], on='customer_id')
orders['order_year'] = orders['order_date'].dt.year

res = []
for y in range(2012, 2022):
    cohort = cust_first[cust_first['cohort_year'] == y]['customer_id']
    retained = orders[(orders['customer_id'].isin(cohort)) & (orders['order_year'] == y + 1)]['customer_id'].nunique()
    retention_rate = (retained / len(cohort)) * 100
    res.append({'Cohort': y, 'Retention': retention_rate, 'Acquired': len(cohort)})

df = pd.DataFrame(res)

fig, ax1 = plt.subplots(figsize=(12, 6))

# Area chart for Retention Rate
ax1.fill_between(df['Cohort'], df['Retention'], color=c_alert, alpha=0.3)
ax1.plot(df['Cohort'], df['Retention'], color=c_alert_dark, marker='o', lw=3, markersize=8, label="Next-year Retention Rate (%)")

for i, row in df.iterrows():
    ax1.text(row['Cohort'], row['Retention'] + 2, f"{row['Retention']:.1f}%", ha='center', fontweight='bold', color=c_alert_dark)

ax1.set_ylabel("Customer Retention Rate (%)", color=c_alert_dark)
ax1.set_ylim(0, 80)
ax1.set_xticks(df['Cohort'])
ax1.grid(True, linestyle='--', alpha=0.5)

# Bar chart for Cohort Size (Acquisition)
ax2 = ax1.twinx()
ax2.bar(df['Cohort'], df['Acquired'], color=c_pastel_mid, alpha=0.4, width=0.6, edgecolor=c_dark_accent, label="New Customer Volume (Acquisition)")
ax2.set_ylabel("New Customer Count", color=c_dark_accent)
ax2.set_ylim(0, df['Acquired'].max() * 2)
ax2.grid(False)

plt.title("The Retention Crisis (Loyalty Collapse)\nNew customer acquisition rises rapidly, but retention falls sharply", pad=20)

annotate_chart(ax1, "GOLDEN ERA:\nEarly customers (2012-2014)\nwere highly loyal (>35%).\nFocus on quality.", 
               xy=(2013, df[df['Cohort']==2013]['Retention'].values[0]), xytext=(2014.5, 60), color=c_dark_accent, arrow_color=c_dark_accent)

annotate_chart(ax1, "RED ALERT:\nModern cohorts (2018-2021)\nnearly buy once and leave (<10%).\nLTV is evaporating badly!", 
               xy=(2019, df[df['Cohort']==2019]['Retention'].values[0]), xytext=(2018, 30), color=c_alert_dark, arrow_color=c_alert_dark)

# Combine legends
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right', frameon=True, facecolor='white')

plt.savefig(OUT / "6_loyalty_collapse.png")
plt.close()
print("Chart 6 generated!")
