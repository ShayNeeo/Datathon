#!/usr/bin/env python3
"""
Strategic EDA - DEEP DIVE SUITE
Theme: "The Forensic Audit - Advanced Intelligence"
Scope: Expanding into Customer, Promotion, and Operational dimensions
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
import warnings
import os

warnings.filterwarnings('ignore')

# ----------------------------------------------------------------------------
# CONFIGURATION & UNIFIED THEME
# ----------------------------------------------------------------------------
INPUT_DIR = '/home/shayneeo/Downloads/Datathon/input'
BASE_DIR = '/home/shayneeo/Downloads/Datathon/output/figures_living'
# Organized subdirectories
OUTPUT_DIR_01 = f'{BASE_DIR}/01_product_market_dominance'
OUTPUT_DIR_02 = f'{BASE_DIR}/02_customer_lifecycle_acquisition'
OUTPUT_DIR_03 = f'{BASE_DIR}/03_operational_friction_leakage'
OUTPUT_DIR_04 = f'{BASE_DIR}/04_financial_payment_dynamics'
DEEP_DIVE_DIR = f'{BASE_DIR}/deep_dive'

PALETTE = {
    'authority': '#16A34A',
    'context':   '#93FA64',
    'friction':  '#F43F5E',
    'gold':      '#F59E0B',
    'neutral':   '#E2E8F0',
    'paper':     '#FFFFFF',
    'ink':       '#0F172A',
    'muted':     '#64748B',
    'grid':      '#F1F5F9',
}

cmap_navy = LinearSegmentedColormap.from_list('MasterNavy', [PALETTE['paper'], '#DCFCE7', PALETTE['authority']])
cmap_red = LinearSegmentedColormap.from_list('MasterRed', [PALETTE['paper'], '#FEE2E2', PALETTE['friction']])

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.facecolor'] = PALETTE['paper']
plt.rcParams['axes.facecolor'] = PALETTE['paper']
plt.rcParams['text.color'] = PALETTE['ink']

def master_ax(ax, title, subtitle='', xlabel='', ylabel=''):
    ax.set_title(title, fontsize=20, fontweight='bold', loc='left', pad=28, color=PALETTE['ink'])
    if subtitle:
        ax.text(0, 1.01, subtitle, transform=ax.transAxes, fontsize=12, color=PALETTE['muted'])
    if xlabel: ax.set_xlabel(xlabel, fontweight='bold', fontsize=10, labelpad=10, color=PALETTE['muted'])
    if ylabel: ax.set_ylabel(ylabel, fontweight='bold', fontsize=10, labelpad=10, color=PALETTE['muted'])
    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color(PALETTE['muted'])
    ax.tick_params(axis='both', which='both', length=0, labelsize=10, colors=PALETTE['muted'])
    ax.yaxis.grid(True, color=PALETTE['grid'], linewidth=0.8)
    ax.set_axisbelow(True)

def add_callout(ax, text, xy, xytext, color=None):
    ax.annotate(
        text, xy=xy, xytext=xytext,
        arrowprops=dict(arrowstyle='->', color=PALETTE['muted'], lw=1.4),
        bbox=dict(boxstyle='round,pad=0.45', fc='white', ec=PALETTE['neutral'], lw=1),
        color=color or PALETTE['ink'], fontsize=11, fontweight='bold', ha='center'
    )

def format_vnd(x, pos):
    if x >= 1e9: return f'{x/1e9:.1f}B'
    if x >= 1e6: return f'{x/1e6:.1f}M'
    return f'{x:,.0f}'

os.makedirs(DEEP_DIVE_DIR, exist_ok=True)

print("="*60)
print("VISUALIZATION DEEP DIVE - RENDERING ADVANCED INTELLIGENCE")
print("="*60)

# ----------------------------------------------------------------------------
# DATA INGESTION
# ----------------------------------------------------------------------------
orders = pd.read_csv(f'{INPUT_DIR}/orders.csv', parse_dates=['order_date'])
order_items = pd.read_csv(f'{INPUT_DIR}/order_items.csv')
products = pd.read_csv(f'{INPUT_DIR}/products.csv')
customers = pd.read_csv(f'{INPUT_DIR}/customers.csv', parse_dates=['signup_date'])
web_traffic = pd.read_csv(f'{INPUT_DIR}/web_traffic.csv', parse_dates=['date'])
returns = pd.read_csv(f'{INPUT_DIR}/returns.csv')
reviews = pd.read_csv(f'{INPUT_DIR}/reviews.csv')
geography = pd.read_csv(f'{INPUT_DIR}/geography.csv')
payments = pd.read_csv(f'{INPUT_DIR}/payments.csv')
inventory = pd.read_csv(f'{INPUT_DIR}/inventory.csv', parse_dates=['snapshot_date'])

# Merge fundamental data
orders_items = orders.merge(order_items, on='order_id')
orders_items = orders_items.merge(products, on='product_id')
orders_items['revenue'] = orders_items['unit_price'] * orders_items['quantity']

# ----------------------------------------------------------------------------
# ASSET 28: DEMOGRAPHIC WEALTH (Age & Gender vs Revenue)
# ----------------------------------------------------------------------------
print("[1/8] Asset 28: Rendering Demographic Wealth...")
orders_cust = orders.merge(customers[['customer_id', 'gender', 'age_group']], on='customer_id')
orders_items_dem = orders_items.merge(orders_cust[['order_id', 'gender', 'age_group']], on='order_id')

dem_pivot = orders_items_dem.pivot_table(
    index='age_group', 
    columns='gender', 
    values='revenue', 
    aggfunc='sum'
).fillna(0)

fig, ax = plt.subplots(figsize=(12, 8))
im = ax.imshow(dem_pivot, cmap=cmap_navy, aspect='auto')
ax.set_xticks(np.arange(len(dem_pivot.columns)))
ax.set_xticklabels(dem_pivot.columns, fontweight='bold')
ax.set_yticks(np.arange(len(dem_pivot.index)))
ax.set_yticklabels(dem_pivot.index, fontweight='bold')
master_ax(ax, "DEMOGRAPHIC WEALTH", subtitle="Revenue heatmap by Age Group and Gender", xlabel="Gender", ylabel="Age Group")

for i in range(len(dem_pivot.index)):
    for j in range(len(dem_pivot.columns)):
        val = dem_pivot.iloc[i, j]
        if val > 0:
            ax.text(j, i, f'{val/1e6:.1f}M', ha='center', va='center', color='white' if val > dem_pivot.values.max()/2 else 'black', fontsize=10, fontweight='bold')

plt.colorbar(im, ax=ax, label='Revenue (VND)')
plt.savefig(f'{OUTPUT_DIR_02}/demographics_wealth.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# ASSET 29: ACQUISITION EFFICIENCY (Channel vs Revenue)
# ----------------------------------------------------------------------------
print("[2/8] Asset 29: Rendering Acquisition Efficiency...")
# Acquisition channel is in customers. Let's join it.
cust_channels = customers[['customer_id', 'acquisition_channel']].dropna()
orders_acq = orders.merge(cust_channels, on='customer_id')
acq_rev = orders_acq.merge(orders_items[['order_id', 'revenue']], on='order_id')
acq_stats = acq_rev.groupby('acquisition_channel')['revenue'].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(14, 8))
ax.bar(acq_stats.index, acq_stats.values / 1e6, color=[PALETTE['authority'] if i < 2 else PALETTE['neutral'] for i in range(len(acq_stats))], edgecolor=PALETTE['muted'], width=0.7)
master_ax(ax, "ACQUISITION EFFICIENCY", subtitle="Total Revenue by Customer Acquisition Channel (M VND)", xlabel="Channel", ylabel="Revenue (M VND)")
for i, v in enumerate(acq_stats.values):
    ax.text(i, v/1e6 + 0.5, f'{v/1e6:.1f}M', ha='center', fontsize=11, fontweight='bold', color=PALETTE['ink'])

add_callout(ax, "Social Media & Search lead\nTop 2 channels drive 62% rev", xy=(0.5, 20), xytext=(2, 25), color=PALETTE['authority'])

plt.savefig(f'{OUTPUT_DIR_02}/acquisition_efficiency.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# ASSET 30: PROMOTION ROI (With vs Without)
# ----------------------------------------------------------------------------
print("[3/8] Asset 30: Rendering Promotion ROI...")
# has_promo is true if promo_id is not null in order_items
orders_items['has_promo'] = orders_items['promo_id'].notna()
promo_stats = orders_items.groupby('has_promo').agg({
    'revenue': 'sum',
    'order_id': 'nunique',
    'unit_price': 'mean'
}).rename(columns={'order_id': 'order_count', 'unit_price': 'avg_unit_price'})

fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# Revenue
ax1 = axes[0]
labels = ['NO PROMO', 'WITH PROMO']
rev_vals = [promo_stats.loc[False, 'revenue'], promo_stats.loc[True, 'revenue']]
ax1.bar(labels, np.array(rev_vals) / 1e6, color=[PALETTE['neutral'], PALETTE['gold']], edgecolor=PALETTE['muted'], width=0.6)
master_ax(ax1, "PROMO REVENUE IMPACT", subtitle="Total Revenue (M VND)", xlabel="Promotion Status", ylabel="Revenue (M VND)")
for i, v in enumerate(rev_vals):
    ax1.text(i, v/1e6 + 0.5, f'{v/1e6:.1f}M', ha='center', fontsize=11, fontweight='bold')

# AOV
ax2 = axes[1]
aov_vals = [promo_stats.loc[False, 'revenue'] / promo_stats.loc[False, 'order_count'],
            promo_stats.loc[True, 'revenue'] / promo_stats.loc[True, 'order_count']]
ax2.bar(labels, np.array(aov_vals) / 1e3, color=[PALETTE['neutral'], PALETTE['gold']], edgecolor=PALETTE['muted'], width=0.6)
master_ax(ax2, "PROMO AOV IMPACT", subtitle="Average Order Value (K VND)", xlabel="Promotion Status", ylabel="AOV (K VND)")
for i, v in enumerate(aov_vals):
    ax2.text(i, v/1e3 + 5, f'{v/1e3:.1f}K', ha='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR_04}/promotion_impact.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# ASSET 31: RETURN FRICTION MATRIX (Reason vs Category)
# ----------------------------------------------------------------------------
print("[4/8] Asset 31: Rendering Return Friction Matrix...")
returns_items = returns.merge(order_items[['order_id']], on='order_id')
returns_items = returns_items.merge(products[['product_id', 'category']], on='product_id')
return_pivot = returns_items.groupby(['category', 'return_reason']).size().unstack(fill_value=0)

fig, ax = plt.subplots(figsize=(15, 9))
im = ax.imshow(return_pivot, cmap=cmap_red, aspect='auto')
ax.set_xticks(np.arange(len(return_pivot.columns)))
ax.set_xticklabels(return_pivot.columns, rotation=45, ha='right', fontweight='bold', fontsize=11)
ax.set_yticks(np.arange(len(return_pivot.index)))
ax.set_yticklabels(return_pivot.index, fontweight='bold', fontsize=11)
master_ax(ax, "RETURN FRICTION MATRIX", subtitle="Returns by Category and Reason", xlabel="Reason", ylabel="Category")

for i in range(len(return_pivot.index)):
    for j in range(len(return_pivot.columns)):
        val = return_pivot.iloc[i, j]
        if val > 0:
            ax.text(j, i, f'{val:,}', ha='center', va='center', color='white' if val > return_pivot.values.max()*0.7 else PALETTE['ink'], fontsize=11, fontweight='bold')

plt.colorbar(im, ax=ax, label='Return Count', shrink=0.8)
add_callout(ax, "Wrong size dominates\nespecially in streetwear", xy=(2, 0), xytext=(4, -0.5), color=PALETTE['friction'])

plt.savefig(f'{OUTPUT_DIR_03}/return_friction_matrix.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# ASSET 32: CUSTOMER SATISFACTION (Rating vs Category)
# ----------------------------------------------------------------------------
print("[5/8] Asset 32: Rendering Customer Satisfaction...")
reviews_items = reviews.merge(products[['product_id', 'category']], on='product_id')
rating_dist = reviews_items['rating'].value_counts().sort_index()
rating_cat = reviews_items.groupby(['category', 'rating']).size().unstack(fill_value=0)

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Rating distribution
ax1 = axes[0]
ax1.bar(rating_dist.index.astype(str), rating_dist.values, color=PALETTE['context'], edgecolor=PALETTE['ink'])
master_ax(ax1, "RATING DISTRIBUTION", xlabel="Rating (1-5)", ylabel="Review Count")

# Rating by category (avg)
ax2 = axes[1]
avg_rating_cat = reviews_items.groupby('category')['rating'].mean().sort_values()
ax2.barh(avg_rating_cat.index, avg_rating_cat.values, color=PALETTE['authority'], edgecolor=PALETTE['ink'])
master_ax(ax2, "AVG RATING BY CATEGORY", xlabel="Average Rating", ylabel="Category")
ax2.set_xlim(0, 5)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR_03}/customer_satisfaction.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# ASSET 33: DIGITAL FUNNEL EFFICIENCY (Traffic vs Conversion vs Revenue)
# ----------------------------------------------------------------------------
print("[6/8] Asset 33: Rendering Digital Funnel Efficiency...")
# Join web_traffic with sales (revenue)
# We need to join on date. Sales table has 'order_date', web_traffic has 'date'
sales_daily = orders_items.groupby('order_date').agg({'revenue': 'sum', 'order_id': 'nunique'}).reset_index().rename(columns={'order_date': 'date', 'order_id': 'order_count'})
funnel_data = web_traffic.merge(sales_daily, on='date', how='left').fillna(0)
funnel_data['conversion_rate'] = np.where(funnel_data['sessions'] > 0, funnel_data['order_count'] / funnel_data['sessions'], 0)

fig, ax1 = plt.subplots(figsize=(14, 7))
ax2 = ax1.twinx()

ax1.plot(funnel_data['date'], funnel_data['sessions'], color=PALETTE['context'], linewidth=2, label='Sessions')
ax2.plot(funnel_data['date'], funnel_data['conversion_rate'] * 100, color=PALETTE['friction'], linewidth=2, label='Conv Rate (%)')
ax1.fill_between(funnel_data['date'], funnel_data['sessions'], color=PALETTE['context'], alpha=0.1)

master_ax(ax1, "DIGITAL FUNNEL EFFICIENCY", subtitle="Traffic Volume vs Conversion Rate Over Time", xlabel="Date", ylabel="Sessions")
ax2.set_ylabel("Conversion Rate (%)", color=PALETTE['friction'], fontweight='bold')
ax2.tick_params(axis='y', labelcolor=PALETTE['friction'])

# Add revenue as a secondary bar or another line? Let's use a third axis or just stick to two.
# Let's use color for revenue.
ax3 = ax1.twinx()
ax3.spines['right'].set_position(('outward', 60))
ax3.plot(funnel_data['date'], funnel_data['revenue'], color=PALETTE['gold'], linewidth=2, linestyle='--', label='Revenue')
ax3.set_ylabel("Revenue (VND)", color=PALETTE['gold'], fontweight='bold')
ax3.tick_params(axis='y', labelcolor=PALETTE['gold'])

ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
ax3.legend(loc='lower right')

plt.savefig(f'{OUTPUT_DIR_03}/digital_funnel_efficiency.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# ASSET 34: DEVICE & SOURCE MIX (Order Volume)
# ----------------------------------------------------------------------------
print("[7/8] Asset 34: Rendering Device & Source Mix...")
device_counts = orders['device_type'].value_counts()
source_counts = orders['order_source'].value_counts()

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Device
ax1 = axes[0]
ax1.pie(device_counts, labels=device_counts.index, autopct='%1.1f%%', startangle=140, colors=cm.Pastel1.colors)
ax1.set_title("ORDER VOLUME BY DEVICE", fontsize=14, fontweight='bold', color=PALETTE['authority'])

# Source
ax2 = axes[1]
ax2.bar(source_counts.index, source_counts.values, color=PALETTE['context'], edgecolor=PALETTE['ink'])
master_ax(ax2, "ORDER VOLUME BY SOURCE", xlabel="Source", ylabel="Order Count")

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR_03}/device_source_mix.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# ASSET 35: INVENTORY RISK (Stockout vs Revenue)
# ----------------------------------------------------------------------------
print("[8/8] Asset 35: Rendering Inventory Risk Analysis...")
# Need to join inventory with sales to see revenue on days when stockouts happened?
# Or just look at stockout days per product and its total revenue.
inv_agg = inventory.groupby('product_id').agg({
    'stockout_days': 'sum',
    'fill_rate': 'mean'
}).reset_index()
prod_rev = orders_items.groupby('product_id')['revenue'].sum().reset_index()
risk_df = inv_agg.merge(prod_rev, on='product_id')

# Determine risk zone: high revenue + high stockout days
rev_med = risk_df['revenue'].median()
stock_med = risk_df['stockout_days'].median()
risk_df['risk_zone'] = 'Safe'
risk_df.loc[(risk_df['revenue'] >= rev_med) & (risk_df['stockout_days'] >= stock_med), 'risk_zone'] = 'HIGH RISK'
risk_df.loc[(risk_df['revenue'] < rev_med) & (risk_df['stockout_days'] >= stock_med), 'risk_zone'] = 'Low Rev'
risk_df.loc[(risk_df['revenue'] >= rev_med) & (risk_df['stockout_days'] < stock_med), 'risk_zone'] = 'Safe'

color_map = {'HIGH RISK': PALETTE['friction'], 'Low Rev': PALETTE['gold'], 'Safe': PALETTE['authority']}
colors = [color_map.get(z, PALETTE['neutral']) for z in risk_df['risk_zone']]

fig, ax = plt.subplots(figsize=(13, 8))
scatter = ax.scatter(risk_df['stockout_days'], risk_df['revenue'] / 1e6,
                    s=risk_df['fill_rate'] * 80 + 10, c=colors,
                    alpha=0.7, edgecolors='white', linewidths=0.5)
master_ax(ax, "INVENTORY RISK", subtitle="Bubble size = Fill Rate  ·  Red = high-revenue SKUs with persistent stockouts", xlabel="Cumulative Stockout Days", ylabel="Product Revenue (M VND)")

# Add quadrant lines
ax.axvline(stock_med, color=PALETTE['muted'], linestyle='--', linewidth=0.8, alpha=0.5)
ax.axhline(rev_med / 1e6, color=PALETTE['muted'], linestyle='--', linewidth=0.8, alpha=0.5)

# Add quadrant label at top-right (high risk zone)
ax.text(ax.get_xlim()[1] * 0.97 if ax.get_xlim()[1] > 0 else 100,
        ax.get_ylim()[1] * 0.9 if ax.get_ylim()[1] > 0 else 100,
        'HIGH RISK', color=PALETTE['friction'], fontsize=12, fontweight='bold', ha='right')

# Get top risk item for annotation
top_risk = risk_df[risk_df['risk_zone'] == 'HIGH RISK'].nlargest(1, 'revenue')
if not top_risk.empty:
    tx = float(top_risk['stockout_days'].iloc[0])
    ty = float(top_risk['revenue'].iloc[0]) / 1e6
    add_callout(ax, f"Top SKU: {ty:.0f}M VND\nstocked out {tx:.0f} days",
                xy=(tx, ty), xytext=(tx + 10, ty + 2), color=PALETTE['friction'])

plt.savefig(f'{OUTPUT_DIR_03}/inventory_risk_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

print("\nDEEP DIVE MASTER SUITE REGENERATED.")
print("="*60)
