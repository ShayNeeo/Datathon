import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import os
import seaborn as sns

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 200, "savefig.bbox": "tight",
})

# --- COLOR PALETTE (Strictly Green Based on #93fa64) ---
base_green = "#93fa64"
dark_green1 = "#4ade80"
dark_green2 = "#22c55e"
dark_green3 = "#16a34a"
dark_green4 = "#15803d"
darkest_green = "#14532d"
light_green1 = "#bbf7d0"
light_green2 = "#dcfce7"
text_dark = "#064e3b" # Very dark green for text

DATA = Path(r"c:\Users\TRIDELL\Desktop\vinuni\datathon-2026-round-1")
OUT = Path(r"c:\Users\TRIDELL\Desktop\vinuni\part2\charts_final")
os.makedirs(OUT, exist_ok=True)

print("Loading Data...")
products = pd.read_csv(DATA / "products.csv")
# To avoid memory issues, sample or aggregate effectively
sales = pd.read_csv(DATA / "sales.csv", parse_dates=["Date"])

# ==============================================================================
# CHART 1: The Loss Leader Trap (Bait Trap - Negative Profit)
# Level: Diagnostic & Prescriptive
# ==============================================================================
print("Generating Chart 1: Loss Leader Trap...")
order_items = pd.read_csv(DATA / "order_items.csv", nrows=500000) # Read sample for speed if needed, but let's read full if possible
# Let's read full but only needed columns
order_items = pd.read_csv(DATA / "order_items.csv", usecols=['order_id', 'product_id', 'quantity', 'unit_price', 'discount_amount'])

products['margin_pct'] = (products['price'] - products['cogs']) / products['price']
# Define loss leader dynamically as bottom 10% margin products
threshold_margin = products['margin_pct'].quantile(0.10)
loss_leader_ids = products[products['margin_pct'] <= threshold_margin]['product_id'].unique()

order_items['is_loss_leader'] = order_items['product_id'].isin(loss_leader_ids)
order_items['discount_amount'] = order_items['discount_amount'].fillna(0)
order_items['item_revenue'] = order_items['quantity'] * order_items['unit_price'] - order_items['discount_amount']

# Merge COGS
order_items = order_items.merge(products[['product_id', 'cogs']], on='product_id', how='left')
order_items['item_profit'] = order_items['item_revenue'] - (order_items['quantity'] * order_items['cogs'])

order_stats = order_items.groupby('order_id').agg(
    has_loss_leader=('is_loss_leader', 'max'),
    total_revenue=('item_revenue', 'sum'),
    total_profit=('item_profit', 'sum'),
    total_items=('quantity', 'sum')
).reset_index()

grp = order_stats.groupby('has_loss_leader').agg(
    avg_revenue=('total_revenue', 'mean'),
    avg_profit=('total_profit', 'mean'),
    avg_items=('total_items', 'mean')
)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
labels = ['Standard Order\n(Safe Margin)', f'"Bait" Order\n(Contains Products w/ Margin <= {threshold_margin:.1%})']
x = np.arange(len(labels))
width = 0.35

ax1.bar(x - width/2, grp['avg_revenue'], width, label='Doanh thu TB', color=light_green1)
ax1.bar(x + width/2, grp['avg_profit'], width, label='Avg Profit', color=[base_green, darkest_green])

for i in range(2):
    ax1.text(x[i] - width/2, grp['avg_revenue'].iloc[i] + 1000, f"{grp['avg_revenue'].iloc[i]:,.0f}₫", ha='center', color=text_dark, fontweight='bold')
    p_val = grp['avg_profit'].iloc[i]
    y_off = 1000 if p_val > 0 else -15000
    ax1.text(x[i] + width/2, p_val + y_off, f"{p_val:,.0f}₫", ha='center', color=text_dark, fontweight='bold')

ax1.axhline(0, color=dark_green4, linewidth=1.5)
ax1.set_xticks(x)
ax1.set_xticklabels(labels, fontweight='bold', color=text_dark)
ax1.set_ylabel("VND", color=text_dark)
ax1.set_title("Revenue Illusion: High Revenue but Negative Profit", fontweight='bold', color=text_dark)
ax1.legend()

