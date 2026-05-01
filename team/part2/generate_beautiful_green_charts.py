import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

# --- AESTHETIC SETTINGS ---
# Use a clean seaborn style
sns.set_theme(style="whitegrid", font="sans-serif")

# Custom Green Pastel Palette based around #93fa64
c_base = "#93fa64"        # Vibrant Green (Hero color)
c_pastel_light = "#dcfce7" # Light green background / subtle
c_pastel_mid = "#86efac"   # Mid pastel green
c_dark_accent = "#166534"  # Very dark green for text/lines
c_alert = "#fca5a5"        # Pastel red for negative/loss
c_alert_dark = "#991b1b"   # Dark red for alert text
c_neutral = "#94a3b8"      # Slate gray for inactive elements

plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 16,
    "axes.titleweight": "bold",
    "axes.labelsize": 12,
    "axes.labelweight": "bold",
    "axes.labelcolor": c_dark_accent,
    "xtick.color": c_dark_accent,
    "ytick.color": c_dark_accent,
    "text.color": c_dark_accent,
    "figure.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.3,
    "axes.edgecolor": "#cbd5e1",
    "axes.linewidth": 1.5,
    "grid.color": "#f1f5f9",
})

DATA = Path(r"c:\Users\TRIDELL\Desktop\vinuni\datathon-2026-round-1")
OUT = Path(r"c:\Users\TRIDELL\Desktop\vinuni\part2\charts_final")
os.makedirs(OUT, exist_ok=True)

# Helper function for chart annotations
def annotate_chart(ax, text, xy, xytext, color, arrow_color):
    ax.annotate(text, xy=xy, xytext=xytext,
                arrowprops=dict(arrowstyle="->", color=arrow_color, lw=2, connectionstyle="arc3,rad=0.1"),
                color=color, fontweight="bold", ha="center", fontsize=11,
                bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor=color, alpha=0.9, lw=1.5))

print("Loading Data...")
products = pd.read_csv(DATA / "products.csv")

# ==============================================================================
# CHART 1: The Loss Leader Trap (Bait Trap - Negative Profit)
# ==============================================================================
print("Generating Chart 1: Loss Leader Trap...")
order_items = pd.read_csv(DATA / "order_items.csv", low_memory=False)

products['margin'] = (products['price'] - products['cogs']) / products['price']
loss_leader_ids = products[products['margin'] <= 0.055]['product_id'].unique()

order_items['is_loss_leader'] = order_items['product_id'].isin(loss_leader_ids)
order_items['item_revenue'] = order_items['quantity'] * order_items['unit_price'] - order_items['discount_amount'].fillna(0)
order_items = order_items.merge(products[['product_id', 'cogs']], on='product_id', how='left')
order_items['item_profit'] = order_items['item_revenue'] - (order_items['quantity'] * order_items['cogs'])

order_stats = order_items.groupby('order_id').agg(
    has_loss_leader=('is_loss_leader', 'max'),
    total_revenue=('item_revenue', 'sum'),
    total_profit=('item_profit', 'sum'),
    total_items=('quantity', 'sum')
).reset_index()
order_stats = order_stats[order_stats['total_revenue'] > 0]

grp = order_stats.groupby('has_loss_leader').mean().reset_index()
# print(grp)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={'width_ratios': [2, 1]})

labels = ['Standard Order\n(No Bait Products)', '"Bait" Order\n(Contains Products w/ Margin <= 5.5%)']
x = np.arange(2)
width = 0.35

ax1.bar(x - width/2, grp['total_revenue'], width, label='Avg Revenue', color=c_pastel_mid, edgecolor=c_dark_accent)
ax1.bar(x + width/2, grp['total_profit'], width, label='Avg Profit', color=[c_base, c_alert], edgecolor=[c_dark_accent, c_alert_dark])

for i in range(2):
    ax1.text(x[i] - width/2, grp['total_revenue'].iloc[i] + 1000, f"{grp['total_revenue'].iloc[i]:,.0f}₫", ha='center', fontweight='bold', color=c_dark_accent)
    p_val = grp['total_profit'].iloc[i]
    y_off = 1000 if p_val > 0 else -3000
    color_val = c_dark_accent if p_val > 0 else c_alert_dark
    ax1.text(x[i] + width/2, p_val + y_off, f"{p_val:,.0f}₫", ha='center', fontweight='bold', color=color_val)

ax1.axhline(0, color=c_dark_accent, linewidth=1.5, linestyle='--')
ax1.set_xticks(x)
ax1.set_xticklabels(labels, fontweight='bold')
ax1.set_ylabel("VND")
ax1.set_title("Profit Illusion: High Revenue but Heavy Losses", pad=15)
ax1.legend()

annotate_chart(ax1, f"BUSINESS FAILURE:\n'Bait' orders DESTROY profit\n(Avg Loss {grp['total_profit'].iloc[1]:,.0f}₫)", 
               xy=(1 + width/2, grp['total_profit'].iloc[1]), xytext=(0.5, 10000), color=c_alert_dark, arrow_color=c_alert_dark)

