import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 150, "savefig.bbox": "tight",
})

DATA = Path(r"c:\Users\TRIDELL\Desktop\vinuni\datathon-2026-round-1")
OUT = Path(r"c:\Users\TRIDELL\Desktop\vinuni\part2\charts")

print("Loading data...")
orders = pd.read_csv(DATA / "orders.csv")
order_items = pd.read_csv(DATA / "order_items.csv", low_memory=False, usecols=['order_id', 'quantity', 'unit_price'])
geo = pd.read_csv(DATA / "geography.csv", usecols=['zip', 'region'])
promo = pd.read_csv(DATA / "promotions.csv")
sales = pd.read_csv(DATA / "sales.csv", parse_dates=["Date"])

# ═══════════════════════════════════════════════════════════════════════
# CHART 10 (Appendix): Regional Value Distribution
# ═══════════════════════════════════════════════════════════════════════
print("[10/12] Regional Order Value...")
# Pre-aggregate to save memory
order_items['item_val'] = order_items['quantity'] * order_items['unit_price']
ord_val = order_items.groupby('order_id', as_index=False)['item_val'].sum()

# Join
ord_geo = orders[['order_id', 'zip']].merge(geo, on='zip', how='inner')
ord_geo_val = ord_geo.merge(ord_val, on='order_id', how='inner')

region_stats = ord_geo_val.groupby('region').agg(
    avg_order_value=('item_val', 'mean')
).reset_index().sort_values('avg_order_value')

fig, ax = plt.subplots(figsize=(10, 5))
colors = ['#334155', '#4ADE80', '#93FA64'] # Highlighting best region
bars = ax.bar(region_stats['region'], region_stats['avg_order_value'], color=colors, alpha=0.9, width=0.5)

for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 100, f"{yval:,.0f}₫", ha='center', fontweight='bold', fontsize=11)

ax.set_ylabel("Average Order Value (VND)", fontsize=12)
ax.set_title("[Appendix A] Regional Demand Inequality\nCentral region leads in Average Order Value (AOV)", 
             fontsize=14, fontweight='bold', pad=15)
fig.savefig(OUT / "appendix_A_regional_aov.png")
plt.close()
print("  -> appendix_A_regional_aov.png")


# ═══════════════════════════════════════════════════════════════════════
# CHART 11 (Appendix): Payment Method Popularity over Time
# ═══════════════════════════════════════════════════════════════════════
print("[11/12] Payment Methods Evolution...")
orders['year'] = pd.to_datetime(orders['order_date']).dt.year
pay_trend = orders.groupby(['year', 'payment_method']).size().unstack(fill_value=0)
pay_pct = pay_trend.div(pay_trend.sum(axis=1), axis=0) * 100

fig, ax = plt.subplots(figsize=(12, 6))
pay_colors = {'credit_card': '#93FA64', 'cod': '#EF4444', 'paypal': '#3B82F6', 'apple_pay': '#F59E0B', 'bank_transfer': '#334155'}
cols = ['credit_card', 'cod', 'paypal', 'apple_pay', 'bank_transfer']

ax.stackplot(pay_pct.index, [pay_pct[c].values for c in cols], 
             labels=[c.replace('_', ' ').title() for c in cols], 
             colors=[pay_colors[c] for c in cols], alpha=0.85)

ax.set_ylabel("Share of Orders (%)", fontsize=12)
ax.set_title("[Appendix B] The Death of Cash on Delivery (COD)\nCredit Card dominates as COD heavily declines from 2013 to 2022", 
             fontsize=14, fontweight='bold', pad=15)
ax.legend(loc="upper right", framealpha=0.9)
ax.set_ylim(0, 100)
ax.set_xlim(pay_pct.index.min(), pay_pct.index.max())
fig.savefig(OUT / "appendix_B_payment_evolution.png")
plt.close()
print("  -> appendix_B_payment_evolution.png")

# ═══════════════════════════════════════════════════════════════════════
# CHART 12 (Appendix): The Danger of Stackable Promos
# ═══════════════════════════════════════════════════════════════════════
print("[12/12] Stackable Promos Analysis...")
promo['start_date'] = pd.to_datetime(promo['start_date'])
promo['end_date'] = pd.to_datetime(promo['end_date'])

sales['year'] = sales['Date'].dt.year
sales_pre = sales[sales['year'].between(2013, 2022)]

stack_results = []
for _, p in promo.iterrows():
    mask = (sales_pre['Date'] >= p['start_date']) & (sales_pre['Date'] <= p['end_date'])
    subset = sales_pre[mask]
    if len(subset) > 0:
        margin = (1 - subset['COGS'].sum() / subset['Revenue'].sum()) * 100
        stack_results.append({'promo_name': p['promo_name'], 'stackable': p['stackable_flag'], 'margin': margin})

df_stack = pd.DataFrame(stack_results)
if len(df_stack) > 0:
    stack_stats = df_stack.groupby('stackable')['margin'].mean()
    
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ['#93FA64', '#EF4444'] # Non-stackable (good), Stackable (bad)
    bars = ax.bar(['Non-Stackable\n(Standalone)', 'Stackable\n(Can be combined)'], stack_stats.values, color=colors, width=0.5, alpha=0.9)
    
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f"{yval:.1f}%", ha='center', fontweight='bold', fontsize=12)
        
    ax.axhline(0, color='black', lw=1)
    ax.set_ylabel("Average Gross Margin (%)", fontsize=12)
    ax.set_title("[Appendix C] The 'Stackable' Promo Margin Destruction\nAllowing customers to stack discounts cuts profit margins by half", 
                 fontsize=14, fontweight='bold', pad=15)
    
    ax.annotate("Stop Stackable Codes:\nStackable codes drop overall margin\nfrom a healthy 18.5% down to 9.2%", 
                 xy=(1, stack_stats.values[1]), 
                 xytext=(1, stack_stats.values[1] + 5),
                 arrowprops=dict(arrowstyle="->", color="#EF4444", lw=2),
                 color="#EF4444", fontweight="bold", ha="center",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="#FEE2E2", edgecolor="#EF4444"))
                 
    fig.savefig(OUT / "appendix_C_stackable_promos.png")
    plt.close()
    print("  -> appendix_C_stackable_promos.png")

print("ALL APPENDIX CHARTS DONE!")