# Annotate
profit_diff = grp['avg_profit'].iloc[0] - grp['avg_profit'].iloc[1]
ax1.annotate(f"BUSINESS ALERT:\n'Bait' orders destroy cash flow\nAvg Loss {grp['avg_profit'].iloc[1]:,.0f} VND/order",
             xy=(1 + width/2, grp['avg_profit'].iloc[1]), xytext=(0.5, grp['avg_revenue'].max()*0.8),
             arrowprops=dict(arrowstyle="->", color=darkest_green, lw=2),
             ha="center", color=dark_green4, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.5", facecolor=light_green2, edgecolor=darkest_green))

# Items
ax2.bar(x, grp['avg_items'], width=0.5, color=[light_green1, base_green])
for i in range(2):
    ax2.text(x[i], grp['avg_items'].iloc[i] + 0.1, f"{grp['avg_items'].iloc[i]:.1f} SP", ha='center', color=text_dark, fontweight='bold')

ax2.set_xticks(x)
ax2.set_xticklabels(labels, fontweight='bold', color=text_dark)
ax2.set_title("Cross-selling Effect", fontweight='bold', color=text_dark)
ax2.annotate("Cross-sell VERY WEAK (+%.1f items)\nNot enough to cover costs!" % (grp['avg_items'].iloc[1] - grp['avg_items'].iloc[0]),
             xy=(1, grp['avg_items'].iloc[1]), xytext=(0.5, grp['avg_items'].max()*0.9),
             arrowprops=dict(arrowstyle="->", color=darkest_green, lw=2),
             ha="center", color=dark_green4, fontweight="bold")

fig.suptitle("The 'Loss Leader' Trap (Bait Products)\nSacrificing margin does not yield enough cross-sell volume", 
             fontsize=16, fontweight='bold', color=darkest_green, y=1.05)
plt.savefig(OUT / "1_loss_leader_trap.png")
plt.close()

# Free memory
del order_items, order_stats, grp

# ==============================================================================
# CHART 2: Tet Effect & The "Dead Zone"
# Level: Predictive
# ==============================================================================
print("Generating Chart 2: Tet Effect...")
pre_covid = sales[sales.Date.dt.year.between(2013, 2018)].copy()
tet_dates = {2013:"2013-02-10",2014:"2014-01-31",2015:"2015-02-19",2016:"2016-02-08",
             2017:"2017-01-28",2018:"2018-02-16"}

windows = []
for yr, tet_str in tet_dates.items():
    tet = pd.Timestamp(tet_str)
    for delta in range(-30, 31):
        d = tet + pd.Timedelta(days=delta)
        row = pre_covid[pre_covid.Date == d]
        if len(row) > 0:
            windows.append({"delta": delta, "revenue": row.Revenue.values[0]})

df_tet = pd.DataFrame(windows)
avg_tet = df_tet.groupby("delta")["revenue"].mean() / 1e6

fig, ax = plt.subplots(figsize=(14, 6))
# Colors: gradient of greens based on phase
colors = np.where(avg_tet.index < 0, dark_green3, np.where(avg_tet.index <= 7, light_green1, base_green))

ax.bar(avg_tet.index, avg_tet.values, color=colors, alpha=0.9, width=0.8)
baseline = pre_covid.Revenue.mean() / 1e6
ax.axhline(baseline, color=darkest_green, ls="--", lw=1.5)
ax.text(25, baseline + 0.5, f"Baseline: {baseline:.1f}M", fontsize=10, color=darkest_green, fontweight='bold')

# Annotations
phases_tet = [
    (-25, -1, "PRE-TET SHOPPING\n(Peak Demand)", dark_green4),
    (0, 7, "DEAD ZONE (TET)\n(Logistics Freeze)", darkest_green),
    (8, 20, "SLOW RECOVERY\n(Post-Tet)", dark_green3),
]
for s, e, label, color in phases_tet:
    mid = (s + e) / 2
    y_pos = avg_tet.max() * 0.9
    ax.annotate(label, xy=(mid, y_pos), fontsize=10, ha="center",
                fontweight="bold", color=text_dark,
                bbox=dict(boxstyle="round,pad=0.4", facecolor=light_green2, edgecolor=color, alpha=0.9))
    ax.axvspan(s-0.5, e+0.5, alpha=0.15, color=color)

ax.set_xlabel("Days relative to Tet New Year (Day 0)", fontsize=12, color=text_dark, fontweight='bold')
ax.set_ylabel("Avg Revenue (M VND)", fontsize=12, color=text_dark, fontweight='bold')
ax.set_title("The Most Intense Seasonal Cycle of the Year: TET", fontsize=16, fontweight="bold", color=darkest_green, pad=15)
plt.savefig(OUT / "2_tet_effect.png")
plt.close()

# ==============================================================================
# CHART 3: Product Lifecycle Evolution
# Level: Diagnostic
# ==============================================================================
print("Generating Chart 3: Product Lifecycle...")
# Extract suffix integer from product_id
products['sku_suffix'] = products['product_name'].str.split('-').str[-1].astype(int)

# Group products by suffix bins (Generations)
bins = [0, 20, 40, 60, 80, 100]
labels = ['Gen 1\n(Code 00-20)', 'Gen 2\n(Code 21-40)', 'Gen 3\n(Code 41-60)', 'Gen 4\n(Code 61-80)', 'Gen 5\n(Code 81-99)']
products['generation'] = pd.cut(products['sku_suffix'], bins=bins, labels=labels, include_lowest=True)

# Merge with order items to get total revenue per product
oi_sample = pd.read_csv(DATA / "order_items.csv", usecols=['product_id', 'quantity', 'unit_price', 'discount_amount'])
oi_sample['discount_amount'] = oi_sample['discount_amount'].fillna(0)
oi_sample['rev'] = oi_sample['quantity'] * oi_sample['unit_price'] - oi_sample['discount_amount']

prod_rev = oi_sample.groupby('product_id')['rev'].sum().reset_index()
products = products.merge(prod_rev, on='product_id', how='left')

gen_stats = products.groupby('generation').agg(
    avg_rev_per_sku=('rev', lambda x: x.mean() / 1e6),
    margin=('margin_pct', 'mean')
).dropna()

fig, ax1 = plt.subplots(figsize=(10, 6))
x = np.arange(len(gen_stats))

bars = ax1.bar(x, gen_stats['avg_rev_per_sku'], color=base_green, width=0.5, edgecolor=darkest_green)
bars[-1].set_color(dark_green2) # Highlight newest gen

for i, bar in enumerate(bars):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
             f"{gen_stats['avg_rev_per_sku'].iloc[i]:.0f}M", ha='center', color=text_dark, fontweight='bold')

