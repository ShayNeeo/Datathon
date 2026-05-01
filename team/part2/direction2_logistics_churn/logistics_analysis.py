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
OUT = Path(r"c:\Users\TRIDELL\Desktop\vinuni\part2\direction2_logistics_churn")

print("Loading data...")
orders = pd.read_csv(DATA / "orders.csv", parse_dates=['order_date'])
shipments = pd.read_csv(DATA / "shipments.csv", parse_dates=['ship_date', 'delivery_date'])

# 1. Delivery Delay Calculation
df_ship = orders[['order_id', 'customer_id', 'order_date']].merge(shipments[['order_id', 'delivery_date']], on='order_id', how='inner')
df_ship['delivery_days'] = (df_ship['delivery_date'] - df_ship['order_date']).dt.days

# Clean up anomalies
df_ship = df_ship[(df_ship['delivery_days'] >= 0) & (df_ship['delivery_days'] <= 14)]

# 2. Customer Repurchase Analysis
df_ship = df_ship.sort_values(['customer_id', 'order_date'])
df_ship['order_rank'] = df_ship.groupby('customer_id').cumcount() + 1

first_orders = df_ship[df_ship['order_rank'] == 1].copy()
cust_order_counts = df_ship.groupby('customer_id').size()
first_orders['has_repurchased'] = first_orders['customer_id'].map(lambda x: 1 if cust_order_counts[x] > 1 else 0)

# Group by Delivery Days
bins = [-1, 3, 6, 9, 14]
labels = ['1-3 days\n(Fast)', '4-6 days\n(Standard)', '7-9 days\n(Delayed)', '10-14 days\n(Late)']
first_orders['delivery_tier'] = pd.cut(first_orders['delivery_days'], bins=bins, labels=labels)

tier_stats = first_orders.groupby('delivery_tier', observed=False).agg(
    total_customers=('customer_id', 'count'),
    repurchased=('has_repurchased', 'sum')
).reset_index()

tier_stats['repurchase_rate'] = (tier_stats['repurchased'] / tier_stats['total_customers']) * 100

# --- Plotting ---
fig, ax = plt.subplots(figsize=(12, 6))

colors = ['#334155', '#334155', '#334155', '#334155']
bars = ax.bar(tier_stats['delivery_tier'], tier_stats['repurchase_rate'], color=colors, alpha=0.85, width=0.6)

for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{yval:.1f}%", ha='center', fontweight='bold', fontsize=11)

# Annotate trend
ax.plot(tier_stats['delivery_tier'], tier_stats['repurchase_rate'], color='#F59E0B', marker='o', lw=3, zorder=5)

ax.set_ylabel("Repurchase Probability (%)", fontsize=12)
ax.set_title("The 'Inelastic' Logistics Paradox: Customers Don't Care About Shipping Speed!\nRepurchase rates remain firmly at ~74% regardless of whether delivery takes 2 days or 14 days", 
             fontsize=14, fontweight='bold', pad=15)
ax.set_ylim(0, 100)

ax.annotate("Counter-Intuitive Insight:\nWe might be overspending on premium/fast logistics.\nCustomers are highly patient/loyal.", 
             xy=(2.5, 80), 
             xytext=(1.5, 90),
             arrowprops=dict(arrowstyle="->", color="#4ADE80", lw=2),
             color="#4ADE80", fontweight="bold", ha="center",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#ECFDF5", edgecolor="#4ADE80"))

fig.savefig(OUT / "logistics_loyalty_paradox.png")
print("Saved chart to logistics_loyalty_paradox.png")
