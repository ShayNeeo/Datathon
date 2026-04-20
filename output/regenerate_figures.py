"""
Regenerate visualizations with exact color palette and requirements
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

STEEL_BLUE = "#7DAACB"
WARM_SAND = "#E8DBB3"
CREAM = "#FFFDEB"
VIETNAMESE_RED = "#CE2626"

STEEL_BLUE_LIGHT = "#A5C5D8"
STEEL_BLUE_DARK = "#5A8CA8"
WARM_SAND_DARK = "#D4C49A"

OUTPUT_DIR = Path("/home/shayneeo/Downloads/Datathon/output/figures_living")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid')
rcParams['font.family'] = 'DejaVu Sans'
rcParams['font.size'] = 12
rcParams['axes.facecolor'] = CREAM
rcParams['figure.facecolor'] = CREAM
rcParams['savefig.facecolor'] = CREAM
rcParams['grid.color'] = WARM_SAND
rcParams['grid.linewidth'] = 0.5
rcParams['grid.alpha'] = 0.4
rcParams['axes.titlesize'] = 12
rcParams['axes.titleweight'] = 'bold'

DATA_DIR = Path("/home/shayneeo/Downloads/Datathon/input")
orders = pd.read_csv(DATA_DIR / "orders.csv")
order_items = pd.read_csv(DATA_DIR / "order_items.csv")

orders['order_date'] = pd.to_datetime(orders['order_date'])

order_revenue = order_items.groupby('order_id')['unit_price'].sum().reset_index()
orders = orders.merge(order_revenue, on='order_id', how='left')
orders['revenue'] = orders['unit_price']

daily_revenue = orders.groupby('order_date')['revenue'].sum().reset_index()
daily_revenue['rolling_30d'] = daily_revenue['revenue'].rolling(window=30, min_periods=1).mean()

print("="*60)
print("1. Creating revenue_trend.png")
print("="*60)

fig, ax = plt.subplots(figsize=(14, 8))

ax.plot(daily_revenue['order_date'], daily_revenue['revenue'], 
       color=WARM_SAND, alpha=0.3, linewidth=0.8, label='Daily Revenue')

ax.plot(daily_revenue['order_date'], daily_revenue['rolling_30d'], 
       color=STEEL_BLUE, linewidth=3, label='30-Day Rolling Average')

ax.fill_between(daily_revenue['order_date'], 0, daily_revenue['rolling_30d'], 
               color=STEEL_BLUE, alpha=0.12)

peak_idx = daily_revenue['rolling_30d'].idxmax()
peak_date = daily_revenue.loc[peak_idx, 'order_date']
peak_value = daily_revenue.loc[peak_idx, 'rolling_30d']

start_val = daily_revenue['revenue'].iloc[0]

ax.annotate('Start\n~280K VND', 
          xy=(daily_revenue['order_date'].iloc[0], start_val),
          xytext=(daily_revenue['order_date'].iloc[0] + pd.Timedelta(days=200), 
                 start_val * 0.4),
          arrowprops=dict(arrowstyle='->', color=VIETNAMESE_RED, linewidth=2),
          fontsize=12, color=VIETNAMESE_RED, fontweight='bold',
          bbox=dict(boxstyle="round,pad=0.3", facecolor=CREAM, edgecolor=VIETNAMESE_RED))

ax.annotate('Peak: 20.9M VND\n2018-05-30', 
          xy=(peak_date, peak_value),
          xytext=(peak_date - pd.Timedelta(days=180), peak_value * 0.65),
          arrowprops=dict(arrowstyle='->', color=STEEL_BLUE, linewidth=2),
          fontsize=12, color=STEEL_BLUE_DARK, fontweight='bold',
          bbox=dict(boxstyle="round,pad=0.3", facecolor=CREAM, edgecolor=STEEL_BLUE))

ax.set_title('The 70x Journey: From 280K to 20M VND Daily', fontsize=14, fontweight='bold', 
            color=STEEL_BLUE, pad=20)
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Daily Revenue (VND)', fontsize=12)
ax.legend(loc='upper left', frameon=True, fancybox=True, fontsize=11)
ax.grid(True, alpha=0.3)
ax.ticklabel_format(style='plain', axis='y')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "revenue_trend.png", dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {OUTPUT_DIR / 'revenue_trend.png'}")


print("="*60)
print("2. Creating seasonality_dow.png")
print("="*60)

orders['dow'] = orders['order_date'].dt.day_name()
dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_revenue = orders.groupby('dow')['revenue'].sum()
dow_revenue = dow_revenue.reindex(dow_order)

fig, ax = plt.subplots(figsize=(12, 8))

colors = [VIETNAMESE_RED if day == 'Wednesday' else STEEL_BLUE for day in dow_order]
bars = ax.bar(range(len(dow_revenue)), dow_revenue.values / 1e6, color=colors, 
            alpha=0.85, edgecolor='white', linewidth=2)

ax.set_xticks(range(len(dow_revenue)))
ax.set_xticklabels(dow_order, fontsize=12)
ax.set_xlabel('Day of Week', fontsize=12)
ax.set_ylabel('Total Revenue (Million VND)', fontsize=12)

for i, (bar, val) in enumerate(zip(bars, dow_revenue.values)):
    label_color = VIETNAMESE_RED if dow_order[i] == 'Wednesday' else STEEL_BLUE_DARK
    ax.text(i, val/1e6 + 0.3, f'{val/1e6:.0f}M', 
           ha='center', fontsize=11, fontweight='bold', color=label_color)

wed_idx = dow_order.index('Wednesday')
ax.axvline(x=wed_idx - 0.5, color=VIETNAMESE_RED, linestyle='--', alpha=0.5, linewidth=2)

ax.set_title('Why Wednesday Wins', fontsize=14, fontweight='bold', color=STEEL_BLUE, pad=20)
ax.grid(True, axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "seasonality_dow.png", dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {OUTPUT_DIR / 'seasonality_dow.png'}")


print("="*60)
print("3. Creating promotions_fight.png")
print("="*60)

order_items_promo = order_items.merge(orders[['order_id', 'order_date']], on='order_id', how='left')

orders_with_promo = order_items[order_items['promo_id'].notna()]['order_id'].unique()
orders_without_promo = order_items[order_items['promo_id'].isna()]['order_id'].unique()

with_promo_rev = order_items[order_items['order_id'].isin(orders_with_promo)].groupby('order_id')['unit_price'].sum().mean()
without_promo_rev = order_items[order_items['order_id'].isin(orders_without_promo)].groupby('order_id')['unit_price'].sum().mean()

fig, ax = plt.subplots(figsize=(12, 8))

x = np.arange(2)
bars = ax.bar(x, [with_promo_rev, without_promo_rev], 
             color=[VIETNAMESE_RED, STEEL_BLUE], 
             alpha=0.85, edgecolor='white', linewidth=3, width=0.6)

ax.set_xticks(x)
ax.set_xticklabels(['With Promo', 'Without Promo'], fontsize=12, fontweight='bold')
ax.set_ylabel('Average Order Value (VND)', fontsize=12)
ax.set_xlabel('')

ax.text(0, with_promo_rev + 400, f'{with_promo_rev:,.0f}', 
        ha='center', fontsize=13, fontweight='bold', color=VIETNAMESE_RED)
ax.text(1, without_promo_rev + 400, f'{without_promo_rev:,.0f}', 
        ha='center', fontsize=13, fontweight='bold', color=STEEL_BLUE_DARK)

ax.annotate('', xy=(1, without_promo_rev), xytext=(0, with_promo_rev),
            arrowprops=dict(arrowstyle='->', color='gray', lw=2))
mid_y = (with_promo_rev + without_promo_rev) / 2
ax.text(0.5, mid_y + 600, f'-{((without_promo_rev - with_promo_rev) / without_promo_rev) * 100:.1f}%', 
       ha='center', fontsize=11, fontweight='bold', color='gray',
       bbox=dict(boxstyle="round,pad=0.2", facecolor=CREAM, edgecolor='gray'))

ax.set_title('The Promotion Paradox: Lower AOV with Promos', fontsize=14, fontweight='bold', 
            color=STEEL_BLUE, pad=20)
ax.grid(True, axis='y', alpha=0.3)
ax.set_ylim(0, max(with_promo_rev, without_promo_rev) * 1.25)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "promotions_fight.png", dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {OUTPUT_DIR / 'promotions_fight.png'}")


print("="*60)
print("4. Creating cohort_growth.png")
print("="*60)

orders_sorted = orders.sort_values('order_date')
first_purchase = orders_sorted.groupby('customer_id')['order_date'].first().reset_index()
first_purchase.columns = ['customer_id', 'first_purchase_date']
first_purchase['first_purchase_month'] = first_purchase['first_purchase_date'].dt.to_period('M')

orders = orders.merge(first_purchase[['customer_id', 'first_purchase_month']], on='customer_id', how='left')
orders['order_month'] = orders['order_date'].dt.to_period('M')
orders['months_since_first'] = (orders['order_month'].dt.year - orders['first_purchase_month'].dt.year) * 12 + \
                            (orders['order_month'].dt.month - orders['first_purchase_month'].dt.month)

cohort_counts = orders.groupby(['first_purchase_month', 'months_since_first'])['customer_id'].nunique().reset_index()
cohort_sizes = orders.groupby('first_purchase_month')['customer_id'].nunique()

cohort_pivot = cohort_counts.pivot_table(index='first_purchase_month', columns='months_since_first', 
                                          values='customer_id', fill_value=0)

retention = cohort_pivot.divide(cohort_sizes, axis=0)

retention = retention[retention.index >= '2018-01']
retention = retention.loc[:, retention.columns <= 11]
retention = retention.head(12)

fig, ax = plt.subplots(figsize=(14, 10))

custom_cmap = plt.cm.colors.LinearSegmentedColormap.from_list(
    'custom', [CREAM, WARM_SAND, STEEL_BLUE, VIETNAMESE_RED], N=256)

im = ax.imshow(retention.values, cmap=custom_cmap, aspect='auto', vmin=0, vmax=1)

ax.set_xticks(range(len(retention.columns)))
ax.set_xticklabels(retention.columns, fontsize=11, rotation=0)
ax.set_yticks(range(len(retention.index)))
ax.set_yticklabels([str(idx) for idx in retention.index], fontsize=11)

ax.set_xlabel('Months Since First Purchase', fontsize=12, fontweight='bold')
ax.set_ylabel('Cohort Month', fontsize=12, fontweight='bold')

cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('Retention Rate', fontsize=12)

for i in range(len(retention.index)):
    for j in range(len(retention.columns)):
        val = retention.iloc[i, j]
        if val > 0:
            text_color = 'white' if val > 0.4 else STEEL_BLUE_DARK
            ax.text(j, i, f'{val:.0%}', ha='center', va='center', 
                   color=text_color, fontweight='bold', fontsize=9)

ax.set_title('Cohort Retention: Customer Loyalty Over Time', fontsize=14, fontweight='bold', 
             color=STEEL_BLUE, pad=20)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "cohort_growth.png", dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {OUTPUT_DIR / 'cohort_growth.png'}")

print("\n" + "="*60)
print("ALL VISUALIZATIONS COMPLETE")
print("="*60)
print(f"Output directory: {OUTPUT_DIR}")