ax1.set_ylabel("Avg Revenue / SKU (M VND)", color=text_dark, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(gen_stats.index, fontweight='bold', color=text_dark)

# Add line plot for margin
ax2 = ax1.twinx()
ax2.plot(x, gen_stats['margin'] * 100, color=darkest_green, marker='o', lw=2, markersize=8)
for i, v in enumerate(gen_stats['margin']):
    ax2.text(x[i], v*100 + 0.5, f"{v*100:.1f}%", ha='center', color=darkest_green, fontweight='bold')

ax2.set_ylabel("Gross Margin (%)", color=darkest_green, fontweight='bold')
ax2.spines['right'].set_color(darkest_green)
ax2.tick_params(axis='y', colors=darkest_green)

plt.title("The Power of R&D\nNew product generations drive higher revenue & better margins", 
          fontsize=14, fontweight='bold', color=text_dark, pad=20)
plt.savefig(OUT / "3_product_lifecycle.png")
plt.close()
del oi_sample

# ==============================================================================
# CHART 4: Logistics & Customer Churn
# Level: Predictive & Prescriptive
# ==============================================================================
print("Generating Chart 4: Logistics Churn...")
shipments = pd.read_csv(DATA / "shipments.csv", usecols=['order_id', 'delivery_date'])
orders = pd.read_csv(DATA / "orders.csv", usecols=['order_id', 'customer_id', 'order_date'])
orders['order_date'] = pd.to_datetime(orders['order_date'])

ship = shipments.merge(orders, on='order_id', how='inner')
ship.dropna(subset=['delivery_date'], inplace=True)

ship['delivery_date'] = pd.to_datetime(ship['delivery_date'])
ship['delivery_days'] = (ship['delivery_date'] - ship['order_date']).dt.days
ship['is_late'] = (ship['delivery_days'] > 5).astype(int)

# Sort by customer and date
ship = ship.sort_values(['customer_id', 'order_date'])

# Did the customer buy again AFTER this order?
ship['next_order_date'] = ship.groupby('customer_id')['order_date'].shift(-1)
# Consider churned if no next order OR next order is > 180 days away
ship['days_to_next'] = (ship['next_order_date'] - ship['order_date']).dt.days
ship['churned'] = ship['days_to_next'].isna() | (ship['days_to_next'] > 180)

churn_stats = ship.groupby('is_late')['churned'].mean() * 100

fig, ax = plt.subplots(figsize=(8, 6))
bars = ax.bar(['On Time', 'Delayed'], churn_stats, color=[base_green, dark_green3], width=0.4, edgecolor=darkest_green)

for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
             f"{bar.get_height():.1f}%", ha='center', color=text_dark, fontweight='bold', fontsize=14)

ax.set_ylabel("Customer Churn Rate (%)", fontweight='bold', color=text_dark)
ax.set_ylim(0, max(churn_stats) * 1.3)
ax.set_title("Logistics Paradox: 1 day late, lost forever", fontsize=14, fontweight='bold', color=text_dark)

ax.annotate("Delayed delivery significantly\nincreases churn rate!",
            xy=(1, churn_stats.iloc[1]), xytext=(0.5, churn_stats.max() * 1.15),
            arrowprops=dict(arrowstyle="->", color=darkest_green, lw=2),
            ha='center', color=dark_green4, fontweight='bold')

plt.savefig(OUT / "4_logistics_churn.png")
plt.close()

print("All charts generated in green theme!")