sns.barplot(x='has_loss_leader', y='total_items', data=grp, ax=ax2, hue='has_loss_leader', palette=[c_pastel_light, c_pastel_mid], edgecolor=c_dark_accent, legend=False)
for i in range(2):
    ax2.text(i, grp['total_items'].iloc[i] + 0.1, f"{grp['total_items'].iloc[i]:.2f} SP", ha='center', fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(labels, fontweight='bold')
ax2.set_ylabel("Items per Order")
ax2.set_title("Cross-Selling Effect", pad=15)
ax2.set_xlabel("")

annotate_chart(ax2, f"Only +{grp['total_items'].iloc[1] - grp['total_items'].iloc[0]:.2f} more items\nNot enough to cover losses!", 
               xy=(1, grp['total_items'].iloc[1]), xytext=(0.5, 6), color=c_alert_dark, arrow_color=c_alert_dark)

fig.suptitle("The 'Loss Leader' Trap: Trading Blood for Volume\nSacrificing margin for larger baskets is a failing strategy", 
             fontsize=18, fontweight='bold', color=c_dark_accent, y=1.05)
plt.savefig(OUT / "1_loss_leader_trap.png")
plt.close()
del order_items, order_stats

# ==============================================================================
# CHART 2: Logistics Paradox
# ==============================================================================
print("Generating Chart 2: Logistics Paradox...")
orders = pd.read_csv(DATA / "orders.csv", parse_dates=['order_date'])
shipments = pd.read_csv(DATA / "shipments.csv", parse_dates=['ship_date', 'delivery_date'])

df_ship = orders[['order_id', 'customer_id', 'order_date']].merge(shipments[['order_id', 'delivery_date']], on='order_id', how='inner')
df_ship['delivery_days'] = (df_ship['delivery_date'] - df_ship['order_date']).dt.days
df_ship = df_ship[(df_ship['delivery_days'] >= 0) & (df_ship['delivery_days'] <= 14)]

df_ship = df_ship.sort_values(['customer_id', 'order_date'])
df_ship['order_rank'] = df_ship.groupby('customer_id').cumcount() + 1
first_orders = df_ship[df_ship['order_rank'] == 1].copy()
cust_order_counts = df_ship.groupby('customer_id').size()
first_orders['has_repurchased'] = first_orders['customer_id'].map(lambda x: 1 if cust_order_counts[x] > 1 else 0)

bins = [-1, 3, 6, 9, 14]
labels = ['1-3 days\n(Express)', '4-6 days\n(Standard)', '7-9 days\n(Slow)', '10-14 days\n(Very Late)']
first_orders['delivery_tier'] = pd.cut(first_orders['delivery_days'], bins=bins, labels=labels)

tier_stats = first_orders.groupby('delivery_tier', observed=False).agg(
    total_customers=('customer_id', 'count'), repurchased=('has_repurchased', 'sum')
).reset_index()
tier_stats['repurchase_rate'] = (tier_stats['repurchased'] / tier_stats['total_customers']) * 100
# print(tier_stats)

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='delivery_tier', y='repurchase_rate', data=tier_stats, ax=ax, color=c_pastel_mid, edgecolor=c_dark_accent, linewidth=1.5)
ax.plot(tier_stats.index, tier_stats['repurchase_rate'], color=c_base, marker='o', lw=3, markersize=10, markeredgecolor=c_dark_accent, markeredgewidth=2)

for i, val in enumerate(tier_stats['repurchase_rate']):
    ax.text(i, val + 1, f"{val:.1f}%", ha='center', fontweight='bold', fontsize=12)

ax.set_ylim(0, 100)
ax.set_ylabel("Repurchase Rate (%)")
ax.set_xlabel("")
ax.set_title("Inelastic Logistics Paradox\nCustomers don't care about delivery speed!", pad=20)

annotate_chart(ax, "Counter-intuitive Insight:\nRepurchase rate stays firmly at ~74%\nregardless of 2-day or 14-day delivery.\nWe are wasting money on express shipping!", 
               xy=(2, tier_stats['repurchase_rate'].iloc[2]), xytext=(1.5, 90), color=c_dark_accent, arrow_color=c_base)

plt.savefig(OUT / "2_logistics_paradox.png")
plt.close()

# ==============================================================================
# CHART 3: Product Lifecycle & Innovation
# ==============================================================================
print("Generating Chart 3: Product Lifecycle...")
products['suffix'] = products['product_name'].str.extract(r'-(\d+)$')[0].astype(int)
order_items = pd.read_csv(DATA / "order_items.csv", usecols=['product_id', 'quantity', 'unit_price', 'discount_amount'])
order_items['rev'] = order_items['quantity'] * order_items['unit_price'] - order_items['discount_amount'].fillna(0)
item_stats = order_items.groupby('product_id')['rev'].sum().reset_index()
prod_stats = products.merge(item_stats, on='product_id', how='left').fillna(0)

