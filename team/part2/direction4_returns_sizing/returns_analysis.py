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
OUT = Path(r"c:\Users\TRIDELL\Desktop\vinuni\part2\direction4_returns_sizing")

print("Loading data...")
products = pd.read_csv(DATA / "products.csv")
order_items = pd.read_csv(DATA / "order_items.csv", low_memory=False)
returns = pd.read_csv(DATA / "returns.csv")

# Find products with inconsistent pricing across sizes
products['brand_line'] = products['product_name'].str.extract(r'^(.*? [A-Z]{2})')[0]
price_consistency = products.groupby('brand_line')['price'].nunique().reset_index()
inconsistent_brand_lines = price_consistency[price_consistency['price'] > 1]['brand_line'].tolist()

products['is_inconsistent_pricing'] = products['brand_line'].isin(inconsistent_brand_lines)

# Merge returns with products
ret_prod = returns.merge(products, on='product_id', how='inner')

# Calculate total sales per category and segment to find return rate
sales_vol = order_items.merge(products[['product_id', 'category', 'segment', 'is_inconsistent_pricing']], on='product_id', how='left')
sales_by_cat = sales_vol.groupby('category').agg(total_qty_sold=('quantity', 'sum')).reset_index()

# Returns by category and reason
ret_by_cat = ret_prod.groupby(['category', 'return_reason']).agg(total_qty_returned=('return_quantity', 'sum')).reset_index()
ret_by_cat = ret_by_cat.merge(sales_by_cat, on='category', how='left')
ret_by_cat['return_rate_pct'] = (ret_by_cat['total_qty_returned'] / ret_by_cat['total_qty_sold']) * 100

# Focus on wrong_size
wrong_size_returns = ret_by_cat[ret_by_cat['return_reason'] == 'wrong_size'].sort_values('return_rate_pct', ascending=False)
print("Wrong Size Return Rates by Category:")
print(wrong_size_returns)

# Let's plot this return rate by category
fig, ax = plt.subplots(figsize=(10, 6))

colors = ['#EF4444' if cat == 'GenZ' else '#334155' for cat in wrong_size_returns['category']]
bars = ax.bar(wrong_size_returns['category'], wrong_size_returns['return_rate_pct'], color=colors, alpha=0.85, width=0.5)

for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 0.05, f"{yval:.2f}%", ha='center', fontweight='bold', fontsize=11)

ax.set_ylabel("Return Rate due to 'Wrong Size' (%)", fontsize=12)
ax.set_title("The 'GenZ' Fit Problem: Sizing Inconsistencies Drive Returns\nGenZ category suffers heavily from sizing-related returns compared to others", 
             fontsize=14, fontweight='bold', pad=15)

ax.annotate("Operational Bleeding:\nGenZ apparel requires immediate\nsize-chart standardization to reduce reverse logistics costs.", 
             xy=(0, wrong_size_returns['return_rate_pct'].iloc[0]), 
             xytext=(1.5, wrong_size_returns['return_rate_pct'].iloc[0] * 1.1),
             arrowprops=dict(arrowstyle="->", color="#EF4444", lw=2),
             color="#EF4444", fontweight="bold", ha="center",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#FEE2E2", edgecolor="#EF4444"))

fig.savefig(OUT / "wrong_size_returns.png")
print("Saved chart to wrong_size_returns.png")
