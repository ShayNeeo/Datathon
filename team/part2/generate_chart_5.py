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
c_base = "#93fa64"        # Vibrant Green (Hero color)
c_pastel_light = "#dcfce7" 
c_pastel_mid = "#86efac"   
c_dark_accent = "#166534"  
c_alert = "#fca5a5"        
c_alert_dark = "#991b1b"   
c_neutral = "#94a3b8"      

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

print("Generating Chart 5: Campaign ROI...")
promo = pd.read_csv(DATA / 'promotions.csv', parse_dates=['start_date', 'end_date'])
sales = pd.read_csv(DATA / 'sales.csv', parse_dates=['Date'])

def get_type(name):
    if 'Spring' in name: return 'Spring Sale'
    if 'Mid-Year' in name: return 'Mid-Year Sale'
    if 'Fall' in name: return 'Fall Launch'
    if 'Year-End' in name: return 'Year-End Sale'
    return 'Other'

promo['type'] = promo['promo_name'].apply(get_type)
sales['margin'] = (sales['Revenue'] - sales['COGS']) / sales['Revenue']

res = []
for p_type in ['Spring Sale', 'Mid-Year Sale', 'Fall Launch', 'Year-End Sale']:
    p_df = promo[promo['type'] == p_type]
    promo_days = set()
    for _, row in p_df.iterrows():
        promo_days.update(pd.date_range(row['start_date'], row['end_date']))
    
    in_promo = sales[sales['Date'].isin(promo_days)]
    out_promo = sales[~sales['Date'].isin(promo_days)]
    
    lift = (in_promo['Revenue'].mean() - out_promo['Revenue'].mean()) / out_promo['Revenue'].mean() * 100
    margin = in_promo['margin'].mean() * 100
    res.append({'Campaign': p_type, 'Lift': lift, 'Margin': margin})

df = pd.DataFrame(res)

fig, ax1 = plt.subplots(figsize=(12, 6))

# Bar chart for Lift
colors = [c_base if val > 0 else c_alert for val in df['Lift']]
bars = sns.barplot(x='Campaign', y='Lift', data=df, ax=ax1, palette=colors, edgecolor=c_dark_accent, linewidth=1.5, hue='Campaign', legend=False)

for i, bar in enumerate(ax1.patches):
    yval = bar.get_height()
    offset = 2 if yval > 0 else -4
    ax1.text(bar.get_x() + bar.get_width()/2, yval + offset, f"{yval:+.1f}%", ha='center', fontweight='bold', fontsize=12, color=c_dark_accent if yval > 0 else c_alert_dark)

ax1.set_ylabel("Revenue Lift (%)")
ax1.set_xlabel("")
ax1.axhline(0, color=c_dark_accent, linewidth=1.5, linestyle='--')

# Line chart for Margin
ax2 = ax1.twinx()
ax2.plot(df.index, df['Margin'], color=c_dark_accent, marker='D', markersize=10, lw=3, label='Gross Margin (%)')
for i, val in enumerate(df['Margin']):
    ax2.text(i, val + 0.8, f"Margin:\n{val:.1f}%", ha='center', fontweight='bold', color=c_dark_accent, fontsize=10)

ax2.set_ylabel("Gross Margin (%)", color=c_dark_accent)
ax2.set_ylim(0, 15)
ax2.grid(False)

plt.title("Campaign ROI & Trade-offs\nSpring Sale wins big, Year-End Sale is a double disaster", pad=20)

annotate_chart(ax1, "'YEAR-END' DISASTER:\nRevenue drops 46%,\nGross margin is squeezed to 1.5%!\nThis campaign is destroying value.", 
               xy=(3, df['Lift'].iloc[3]), xytext=(2.8, -20), color=c_alert_dark, arrow_color=c_alert_dark)

annotate_chart(ax1, "'SPRING SALE' BRIGHT SPOT:\nRevenue grows 44% while\nstill keeping 10.5% margin.", 
               xy=(0, df['Lift'].iloc[0]), xytext=(1.2, 38), color=c_dark_accent, arrow_color=c_base)

plt.savefig(OUT / "5_campaign_roi.png")
plt.close()
print("Chart 5 generated!")
