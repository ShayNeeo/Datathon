#!/usr/bin/env python3
"""
Strategic EDA - FINAL MASTER EXTENDED SUITE (Full 10-Year Cohort Accuracy)
Theme: "The Forensic Audit"
Scope: 2012-2022 (Entire Dataset)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
import warnings

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
TOP_PROD_DIR = f'{BASE_DIR}/top_product_segment'
DEEP_DIVE_DIR = f'{BASE_DIR}/deep_dive'

PALETTE = {
    'authority': '#003366',    # Deep Navy
    'context':   '#7DAACB',    # Slate Blue
    'friction':  '#CE2626',    # Strategic Red
    'gold':      '#B8860B',    # Strategic Gold
    'highlight': '#E8DBB3',    # Sand
    'paper':     '#FFFDEB',    # Cream
    'ink':       '#1A1A1A',    # Dark Gray
    'grid':      '#D1D1D1',
}

cmap_navy = LinearSegmentedColormap.from_list('MasterNavy', [PALETTE['paper'], PALETTE['authority']])

plt.rcParams['font.family'] = 'serif'
plt.rcParams['figure.facecolor'] = PALETTE['paper']
plt.rcParams['axes.facecolor'] = PALETTE['paper']
plt.rcParams['text.color'] = PALETTE['ink']

def master_ax(ax, title, subtitle='', xlabel='', ylabel=''):
    ax.set_title(title.upper(), fontsize=16, fontweight='bold', loc='left', pad=25, color=PALETTE['authority'])
    if subtitle:
        ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=10, color=PALETTE['ink'], fontstyle='italic')
    if xlabel: ax.set_xlabel(xlabel, fontweight='bold', fontsize=10, labelpad=10)
    if ylabel: ax.set_ylabel(ylabel, fontweight='bold', fontsize=10, labelpad=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(PALETTE['grid'])
    ax.spines['bottom'].set_color(PALETTE['grid'])
    ax.grid(axis='y', linestyle='--', alpha=0.3, color=PALETTE['grid'])

def format_vnd(x, pos):
    if x >= 1e9: return f'{x/1e9:.1f}B'
    if x >= 1e6: return f'{x/1e6:.1f}M'
    return f'{x:,.0f}'

print("="*60)
print("VISUALIZATION MASTER - RENDERING FULL LONGITUDINAL SUITE")
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
geography = pd.read_csv(f'{INPUT_DIR}/geography.csv')
payments = pd.read_csv(f'{INPUT_DIR}/payments.csv')
inventory = pd.read_csv(f'{INPUT_DIR}/inventory.csv', parse_dates=['snapshot_date'])
sales = pd.read_csv(f'{INPUT_DIR}/sales.csv', parse_dates=['Date'])

item_rev = order_items.merge(products[['product_id', 'category', 'segment']], on='product_id')
item_rev['revenue'] = item_rev['unit_price'] * item_rev['quantity']

# ----------------------------------------------------------------------------
# FIG 4: COHORT RETENTION (Full 10-Year Matrix)
# ----------------------------------------------------------------------------
print("[1/13] Fig 4: Rendering Full 10-Year Cohort Matrix...")
first_p = orders.groupby('customer_id')['order_date'].min().reset_index()
first_p.columns = ['customer_id', 'first_purchase']
first_p['cohort_year'] = first_p['first_purchase'].dt.year

df_ret = orders.merge(first_p, on='customer_id')
df_ret['order_year'] = df_ret['order_date'].dt.year
df_ret['years_since'] = df_ret['order_year'] - df_ret['cohort_year']

ret_matrix = df_ret.groupby(['cohort_year', 'years_since'])['customer_id'].nunique().unstack(fill_value=0)
ret_matrix = ret_matrix.divide(ret_matrix[0], axis=0) * 100

fig, ax = plt.subplots(figsize=(14, 10))
im = ax.imshow(ret_matrix, cmap=cmap_navy, aspect='auto')
master_ax(ax, "THE BRAND LOYALTY DECAY (2012-2022)", "Yearly cohort retention tracking since first acquisition",
          xlabel="Years Since First Purchase", ylabel="Customer Cohort (Acquisition Year)")

# Annotate cells
for i in range(ret_matrix.shape[0]):
    for j in range(ret_matrix.shape[1]):
        val = ret_matrix.iloc[i, j]
        if val > 0:
            ax.text(j, i, f'{val:.0f}', ha='center', va='center', color='white' if val > 40 else 'black', fontsize=9)

plt.colorbar(im, label='Retention Rate (%)')
plt.savefig(f'{OUTPUT_DIR_02}/cohort_growth.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# REMAINING SUITE (Unified & Labeled)
# ----------------------------------------------------------------------------
print("[2-13/13] Rendering Remaining Strategic Assets...")

# Fig 5: Promo Dual-Axis
order_items['has_promo'] = order_items['promo_id'].notna()
p_stats = order_items.groupby('has_promo').agg({'unit_price': 'mean', 'order_id': 'count'})
fig, ax = plt.subplots(figsize=(10, 6))
ax2 = ax.twinx()
ax.bar([0,1], p_stats['unit_price'] / 1e3, 0.35, color=PALETTE['context'], edgecolor=PALETTE['ink'])
ax2.bar([0.35,1.35], p_stats['order_id'] / 1e3, 0.35, color=PALETTE['authority'], edgecolor=PALETTE['ink'])
master_ax(ax, "THE PROMOTION PARADOX", xlabel="Order Type (Organic vs. Promoted)", ylabel="Avg Unit Price (K VND)")
ax2.set_ylabel("Order Volume (K Units)", color=PALETTE['authority'], fontweight='bold')
ax.set_xticks([0.17, 1.17]); ax.set_xticklabels(['ORGANIC', 'PROMOTED'], fontweight='bold')
plt.savefig(f'{OUTPUT_DIR_04}/promotions_fight.png', dpi=300, bbox_inches='tight')
plt.close()

# Fig 6: Traffic Horizontal
t_vol = web_traffic.groupby('traffic_source')['sessions'].sum().sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(12, 7))
ax.barh(t_vol.index, t_vol.values / 1e6, color=cm.Blues(np.linspace(0.4, 0.9, len(t_vol))), edgecolor=PALETTE['ink'])
master_ax(ax, "DIGITAL ACQUISITION FUNNEL", xlabel="Total Sessions (Millions)", ylabel="Traffic Source")
plt.savefig(f'{OUTPUT_DIR_03}/traffic_treemap.png', dpi=300, bbox_inches='tight')
plt.close()

# Fig 1: Category
c_st = item_rev.groupby('category')['revenue'].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(10, 8))
ax.pie(c_st, labels=c_st.index, autopct='%1.1f%%', startangle=140, colors=[PALETTE['authority'], PALETTE['context'], PALETTE['gold'], PALETTE['highlight']], explode=[0.08, 0, 0, 0])
ax.add_artist(plt.Circle((0,0), 0.70, fc=PALETTE['paper']))
ax.set_title("THE STREETWEAR HEGEMONY", fontsize=18, fontweight='bold', color=PALETTE['authority'], pad=20)
plt.savefig(f'{OUTPUT_DIR_01}/category_pie.png', dpi=300, bbox_inches='tight')
plt.close()

# Fig 2: Returns
r_v = returns['return_reason'].value_counts().sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(r_v.index, r_v.values, color=PALETTE['friction'], edgecolor=PALETTE['ink'])
master_ax(ax, "THE SIZING CRISIS", xlabel="Return Count", ylabel="Reason")
plt.savefig(f'{OUTPUT_DIR_03}/returns_bar.png', dpi=300, bbox_inches='tight')
plt.close()

# Fig 3: Revenue Trend
s_v = sales.set_index('Date')['Revenue'].resample('ME').sum()
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(s_v.index, s_v.values, color=PALETTE['authority'], linewidth=3)
ax.fill_between(s_v.index, s_v.values, color=PALETTE['authority'], alpha=0.1)
master_ax(ax, "THE 16.43B VND GROWTH ENGINE", xlabel="Fiscal Year", ylabel="Monthly Revenue (VND)")
ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_vnd))
plt.savefig(f'{OUTPUT_DIR_04}/revenue_trend.png', dpi=300, bbox_inches='tight')
plt.close()

# Fig 7: Geography
o_g = orders.merge(geography, on='zip')
e_v = o_g[o_g['region'] == 'East']['city'].value_counts().head(5)
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(e_v.index, e_v.values / 1e3, color=PALETTE['authority'], edgecolor=PALETTE['ink'])
master_ax(ax, "URBAN POWER CENTERS", xlabel="City", ylabel="Order Volume (K)")
plt.savefig(f'{OUTPUT_DIR_03}/geography_map.png', dpi=300, bbox_inches='tight')
plt.close()

# Fig 8: Monthly Seasonality
m_r = sales.groupby(sales['Date'].dt.month)['Revenue'].mean()
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(range(1,13), m_r / 1e6, color=PALETTE['context'], edgecolor=PALETTE['ink'])
master_ax(ax, "THE MAY ANOMALY", xlabel="Month", ylabel="Avg Daily Revenue (M VND)")
ax.set_xticks(range(1,13)); ax.set_xticklabels(['J','F','M','A','M','J','J','A','S','O','N','D'])
plt.savefig(f'{OUTPUT_DIR_03}/seasonality_month.png', dpi=300, bbox_inches='tight')
plt.close()

# Fig 9: Weekly Seasonality
orders['dow'] = orders['order_date'].dt.day_name()
d_v = orders['dow'].value_counts().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(d_v.index, d_v.values / 1e3, color=PALETTE['highlight'], edgecolor=PALETTE['ink'])
master_ax(ax, "THE WEDNESDAY PULSE", xlabel="Day of Week", ylabel="Order Volume (K)")
plt.savefig(f'{OUTPUT_DIR_03}/seasonality_dow.png', dpi=300, bbox_inches='tight')
plt.close()

# Fig 10: Segment Revenue
sg_v = item_rev.groupby('segment')['revenue'].sum().sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(sg_v.index, sg_v.values / 1e9, color=PALETTE['authority'], edgecolor=PALETTE['ink'])
master_ax(ax, "SEGMENT REVENUE SHARE", xlabel="Revenue (Billions VND)", ylabel="Market Segment")
plt.savefig(f'{OUTPUT_DIR_01}/segments.png', dpi=300, bbox_inches='tight')
plt.close()

# Fig 11: Inventory
iv_m = inventory.groupby('snapshot_date').agg({'fill_rate': 'mean'})
sl_m = sales.set_index('Date')['Revenue'].resample('ME').mean()
iv_m = iv_m.join(sl_m)
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(iv_m.index, iv_m['fill_rate'] * 100, color=PALETTE['friction'], label='Fill Rate %')
ax2 = ax.twinx()
ax2.bar(iv_m.index, iv_m['Revenue'] / 1e6, color=PALETTE['authority'], alpha=0.2, width=20)
master_ax(ax, "SUPPLY-SIDE CAPACITY CEILING", xlabel="Date", ylabel="Fill Rate (%)")
ax2.set_ylabel("Revenue (M VND)", color=PALETTE['authority'], fontweight='bold')
plt.savefig(f'{OUTPUT_DIR_03}/inventory_friction.png', dpi=300, bbox_inches='tight')
plt.close()

# Fig 12: Conversion Matrix
tr_s = web_traffic.groupby('traffic_source').agg({'sessions': 'sum', 'bounce_rate': 'mean'})
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(tr_s['sessions']/1e6, tr_s['bounce_rate'], s=tr_s['sessions']/5e4, c=tr_s['bounce_rate'], cmap='RdYlGn_r', edgecolor=PALETTE['ink'])
master_ax(ax, "ENGAGEMENT EFFICIENCY MATRIX", xlabel="Total Sessions (Millions)", ylabel="Avg Bounce Rate (%)")
for i, txt in enumerate(tr_s.index):
    ax.annotate(txt, (tr_s['sessions'].iloc[i]/1e6, tr_s['bounce_rate'].iloc[i]), xytext=(5,5), textcoords='offset points', fontweight='bold')
plt.savefig(f'{OUTPUT_DIR_03}/conversion_matrix.png', dpi=300, bbox_inches='tight')
plt.close()

# Fig 13: Financial Velocity
pm_s = payments.groupby('installments')['payment_value'].mean()
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(pm_s.index.astype(str), pm_s.values / 1e3, color=PALETTE['gold'], edgecolor=PALETTE['ink'])
master_ax(ax, "FINANCIAL VELOCITY", xlabel="Installment Tier", ylabel="AOV (K VND)")
plt.savefig(f'{OUTPUT_DIR_04}/financial_velocity.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# FIG 14: MAY PRODUCTS/GENRE (Year-over-Year Analysis)
# ----------------------------------------------------------------------------
print("[14/14] Fig 14: Rendering May Products/Genre Analysis...")

# Join orders with order_items and products to get May data by category
orders_items = orders.merge(order_items, on='order_id')
orders_items = orders_items.merge(products[['product_id', 'category', 'segment', 'product_name', 'size', 'color']], on='product_id')

# Filter for May orders across all years
orders_items['month'] = orders_items['order_date'].dt.month
orders_items['year'] = orders_items['order_date'].dt.year
may_data = orders_items[orders_items['month'] == 5].copy()

# Calculate revenue for each order item
may_data['item_revenue'] = may_data['unit_price'] * may_data['quantity']

# Aggregate by category (genre) for May
may_cat = may_data.groupby('category')['item_revenue'].sum().sort_values(ascending=False)

# Also get top products in May
may_prod = may_data.groupby('product_name')['item_revenue'].sum().sort_values(ascending=False).head(10)

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Left: Category/Genre in May
ax1 = axes[0]
bars1 = ax1.bar(range(len(may_cat)), may_cat.values / 1e6, color=PALETTE['context'], edgecolor=PALETTE['ink'])
ax1.set_xticks(range(len(may_cat)))
ax1.set_xticklabels(may_cat.index, rotation=30, ha='right', fontweight='bold')
master_ax(ax1, "MAY GENRE DOMINANCE", xlabel="Category", ylabel="Revenue (M VND)")

# Annotate with values
for i, v in enumerate(may_cat.values):
    ax1.text(i, v/1e6 + 0.5, f'{v/1e6:.1f}M', ha='center', fontsize=9, fontweight='bold')

# Right: Top 10 Products in May
ax2 = axes[1]
may_prod_rev = may_prod.sort_values(ascending=True)
ax2.barh(range(len(may_prod_rev)), may_prod_rev.values / 1e6, color=PALETTE['authority'], edgecolor=PALETTE['ink'])
ax2.set_yticks(range(len(may_prod_rev)))
ax2.set_yticklabels([p.replace(' ', '\n') if len(p) > 15 else p for p in may_prod_rev.index], fontsize=8)
master_ax(ax2, "MAY TOP 10 PRODUCTS", xlabel="Revenue (M VND)", ylabel="Product")

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR_01}/may_products.png', dpi=300, bbox_inches='tight')
plt.close()

# # ----------------------------------------------------------------------------
# # FIG 15-24: TOP 10 PRODUCTS - SIZE AND COLOR BREAKDOWN (COMMENTED OUT)
# # ----------------------------------------------------------------------------
# print("[15-24/24] Fig 15-24: Rendering Top 10 Products - Size & Color Breakdown...")

# # Get top 10 products in May
# top_10_products = may_prod.head(10).index.tolist()

# # Create output directory
# import os
# os.makedirs(TOP_PROD_DIR, exist_ok=True)

# # Create a color palette for sizes
# size_colors = {'S': '#4CAF50', 'M': '#2196F3', 'L': '#FF9800', 'XL': '#9C27B0', 'XXL': '#E91E63'}

# # Create a color palette for product colors
# product_color_palette = {
#     'red': '#F44336', 'blue': '#2196F3', 'green': '#4CAF50', 'black': '#212121',
#     'white': '#FAFAFA', 'yellow': '#FFEB3B', 'purple': '#9C27B0', 'orange': '#FF9800',
#     'pink': '#E91E63', 'silver': '#BDBDBD', 'brown': '#795548', 'gray': '#9E9E9E'
# }

# for idx, product_name in enumerate(top_10_products, start=15):
#     # Filter data for this product
#     prod_data = may_data[may_data['product_name'] == product_name].copy()
    
#     # Size breakdown
#     size_rev = prod_data.groupby('size')['item_revenue'].sum().sort_values(ascending=False)
    
#     # Color breakdown
#     color_rev = prod_data.groupby('color')['item_revenue'].sum().sort_values(ascending=False)
    
#     fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
#     # Left: Size distribution
#     ax1 = axes[0]
#     size_labels = size_rev.index.tolist()
#     size_vals = size_rev.values / 1e6
#     size_colors_list = [size_colors.get(s, PALETTE['context']) for s in size_labels]
#     bars1 = ax1.bar(range(len(size_labels)), size_vals, color=size_colors_list, edgecolor=PALETTE['ink'])
#     ax1.set_xticks(range(len(size_labels)))
#     ax1.set_xticklabels(size_labels, fontweight='bold', fontsize=12)
#     master_ax(ax1, f"SIZE DISTRIBUTION", xlabel="Size", ylabel="Revenue (M VND)")
    
#     # Add value labels
#     for i, v in enumerate(size_vals):
#         ax1.text(i, v + 0.1, f'{v:.1f}M', ha='center', fontsize=9, fontweight='bold')
    
#     # Right: Color distribution
#     ax2 = axes[1]
#     color_labels = color_rev.index.tolist()
#     color_vals = color_rev.values / 1e6
#     color_colors_list = [product_color_palette.get(c.lower(), PALETTE['context']) for c in color_labels]
#     bars2 = ax2.bar(range(len(color_labels)), color_vals, color=color_colors_list, edgecolor=PALETTE['ink'])
#     ax2.set_xticks(range(len(color_labels)))
#     ax2.set_xticklabels([c.capitalize() for c in color_labels], rotation=45, ha='right', fontweight='bold')
#     master_ax(ax2, f"COLOR DISTRIBUTION", xlabel="Color", ylabel="Revenue (M VND)")
    
#     # Add value labels
#     for i, v in enumerate(color_vals):
#         ax2.text(i, v + 0.1, f'{v:.1f}M', ha='center', fontsize=9, fontweight='bold')
    
#     # Main title
#     prod_short = product_name[:25] + '...' if len(product_name) > 25 else product_name
#     fig.suptitle(f"TOP PRODUCT #{idx-14}: {prod_short}", fontsize=14, fontweight='bold', color=PALETTE['authority'], y=1.02)
    
#     plt.tight_layout()
#     # Save with numbered filename
#     plt.savefig(f'{TOP_PROD_DIR}/top_product_{idx-14:02d}_size_color.png', dpi=300, bbox_inches='tight')
#     plt.close()
#     print(f"  Generated: top_product_{idx-14:02d}_size_color.png")

# ----------------------------------------------------------------------------
# FIG 25: SAIGONFLEX ATTRIBUTE ANALYSIS (Size, Color, Price, COGS)
# ----------------------------------------------------------------------------
print("[25/25] Fig 25: Rendering SaigonFlex Attribute Analysis...")

# Filter for SaigonFlex products
saigonflex = products[products['product_name'].str.startswith('SaigonFlex', na=False)].copy()

product_color_palette = {
    'red': '#F44336', 'blue': '#2196F3', 'green': '#4CAF50', 'black': '#212121',
    'white': '#FAFAFA', 'yellow': '#FFEB3B', 'purple': '#9C27B0', 'orange': '#FF9800',
    'pink': '#E91E63', 'silver': '#BDBDBD', 'brown': '#795548', 'gray': '#9E9E9E'
}

# Create figure with 4 subplots
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 1. Size distribution (count and avg price)
ax1 = axes[0, 0]
size_stats = saigonflex.groupby('size').agg({
    'product_id': 'count',
    'price': 'mean',
    'cogs': 'mean'
}).rename(columns={'product_id': 'count'})
x = range(len(size_stats))
bars1 = ax1.bar(x, size_stats['count'], color=PALETTE['context'], edgecolor=PALETTE['ink'])
ax1.set_xticks(x)
ax1.set_xticklabels(size_stats.index, fontweight='bold', fontsize=12)
master_ax(ax1, "SIZE DISTRIBUTION (Count)", xlabel="Size", ylabel="Product Count")
for i, v in enumerate(size_stats['count']):
    ax1.text(i, v + 5, str(v), ha='center', fontsize=10, fontweight='bold')

# 2. Color distribution (count)
ax2 = axes[0, 1]
color_counts = saigonflex['color'].value_counts()
color_colors_list = [product_color_palette.get(c.lower(), PALETTE['context']) for c in color_counts.index]
bars2 = ax2.bar(range(len(color_counts)), color_counts.values, color=color_colors_list, edgecolor=PALETTE['ink'])
ax2.set_xticks(range(len(color_counts)))
ax2.set_xticklabels([c.capitalize() for c in color_counts.index], rotation=45, ha='right', fontweight='bold')
master_ax(ax2, "COLOR DISTRIBUTION (Count)", xlabel="Color", ylabel="Product Count")
for i, v in enumerate(color_counts.values):
    ax2.text(i, v + 10, str(v), ha='center', fontsize=9, fontweight='bold')

# 3. Price distribution by Size
ax3 = axes[1, 0]
size_order = ['S', 'M', 'L', 'XL', 'XXL']
size_price = saigonflex.groupby('size')['price'].mean().reindex([s for s in size_order if s in saigonflex['size'].unique()])
bars3 = ax3.bar(range(len(size_price)), size_price.values / 1e3, color=PALETTE['authority'], edgecolor=PALETTE['ink'])
ax3.set_xticks(range(len(size_price)))
ax3.set_xticklabels(size_price.index, fontweight='bold', fontsize=12)
master_ax(ax3, "AVERAGE PRICE BY SIZE", xlabel="Size", ylabel="Avg Price (K VND)")
for i, v in enumerate(size_price.values):
    ax3.text(i, v/1e3 + 0.2, f'{v/1e3:.1f}K', ha='center', fontsize=10, fontweight='bold')

# 4. COGS vs Price scatter by Size
ax4 = axes[1, 1]
size_marker = {'S': 'o', 'M': 's', 'L': '^', 'XL': 'D', 'XXL': 'v'}
size_color_map = {'S': '#4CAF50', 'M': '#2196F3', 'L': '#FF9800', 'XL': '#9C27B0', 'XXL': '#E91E63'}
for size in saigonflex['size'].unique():
    subset = saigonflex[saigonflex['size'] == size]
    ax4.scatter(subset['price']/1e3, subset['cogs']/1e3, 
                label=size, alpha=0.6, s=50, c=size_color_map.get(size, PALETTE['context']),
                marker=size_marker.get(size, 'o'))
# Add profit margin line
ax4.plot([0, 20], [0, 20], 'k--', alpha=0.3, label='0% margin')
ax4.plot([0, 20], [0, 15], 'r--', alpha=0.3, label='25% margin')
master_ax(ax4, "PRICE vs COGS BY SIZE", xlabel="Price (K VND)", ylabel="COGS (K VND)")
ax4.legend(title='Size', loc='upper left', fontsize=8)

fig.suptitle("SAIGONFLEX PRODUCT ATTRIBUTE ANALYSIS", fontsize=16, fontweight='bold', color=PALETTE['authority'], y=1.02)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR_01}/saigonflex_attributes.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# FIG 26: PROFIT MARGIN BY SIZE (All Products)
# ----------------------------------------------------------------------------
print("[26/26] Fig 26: Rendering Profit Margin by Size Analysis...")

# Calculate margin for all products
products['margin'] = (products['price'] - products['cogs']) / products['price'] * 100
products['profit'] = products['price'] - products['cogs']

# Margin by size - all products
size_margin = products.groupby('size').agg({
    'margin': 'mean',
    'profit': 'mean',
    'price': 'mean',
    'cogs': 'mean',
    'product_id': 'count'
}).rename(columns={'product_id': 'count'}).sort_values('margin', ascending=False)

fig, axes = plt.subplots(1, 3, figsize=(16, 6))

# Panel 1: Average Margin % by Size
ax1 = axes[0]
size_order = ['S', 'M', 'L', 'XL', 'XXL']
margin_vals = [size_margin.loc[s, 'margin'] if s in size_margin.index else 0 for s in size_order]
colors = [size_color_map.get(s, PALETTE['context']) for s in size_order]
bars1 = ax1.bar(size_order, margin_vals, color=colors, edgecolor=PALETTE['ink'])
ax1.axhline(y=30, color='red', linestyle='--', alpha=0.7, label='30% target')
master_ax(ax1, "AVG PROFIT MARGIN % BY SIZE", xlabel="Size", ylabel="Margin (%)")
for i, v in enumerate(margin_vals):
    ax1.text(i, v + 0.5, f'{v:.1f}%', ha='center', fontsize=11, fontweight='bold')
ax1.legend()

# Panel 2: Average Profit (VND) by Size
ax2 = axes[1]
profit_vals = [size_margin.loc[s, 'profit'] if s in size_margin.index else 0 for s in size_order]
bars2 = ax2.bar(size_order, profit_vals, color=colors, edgecolor=PALETTE['ink'])
master_ax(ax2, "AVG PROFIT (VND) BY SIZE", xlabel="Size", ylabel="Profit (VND)")
for i, v in enumerate(profit_vals):
    ax2.text(i, v + 50, f'{v:,.0f}', ha='center', fontsize=10, fontweight='bold')

# Panel 3: Product Count & Avg Price by Size
ax3 = axes[2]
x = np.arange(len(size_order))
width = 0.35
count_vals = [size_margin.loc[s, 'count'] if s in size_margin.index else 0 for s in size_order]
price_vals = [size_margin.loc[s, 'price'] if s in size_margin.index else 0 for s in size_order]
ax3_twin = ax3.twinx()
bars3 = ax3.bar(x - width/2, count_vals, width, label='Product Count', color=PALETTE['context'], edgecolor=PALETTE['ink'])
bars4 = ax3_twin.bar(x + width/2, [p/1e3 for p in price_vals], width, label='Avg Price (K)', color=PALETTE['authority'], edgecolor=PALETTE['ink'])
ax3.set_xticks(x)
ax3.set_xticklabels(size_order, fontweight='bold')
master_ax(ax3, "PRODUCT COUNT & AVG PRICE", xlabel="Size", ylabel="Product Count")
ax3_twin.set_ylabel("Avg Price (K VND)", color=PALETTE['authority'], fontweight='bold')
ax3.legend(loc='upper left')
ax3_twin.legend(loc='upper right')

fig.suptitle("PROFIT MARGIN ANALYSIS BY SIZE", fontsize=16, fontweight='bold', color=PALETTE['authority'], y=1.02)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR_01}/margin_by_size.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# FIG 27: PAYMENT TYPES ANALYSIS
# ----------------------------------------------------------------------------
print("[27/27] Fig 27: Rendering Payment Types Analysis...")

# Load payments data
payments = pd.read_csv(f'{INPUT_DIR}/payments.csv')
orders = pd.read_csv(f'{INPUT_DIR}/orders.csv', parse_dates=['order_date'])
products = pd.read_csv(f'{INPUT_DIR}/products.csv')
geography = pd.read_csv(f'{INPUT_DIR}/geography.csv')
web_traffic = pd.read_csv(f'{INPUT_DIR}/web_traffic.csv', parse_dates=['date'])
order_items = pd.read_csv(f'{INPUT_DIR}/order_items.csv')

# Payment method distribution
pm_dist = payments['payment_method'].value_counts()

# Payment by geography (region)
orders_geo = orders.drop(columns=['payment_method']).merge(geography, on='zip')
orders_pay = orders_geo.merge(payments[['order_id', 'payment_method']], on='order_id')
pm_by_region = orders_pay.groupby(['region', 'payment_method']).size().unstack(fill_value=0)

# Payment by top products
orders_items = orders.drop(columns=['payment_method']).merge(order_items, on='order_id')
orders_items = orders_items.merge(products[['product_id', 'product_name']], on='product_id')
orders_items_pay = orders_items.merge(payments[['order_id', 'payment_method', 'payment_value']], on='order_id')
top_products = orders_items_pay.groupby('product_name')['payment_value'].sum().sort_values(ascending=False).head(10).index
pm_by_product = orders_items_pay[orders_items_pay['product_name'].isin(top_products)].groupby(['product_name', 'payment_method']).size().unstack(fill_value=0)

# Payment by traffic source
orders_pay_traffic = orders.drop(columns=['payment_method']).merge(web_traffic[['date', 'traffic_source']], left_on='order_date', right_on='date')
orders_pay_traffic = orders_pay_traffic.merge(payments[['order_id', 'payment_method']], on='order_id')
pm_by_traffic = orders_pay_traffic.groupby(['traffic_source', 'payment_method']).size().unstack(fill_value=0)

fig = plt.figure(figsize=(18, 14))

# Panel 1: Payment Method Distribution
ax1 = fig.add_subplot(2, 2, 1)
colors_pm = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#E91E63']
wedges, texts, autotexts = ax1.pie(pm_dist, labels=pm_dist.index, autopct='%1.1f%%', 
                                    colors=colors_pm[:len(pm_dist)], startangle=90)
ax1.set_title("PAYMENT METHOD DISTRIBUTION", fontsize=14, fontweight='bold', color=PALETTE['authority'])
for autotext in autotexts:
    autotext.set_fontweight('bold')

# Panel 2: Payment by Geography (heatmap)
ax2 = fig.add_subplot(2, 2, 2)
pm_by_region_pct = pm_by_region.div(pm_by_region.sum(axis=1), axis=0) * 100
im = ax2.imshow(pm_by_region_pct.values, cmap='Blues', aspect='auto')
ax2.set_xticks(range(len(pm_by_region.columns)))
ax2.set_xticklabels(pm_by_region.columns, rotation=45, ha='right', fontweight='bold')
ax2.set_yticks(range(len(pm_by_region.index)))
ax2.set_yticklabels(pm_by_region.index, fontweight='bold')
ax2.set_title("PAYMENT BY REGION (%)", fontsize=14, fontweight='bold', color=PALETTE['authority'])
for i in range(len(pm_by_region.index)):
    for j in range(len(pm_by_region.columns)):
        val = pm_by_region_pct.iloc[i, j]
        if val > 0:
            ax2.text(j, i, f'{val:.0f}%', ha='center', va='center', color='white' if val > 30 else 'black', fontsize=9)
plt.colorbar(im, ax=ax2, label='%')

# Panel 3: Payment by Top Products (heatmap)
ax3 = fig.add_subplot(2, 2, 3)
pm_by_product_pct = pm_by_product.div(pm_by_product.sum(axis=1), axis=0) * 100
im3 = ax3.imshow(pm_by_product_pct.values, cmap='Greens', aspect='auto')
ax3.set_xticks(range(len(pm_by_product.columns)))
ax3.set_xticklabels(pm_by_product.columns, rotation=45, ha='right', fontweight='bold')
ax3.set_yticks(range(len(pm_by_product.index)))
short_names = [n[:20] + '...' if len(n) > 20 else n for n in pm_by_product.index]
ax3.set_yticklabels(short_names, fontsize=8)
ax3.set_title("PAYMENT BY TOP 10 PRODUCTS (%)", fontsize=14, fontweight='bold', color=PALETTE['authority'])
plt.colorbar(im3, ax=ax3, label='%')

# Panel 4: Payment by Traffic Source
ax4 = fig.add_subplot(2, 2, 4)
pm_by_traffic_pct = pm_by_traffic.div(pm_by_traffic.sum(axis=1), axis=0) * 100
im4 = ax4.imshow(pm_by_traffic_pct.values, cmap='Oranges', aspect='auto')
ax4.set_xticks(range(len(pm_by_traffic.columns)))
ax4.set_xticklabels(pm_by_traffic.columns, rotation=45, ha='right', fontweight='bold')
ax4.set_yticks(range(len(pm_by_traffic.index)))
ax4.set_yticklabels(pm_by_traffic.index, fontsize=9)
ax4.set_title("PAYMENT BY TRAFFIC SOURCE (%)", fontsize=14, fontweight='bold', color=PALETTE['authority'])
plt.colorbar(im4, ax=ax4, label='%')

fig.suptitle("PAYMENT TYPES ANALYSIS: GEOGRAPHY, PRODUCTS & TRAFFIC", fontsize=16, fontweight='bold', color=PALETTE['authority'], y=1.02)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR_04}/payment_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

print("\nLONGITUDINAL MASTER SUITE REGENERATED.")
print("="*60)
