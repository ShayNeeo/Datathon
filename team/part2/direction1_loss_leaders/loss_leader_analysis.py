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
OUT = Path(r"c:\Users\TRIDELL\Desktop\vinuni\part2\direction1_loss_leaders")

print("Loading data...")
products = pd.read_csv(DATA / "products.csv")
order_items = pd.read_csv(DATA / "order_items.csv", low_memory=False)

# Identify Loss Leaders
products['margin'] = (products['price'] - products['cogs']) / products['price']
loss_leader_ids = products[products['margin'] <= 0.055]['product_id'].unique()

# Map loss leader flag to items
order_items['is_loss_leader'] = order_items['product_id'].isin(loss_leader_ids)
order_items['item_revenue'] = order_items['quantity'] * order_items['unit_price'] - order_items['discount_amount'].fillna(0)

# Merge COGS to calculate item profit
order_items = order_items.merge(products[['product_id', 'cogs']], on='product_id', how='left')
order_items['item_profit'] = order_items['item_revenue'] - (order_items['quantity'] * order_items['cogs'])

# Aggregate at Order Level
order_stats = order_items.groupby('order_id').agg(
    has_loss_leader=('is_loss_leader', 'max'),
    total_revenue=('item_revenue', 'sum'),
    total_profit=('item_profit', 'sum'),
    total_items=('quantity', 'sum')
).reset_index()

# Filter out edge cases
order_stats = order_stats[order_stats['total_revenue'] > 0]

# Calculate metrics
grp = order_stats.groupby('has_loss_leader').agg(
    avg_basket_value=('total_revenue', 'mean'),
    avg_profit=('total_profit', 'mean'),
    avg_items=('total_items', 'mean'),
    order_count=('order_id', 'count')
)

# --- Plotting ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

labels = ['Standard Orders\n(No Loss Leaders)', 'Loss Leader Orders\n(Contains <=5.5% Margin Item)']
colors = ['#93FA64', '#EF4444']
x = np.arange(len(labels))

# Plot 1: Average Basket Value & Profit
width = 0.35
ax1.bar(x - width/2, grp['avg_basket_value'], width, label='Avg Basket Revenue', color='#1E293B', alpha=0.8)
ax1.bar(x + width/2, grp['avg_profit'], width, label='Avg Basket Profit', color=['#93FA64', '#EF4444'], alpha=0.9)

for i in range(2):
    ax1.text(x[i] - width/2, grp['avg_basket_value'].iloc[i] + 1000, f"{grp['avg_basket_value'].iloc[i]:,.0f}₫", ha='center', fontweight='bold', fontsize=10)
    profit_val = grp['avg_profit'].iloc[i]
    y_offset = 1000 if profit_val > 0 else -3000
    ax1.text(x[i] + width/2, profit_val + y_offset, f"{profit_val:,.0f}₫", ha='center', fontweight='bold', fontsize=10, color='black' if profit_val > 0 else '#EF4444')

ax1.axhline(0, color='black', linewidth=1)
ax1.set_xticks(x)
ax1.set_xticklabels(labels, fontweight='bold')
ax1.set_ylabel("VND")
ax1.set_title("The Profitability Illusion: Revenue vs Actual Profit", fontweight='bold', pad=15)
ax1.legend(loc='upper right')

# Annotate insight
ax1.annotate(f"CRITICAL FAILURE:\nLoss leader orders DESTROY profit\n({grp['avg_profit'].iloc[1]:,.0f}₫ avg loss)", 
             xy=(1 + width/2, grp['avg_profit'].iloc[1]), 
             xytext=(0.5, 10000),
             arrowprops=dict(arrowstyle="->", color="#DC2626", lw=2),
             color="#DC2626", fontweight="bold", ha="center",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#FEE2E2", edgecolor="#DC2626"))

# Plot 2: Average Items per Cart
ax2.bar(x, grp['avg_items'], color=colors, alpha=0.8, width=0.5)
for i in range(2):
    ax2.text(x[i], grp['avg_items'].iloc[i] + 0.1, f"{grp['avg_items'].iloc[i]:.1f} items", ha='center', fontweight='bold', fontsize=11)

ax2.set_xticks(x)
ax2.set_xticklabels(labels, fontweight='bold')
ax2.set_ylabel("Quantity")
ax2.set_title("Cross-Selling Impact (Items per Cart)", fontweight='bold', pad=15)

ax2.annotate("Slight increase in basket size (+0.2 items)...\nbut NOT enough to offset the margin loss!",
             xy=(1, grp['avg_items'].iloc[1]), xytext=(0.5, 6),
             arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.5),
             ha='center', fontsize=9, color="#DC2626", fontweight="bold")

fig.suptitle("The 'Loss Leader' Trap: Operational Bleeding\nSacrificing margin to drive volume is actively harming bottom-line profitability", 
             fontsize=15, fontweight='bold', y=1.05)
fig.tight_layout()
fig.savefig(OUT / "loss_leader_trap.png")
print("Saved chart to loss_leader_trap.png")