bins = [-1, 10, 30, 50, 70, 100]
labels = ['Classic\n(Code 00-10)', 'Early Gen\n(Code 11-30)', 'Mid Gen\n(Code 31-50)', 'Late Gen\n(Code 51-70)', 'Latest Gen\n(Code 71-99)']
prod_stats['generation'] = pd.cut(prod_stats['suffix'], bins=bins, labels=labels)
gen_stats = prod_stats.groupby('generation', observed=False).agg(
    total_rev=('rev', 'sum'), total_prod=('product_id', 'count')
).reset_index()
gen_stats['rev_per_sku'] = gen_stats['total_rev'] / gen_stats['total_prod']
# print(gen_stats)

fig, ax = plt.subplots(figsize=(10, 6))
colors = [c_neutral, c_neutral, c_pastel_light, c_pastel_mid, c_base]
sns.barplot(x='generation', y=gen_stats['rev_per_sku']/1e6, data=gen_stats, ax=ax, palette=colors, edgecolor=c_dark_accent, linewidth=1.5)
ax.plot(gen_stats.index, gen_stats['rev_per_sku']/1e6, color=c_dark_accent, marker='o', lw=2)

for i, val in enumerate(gen_stats['rev_per_sku']/1e6):
    ax.text(i, val + 0.2, f"{val:.1f}M", ha='center', fontweight='bold', fontsize=12)

ax.set_ylabel("Avg Revenue / SKU (M VND)")
ax.set_xlabel("")
ax.set_title("The Power of R&D (Product Iteration)\nImproved versions (Suffix 71-99) generate 64% more revenue/SKU vs. classic models", pad=20)

annotate_chart(ax, "Innovation Success:\nThe Design & R&D team is doing\nexcellent work capturing market demand with each version.", 
               xy=(4, (gen_stats['rev_per_sku'].iloc[4]/1e6)), xytext=(2, 12), color=c_dark_accent, arrow_color=c_base)

plt.savefig(OUT / "3_product_lifecycle.png")
plt.close()
del order_items

# ==============================================================================
# CHART 4: Tet Effect
# ==============================================================================
print("Generating Chart 4: Tet Effect...")
sales = pd.read_csv(DATA / "sales.csv", parse_dates=["Date"])
sales["year"] = sales.Date.dt.year
TET = {2013:"2013-02-10",2014:"2014-01-31",2015:"2015-02-19",2016:"2016-02-08",2017:"2017-01-28",2018:"2018-02-16"}
pre_covid = sales[sales.year.between(2013, 2018)].copy()

windows = []
for yr, tet_str in TET.items():
    tet = pd.Timestamp(tet_str)
    for delta in range(-30, 31):
        d = tet + pd.Timedelta(days=delta)
        row = pre_covid[pre_covid.Date == d]
        if len(row) > 0:
            windows.append({"delta": delta, "revenue": row.Revenue.values[0]})
df_tet = pd.DataFrame(windows)
avg_tet = df_tet.groupby("delta")["revenue"].mean() / 1e6

fig, ax = plt.subplots(figsize=(14, 6))
bar_colors = np.where(avg_tet.index < 0, c_pastel_mid, np.where(avg_tet.index <= 7, c_alert, c_base))
ax.bar(avg_tet.index, avg_tet.values, color=bar_colors, alpha=0.9, width=0.8, edgecolor="none")

baseline = pre_covid.Revenue.mean() / 1e6
ax.axhline(baseline, color=c_dark_accent, ls="--", lw=1.5, alpha=0.7)
ax.text(25, baseline + 0.15, f"Baseline: {baseline:.1f}M", fontsize=10, color=c_dark_accent, fontweight='bold')

phases_tet = [
    (-25, -1, "SHOPPING SURGE\n(Up 40-80%)", c_dark_accent, c_pastel_mid),
    (0, 7, "TET HOLIDAY\n(Down 50%)", c_alert_dark, c_alert),
    (8, 20, "RECOVERY\n(Back to normal)", c_dark_accent, c_base),
]
for s, e, label, text_col, bg_col in phases_tet:
    mid = (s + e) / 2
    y_pos = avg_tet.max() * 1.05
    ax.annotate(label, xy=(mid, y_pos), fontsize=10, ha="center",
                fontweight="bold", color=text_col,
                bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=bg_col, lw=2))
    ax.axvspan(s-0.5, e+0.5, alpha=0.1, color=bg_col)

ax.annotate(f"Peak: {avg_tet.max():.1f}M", xy=(avg_tet.idxmax(), avg_tet.max()), xytext=(avg_tet.idxmax()+8, avg_tet.max()+0.5),
            arrowprops=dict(arrowstyle="->", color=c_dark_accent, lw=1.5), fontweight="bold", color=c_dark_accent)

ax.set_xlabel("Days relative to Tet New Year (Day 0)", fontweight='bold')
ax.set_ylabel("Avg Revenue (M VND)", fontweight='bold')
ax.set_title("Tet Effect: The Largest Seasonal Cycle of the Year (Avg 2013-2018)", pad=15)
ax.set_ylim(bottom=0, top=avg_tet.max()*1.2)

plt.savefig(OUT / "4_tet_effect.png")
plt.close()

print("All beautiful charts generated!")
