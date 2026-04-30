#!/usr/bin/env python3
"""
Operational Friction & Leakage - Deep Analysis
Theme: "The Forensic Audit - Operational Intelligence"
Focus: Identifying bottlenecks, revenue leakage, and operational inefficiencies
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import warnings
import os

warnings.filterwarnings('ignore')

# Helper functions for professional styling
def apply_editorial_style(fig, ax, title, subtitle):
    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color('#CBD5E1')
    ax.spines['bottom'].set_linewidth(1.5)
    ax.tick_params(axis='both', which='both', length=0, labelsize=11, colors='#64748B')
    ax.grid(axis='y', color='#F1F5F9', linewidth=1.5, linestyle='-')
    ax.set_axisbelow(True)
    fig.text(0.04, 0.95, title.upper(), fontsize=20, fontweight='black', color='#0F172A')
    fig.text(0.04, 0.90, subtitle, fontsize=12, color='#64748B')
    plt.subplots_adjust(top=0.82, bottom=0.12, left=0.08, right=0.95)

def add_callout(ax, text, xy, xytext, color='#0F172A', arrow_color='#64748B'):
    ax.annotate(text, xy=xy, xytext=xytext,
                arrowprops=dict(arrowstyle="->", color=arrow_color, lw=1.5, connectionstyle="arc3,rad=0.2"),
                color=color, fontweight="600", ha="center", fontsize=11,
                bbox=dict(boxstyle="round,pad=0.6,rounding_size=0.3", facecolor="#FFFFFF", 
                          edgecolor="#E2E8F0", alpha=0.95, lw=1))

def annotate_output(path):
    pass

PALETTE = {
    'authority': '#16A34A',    # brand green
    'context':   '#93FA64',    # soft green highlight
    'friction':  '#DC2626',    # alert red
    'gold':      '#F59E0B',    # amber accent
    'highlight': '#DCFCE7',    # pale green wash
    'paper':     '#FFFFFF',    # Clean White
    'ink':       '#0F172A',    # slate
    'grid':      '#D1D1D1',
}

cmap_navy = LinearSegmentedColormap.from_list('MasterNavy', [PALETTE['paper'], PALETTE['authority']])
cmap_red = LinearSegmentedColormap.from_list('MasterRed', [PALETTE['paper'], PALETTE['friction']])

plt.rcParams['font.family'] = 'sans-serif'
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

INPUT_DIR = '/home/shayneeo/Downloads/Datathon/input'
OUTPUT_DIR = '/home/shayneeo/Downloads/Datathon/output/figures_living/03_operational_friction_leakage'

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*60)
print("OPERATIONAL FRICTION & LEAKAGE - DEEP ANALYSIS")
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
shipments = pd.read_csv(f'{INPUT_DIR}/shipments.csv', parse_dates=['ship_date', 'delivery_date'])

# Merge fundamental data
orders_items = orders.merge(order_items, on='order_id')
orders_items = orders_items.merge(products, on='product_id')
orders_items['revenue'] = orders_items['unit_price'] * orders_items['quantity']

# ----------------------------------------------------------------------------
# ASSET 1: RETURN DEEP DIVE - Category, Size, Color, Region
# ----------------------------------------------------------------------------
print("[1/10] Asset 1: Rendering Return Deep Dive...")

returns_items = returns.merge(order_items[['order_id', 'product_id']], on='order_id', suffixes=('_return', '_item'))
returns_items = returns_items.merge(products[['product_id', 'category', 'size', 'color']], left_on='product_id_item', right_on='product_id')
returns_geo = returns_items.merge(orders[['order_id', 'zip']], on='order_id').merge(geography, on='zip')

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Returns by category
ax1 = axes[0, 0]
ret_cat = returns_items['category'].value_counts()
ax1.bar(ret_cat.index, ret_cat.values, color=PALETTE['friction'], edgecolor=PALETTE['ink'])
master_ax(ax1, "RETURNS BY CATEGORY", xlabel="Category", ylabel="Return Count")

# Returns by size
ax2 = axes[0, 1]
ret_size = returns_items['size'].value_counts()
ax2.bar(ret_size.index, ret_size.values, color=PALETTE['context'], edgecolor=PALETTE['ink'])
master_ax(ax2, "RETURNS BY SIZE", xlabel="Size", ylabel="Return Count")

# Returns by color (top 10)
ax3 = axes[1, 0]
ret_color = returns_items['color'].value_counts().head(10)
ax3.barh(ret_color.index, ret_color.values, color=PALETTE['gold'], edgecolor=PALETTE['ink'])
master_ax(ax3, "RETURNS BY COLOR (TOP 10)", xlabel="Return Count", ylabel="Color")

# Returns by region
ax4 = axes[1, 1]
ret_region = returns_geo['region'].value_counts()
ax4.bar(ret_region.index, ret_region.values, color=PALETTE['authority'], edgecolor=PALETTE['ink'])
master_ax(ax4, "RETURNS BY REGION", xlabel="Region", ylabel="Return Count")

# Professional Styling
apply_editorial_style(fig, axes[0,0], "Returns Analysis: The Sizing Crisis", "Wrong size remains the #1 driver of reverse logistics friction")

# Native callouts
add_callout(axes[0,0], "Wrong-size drives returns", xy=(0.5, ret_cat.max() * 0.75), xytext=(1.5, ret_cat.max() * 0.45), color='#DC2626')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/return_deep_dive.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# ASSET 2: RETURN REASON MATRIX - Category vs Reason
# ----------------------------------------------------------------------------
print("[2/10] Asset 2: Rendering Return Reason Matrix...")

return_pivot = returns_items.groupby(['category', 'return_reason']).size().unstack(fill_value=0)

fig, ax = plt.subplots(figsize=(14, 8))
im = ax.imshow(return_pivot, cmap=cmap_red, aspect='auto')
ax.set_xticks(np.arange(len(return_pivot.columns)))
ax.set_xticklabels(return_pivot.columns, rotation=45, ha='right', fontweight='bold')
ax.set_yticks(np.arange(len(return_pivot.index)))
ax.set_yticklabels(return_pivot.index, fontweight='bold')
master_ax(ax, "RETURN REASON MATRIX", subtitle="Volume of returns by Category and Reason", xlabel="Reason", ylabel="Category")

for i in range(len(return_pivot.index)):
    for j in range(len(return_pivot.columns)):
        val = return_pivot.iloc[i, j]
        if val > 0:
            ax.text(j, i, str(val), ha='center', va='center', color='white' if val > return_pivot.values.max()/2 else 'black', fontsize=10, fontweight='bold')

plt.colorbar(im, ax=ax, label='Return Count')
plt.savefig(f'{OUTPUT_DIR}/return_reason_matrix.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# ASSET 3: INVENTORY STOCKOUT ANALYSIS - Revenue Impact
# ----------------------------------------------------------------------------
print("[3/10] Asset 3: Rendering Inventory Stockout Analysis...")

# Aggregate inventory data
inv_agg = inventory.groupby('product_id').agg({
    'stockout_days': 'sum',
    'fill_rate': 'mean',
    'stockout_flag': 'sum',
    'overstock_flag': 'sum'
}).reset_index()

# Get product revenue
prod_rev = orders_items.groupby('product_id').agg({
    'revenue': 'sum',
    'order_id': 'nunique'
}).rename(columns={'order_id': 'order_count'}).reset_index()

# Merge
risk_df = inv_agg.merge(prod_rev, on='product_id')
risk_df = risk_df.merge(products[['product_id', 'category', 'product_name']], on='product_id')

# Calculate revenue per stockout day
risk_df['revenue_per_stockout_day'] = risk_df['revenue'] / (risk_df['stockout_days'] + 1)

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Stockout days vs revenue
ax1 = axes[0]
scatter1 = ax1.scatter(risk_df['stockout_days'], risk_df['revenue'], 
                      s=risk_df['fill_rate']*100, c=risk_df['revenue'], 
                      cmap='viridis', alpha=0.6, edgecolors=PALETTE['ink'])
master_ax(ax1, "STOCKOUT DAYS VS REVENUE", subtitle="Bubble size = Fill Rate; Color = Revenue", 
          xlabel="Cumulative Stockout Days", ylabel="Total Product Revenue (VND)")
plt.colorbar(scatter1, ax=ax1, label='Revenue (VND)')

# Top 20 products by stockout days
ax2 = axes[1]
top_stockout = risk_df.nlargest(20, 'stockout_days')
ax2.barh(range(len(top_stockout)), top_stockout['stockout_days'], color=PALETTE['friction'], edgecolor=PALETTE['ink'])
ax2.set_yticks(range(len(top_stockout)))
ax2.set_yticklabels([p[:25] + '...' if len(p) > 25 else p for p in top_stockout['product_name']], fontsize=8)
master_ax(ax2, "TOP 20 PRODUCTS BY STOCKOUT DAYS", xlabel="Cumulative Stockout Days", ylabel="Product")

# Professional Styling
apply_editorial_style(fig, axes[0], "Inventory Risk: Stockout vs Revenue", "High-revenue 'hero' products face significant leakage risk")

# Native callout
add_callout(axes[0], "Hero product revenue leakage", xy=(15, 1e7), xytext=(40, 1.5e7), color='#DC2626')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/inventory_stockout_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# ASSET 4: SHIPPING & DELIVERY EFFICIENCY
# ----------------------------------------------------------------------------
print("[4/10] Asset 4: Rendering Shipping & Delivery Efficiency...")

# Calculate delivery time
shipments['delivery_days'] = (shipments['delivery_date'] - shipments['ship_date']).dt.days

# Merge with orders and geography
ship_geo = shipments.merge(orders[['order_id', 'zip']], on='order_id').merge(geography, on='zip')

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Delivery time distribution
ax1 = axes[0]
ax1.hist(shipments['delivery_days'], bins=30, color=PALETTE['context'], edgecolor=PALETTE['ink'])
ax1.axvline(shipments['delivery_days'].mean(), color=PALETTE['friction'], linestyle='--', linewidth=2, label=f'Mean: {shipments["delivery_days"].mean():.1f} days')
master_ax(ax1, "DELIVERY TIME DISTRIBUTION", xlabel="Delivery Days", ylabel="Order Count")
ax1.legend()

# Delivery time by region
ax2 = axes[1]
region_delivery = ship_geo.groupby('region')['delivery_days'].agg(['mean', 'median']).sort_values('mean')
x = np.arange(len(region_delivery))
width = 0.35
ax2.bar(x - width/2, region_delivery['mean'], width, label='Mean', color=PALETTE['authority'], edgecolor=PALETTE['ink'])
ax2.bar(x + width/2, region_delivery['median'], width, label='Median', color=PALETTE['gold'], edgecolor=PALETTE['ink'])
ax2.set_xticks(x)
ax2.set_xticklabels(region_delivery.index, fontweight='bold')
master_ax(ax2, "DELIVERY TIME BY REGION", xlabel="Region", ylabel="Days")
ax2.legend()

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/shipping_delivery_efficiency.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# ASSET 5: ORDER STATUS FLOW ANALYSIS
# ----------------------------------------------------------------------------
print("[5/10] Asset 5: Rendering Order Status Flow Analysis...")

# Order status distribution
status_dist = orders['order_status'].value_counts()

# Order status by month
orders['month'] = orders['order_date'].dt.month
orders['year'] = orders['order_date'].dt.year
status_month = orders.groupby(['year', 'month', 'order_status']).size().unstack(fill_value=0)

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Status distribution
ax1 = axes[0]
ax1.pie(status_dist, labels=status_dist.index, autopct='%1.1f%%', startangle=140, 
        colors=cm.Pastel1.colors)
ax1.set_title("ORDER STATUS DISTRIBUTION", fontsize=14, fontweight='bold', color=PALETTE['authority'])

# Status trend over time
ax2 = axes[1]
for status in status_dist.index:
    if status in status_month.columns:
        ax2.plot(range(len(status_month)), status_month[status], label=status, linewidth=2)
ax2.set_xticks(range(0, len(status_month), 12))
ax2.set_xticklabels([f"{status_month.index[i][0]}" for i in range(0, len(status_month), 12)], rotation=45)
master_ax(ax2, "ORDER STATUS TREND", xlabel="Time (Months)", ylabel="Order Count")
ax2.legend()

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/order_status_flow.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# ASSET 6: WEB TRAFFIC VS CONVERSION GAP
# ----------------------------------------------------------------------------
print("[6/10] Asset 6: Rendering Web Traffic vs Conversion Gap...")

# Calculate daily metrics
traffic_daily = web_traffic.groupby('date').agg({
    'sessions': 'sum',
    'unique_visitors': 'sum',
    'bounce_rate': 'mean'
}).reset_index()

# Get daily orders
orders_daily = orders.groupby('order_date').size().reset_index(name='order_count')

# Merge
funnel_data = traffic_daily.merge(orders_daily, left_on='date', right_on='order_date', how='left').fillna(0)

# Calculate conversion rate from available data
funnel_data['conversion_rate'] = funnel_data['order_count'] / funnel_data['sessions']

# Calculate conversion gap (potential orders if conversion rate was at peak)
peak_conversion = funnel_data['conversion_rate'].max()
funnel_data['potential_orders'] = funnel_data['sessions'] * peak_conversion
funnel_data['conversion_gap'] = funnel_data['potential_orders'] - funnel_data['order_count']

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Sessions vs Orders
ax1 = axes[0, 0]
ax1.plot(funnel_data['date'], funnel_data['sessions'], color=PALETTE['context'], label='Sessions', linewidth=2)
ax1_twin = ax1.twinx()
ax1_twin.plot(funnel_data['date'], funnel_data['order_count'], color=PALETTE['friction'], label='Orders', linewidth=2)
master_ax(ax1, "SESSIONS VS ORDERS", xlabel="Date", ylabel="Sessions")
ax1_twin.set_ylabel("Orders", color=PALETTE['friction'], fontweight='bold')
ax1.legend(loc='upper left')
ax1_twin.legend(loc='upper right')

# Conversion rate trend
ax2 = axes[0, 1]
ax2.plot(funnel_data['date'], funnel_data['conversion_rate'] * 100, color=PALETTE['authority'], linewidth=2)
ax2.fill_between(funnel_data['date'], funnel_data['conversion_rate'] * 100, color=PALETTE['authority'], alpha=0.1)
ax2.axhline(y=peak_conversion * 100, color=PALETTE['friction'], linestyle='--', linewidth=2, label=f'Peak: {peak_conversion*100:.2f}%')
master_ax(ax2, "CONVERSION RATE TREND", xlabel="Date", ylabel="Conversion Rate (%)")
ax2.legend()

# Bounce rate vs Conversion rate
ax3 = axes[1, 0]
ax3.scatter(funnel_data['bounce_rate'], funnel_data['conversion_rate'], alpha=0.5, c=funnel_data['sessions'], cmap='viridis')
ax3.set_xlabel('Bounce Rate (%)', fontweight='bold')
ax3.set_ylabel('Conversion Rate (%)', fontweight='bold')
ax3.set_title("BOUNCE RATE VS CONVERSION RATE", fontsize=14, fontweight='bold', color=PALETTE['authority'])
plt.colorbar(ax3.collections[0], ax=ax3, label='Sessions')

# Conversion gap
ax4 = axes[1, 1]
ax4.plot(funnel_data['date'], funnel_data['conversion_gap'], color=PALETTE['friction'], linewidth=2)
ax4.fill_between(funnel_data['date'], funnel_data['conversion_gap'], color=PALETTE['friction'], alpha=0.1)
master_ax(ax4, "CONVERSION GAP (POTENTIAL LOST ORDERS)", xlabel="Date", ylabel="Lost Orders")

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/web_traffic_conversion_gap.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# ASSET 7: DEVICE VS CONVERSION ANALYSIS
# ----------------------------------------------------------------------------
print("[7/10] Asset 7: Rendering Device vs Conversion Analysis...")

# Device analysis
device_stats = orders.groupby('device_type').agg({
    'order_id': 'count',
    'customer_id': 'nunique'
}).rename(columns={'order_id': 'order_count', 'customer_id': 'unique_customers'})

# Calculate conversion rate by device (need to merge with web traffic)
# For now, we'll use order count as proxy
device_stats['orders_per_customer'] = device_stats['order_count'] / device_stats['unique_customers']

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Device distribution
ax1 = axes[0]
ax1.pie(device_stats['order_count'], labels=device_stats.index, autopct='%1.1f%%', startangle=140,
        colors=cm.Pastel1.colors)
ax1.set_title("ORDER VOLUME BY DEVICE", fontsize=14, fontweight='bold', color=PALETTE['authority'])

# Device efficiency
ax2 = axes[1]
x = np.arange(len(device_stats))
width = 0.35
ax2.bar(x - width/2, device_stats['order_count'], width, label='Total Orders', color=PALETTE['context'], edgecolor=PALETTE['ink'])
ax2_twin = ax2.twinx()
ax2_twin.bar(x + width/2, device_stats['orders_per_customer'], width, label='Orders/Customer', color=PALETTE['gold'], edgecolor=PALETTE['ink'])
ax2.set_xticks(x)
ax2.set_xticklabels(device_stats.index, fontweight='bold')
master_ax(ax2, "DEVICE EFFICIENCY", xlabel="Device", ylabel="Order Count")
ax2_twin.set_ylabel("Orders per Customer", color=PALETTE['gold'], fontweight='bold')
ax2.legend(loc='upper left')
ax2_twin.legend(loc='upper right')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/device_conversion_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# ASSET 8: GEOGRAPHIC LOGISTICS EFFICIENCY
# ----------------------------------------------------------------------------
print("[8/10] Asset 8: Rendering Geographic Logistics Efficiency...")

# Geographic analysis
geo_orders = orders.merge(geography, on='zip')
geo_stats = geo_orders.groupby('region').agg({
    'order_id': 'count',
    'zip': 'nunique'
}).rename(columns={'order_id': 'order_count', 'zip': 'unique_cities'})

# Get revenue by region
geo_items = orders_items.merge(geography, on='zip')
geo_rev = geo_items.groupby('region')['revenue'].sum()

# Merge
geo_final = geo_stats.merge(geo_rev, left_index=True, right_index=True)
geo_final['revenue_per_order'] = geo_final['revenue'] / geo_final['order_count']
geo_final['orders_per_city'] = geo_final['order_count'] / geo_final['unique_cities']

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Order volume by region
ax1 = axes[0, 0]
ax1.bar(geo_final.index, geo_final['order_count'], color=PALETTE['authority'], edgecolor=PALETTE['ink'])
master_ax(ax1, "ORDER VOLUME BY REGION", xlabel="Region", ylabel="Order Count")

# Revenue by region
ax2 = axes[0, 1]
ax2.bar(geo_final.index, geo_final['revenue'] / 1e6, color=PALETTE['gold'], edgecolor=PALETTE['ink'])
master_ax(ax2, "REVENUE BY REGION", xlabel="Region", ylabel="Revenue (M VND)")

# Revenue per order
ax3 = axes[1, 0]
ax3.bar(geo_final.index, geo_final['revenue_per_order'] / 1e3, color=PALETTE['context'], edgecolor=PALETTE['ink'])
master_ax(ax3, "REVENUE PER ORDER BY REGION", xlabel="Region", ylabel="Revenue per Order (K VND)")

# Orders per city (density)
ax4 = axes[1, 1]
ax4.bar(geo_final.index, geo_final['orders_per_city'], color=PALETTE['friction'], edgecolor=PALETTE['ink'])
master_ax(ax4, "ORDERS PER CITY (DENSITY)", xlabel="Region", ylabel="Orders per City")

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/geographic_logistics_efficiency.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# ASSET 9: SEASONAL OPERATIONAL PATTERNS
# ----------------------------------------------------------------------------
print("[9/10] Asset 9: Rendering Seasonal Operational Patterns...")

# Monthly analysis
orders['month'] = orders['order_date'].dt.month
orders['year'] = orders['order_date'].dt.year

monthly_stats = orders.groupby(['year', 'month']).agg({
    'order_id': 'count',
    'customer_id': 'nunique'
}).rename(columns={'order_id': 'order_count', 'customer_id': 'unique_customers'})

# Get monthly returns
returns['month'] = pd.to_datetime(returns['return_date']).dt.month
returns['year'] = pd.to_datetime(returns['return_date']).dt.year
monthly_returns = returns.groupby(['year', 'month']).size().reset_index(name='return_count')

# Merge
monthly_final = monthly_stats.reset_index().merge(monthly_returns, on=['year', 'month'], how='left').fillna(0)
monthly_final['return_rate'] = monthly_final['return_count'] / monthly_final['order_count'] * 100

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Monthly order trend
ax1 = axes[0, 0]
for year in sorted(monthly_final['year'].unique()):
    year_data = monthly_final[monthly_final['year'] == year]
    ax1.plot(year_data['month'], year_data['order_count'], label=str(year), linewidth=2)
master_ax(ax1, "MONTHLY ORDER TREND", xlabel="Month", ylabel="Order Count")
ax1.legend()

# Monthly return rate
ax2 = axes[0, 1]
for year in sorted(monthly_final['year'].unique()):
    year_data = monthly_final[monthly_final['year'] == year]
    ax2.plot(year_data['month'], year_data['return_rate'], label=str(year), linewidth=2)
master_ax(ax2, "MONTHLY RETURN RATE", xlabel="Month", ylabel="Return Rate (%)")
ax2.legend()

# Seasonal heatmap (orders)
ax3 = axes[1, 0]
seasonal_orders = monthly_final.pivot_table(index='month', columns='year', values='order_count', aggfunc='sum')
im3 = ax3.imshow(seasonal_orders, cmap=cmap_navy, aspect='auto')
ax3.set_xticks(np.arange(len(seasonal_orders.columns)))
ax3.set_xticklabels(seasonal_orders.columns, rotation=45, ha='right')
ax3.set_yticks(np.arange(len(seasonal_orders.index)))
ax3.set_yticklabels(seasonal_orders.index)
ax3.set_title("SEASONAL ORDERS HEATMAP", fontsize=14, fontweight='bold', color=PALETTE['authority'])
plt.colorbar(im3, ax=ax3)

# Seasonal heatmap (return rate)
ax4 = axes[1, 1]
seasonal_returns = monthly_final.pivot_table(index='month', columns='year', values='return_rate', aggfunc='mean')
im4 = ax4.imshow(seasonal_returns, cmap=cmap_red, aspect='auto')
ax4.set_xticks(np.arange(len(seasonal_returns.columns)))
ax4.set_xticklabels(seasonal_returns.columns, rotation=45, ha='right')
ax4.set_yticks(np.arange(len(seasonal_returns.index)))
ax4.set_yticklabels(seasonal_returns.index)
ax4.set_title("SEASONAL RETURN RATE HEATMAP", fontsize=14, fontweight='bold', color=PALETTE['authority'])
plt.colorbar(im4, ax=ax4)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/seasonal_operational_patterns.png', dpi=300, bbox_inches='tight')
plt.close()

# ----------------------------------------------------------------------------
# ASSET 10: CUSTOMER SATISFACTION VS OPERATIONAL METRICS
# ----------------------------------------------------------------------------
print("[10/10] Asset 10: Rendering Customer Satisfaction vs Operational Metrics...")

# Merge reviews with orders
reviews_orders = reviews.merge(orders[['order_id', 'order_date', 'zip']], on='order_id')
reviews_orders = reviews_orders.merge(geography, on='zip')

# Calculate delivery time for reviewed orders
reviews_ship = reviews_orders.merge(shipments[['order_id', 'delivery_days']], on='order_id', how='left')

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Rating distribution
ax1 = axes[0, 0]
rating_dist = reviews['rating'].value_counts().sort_index()
ax1.bar(rating_dist.index.astype(str), rating_dist.values, color=PALETTE['context'], edgecolor=PALETTE['ink'])
master_ax(ax1, "RATING DISTRIBUTION", xlabel="Rating (1-5)", ylabel="Review Count")

# Rating by category
ax2 = axes[0, 1]
reviews_items = reviews.merge(products[['product_id', 'category']], on='product_id')
rating_cat = reviews_items.groupby('category')['rating'].mean().sort_values()
ax2.barh(rating_cat.index, rating_cat.values, color=PALETTE['authority'], edgecolor=PALETTE['ink'])
ax2.set_xlim(0, 5)
master_ax(ax2, "AVERAGE RATING BY CATEGORY", xlabel="Average Rating", ylabel="Category")

# Rating vs delivery time
ax3 = axes[1, 0]
rating_delivery = reviews_ship.groupby('rating')['delivery_days'].mean()
ax3.bar(rating_delivery.index, rating_delivery.values, color=PALETTE['gold'], edgecolor=PALETTE['ink'])
master_ax(ax3, "RATING VS DELIVERY TIME", xlabel="Rating", ylabel="Avg Delivery Days")

# Rating by region
ax4 = axes[1, 1]
rating_region = reviews_orders.groupby('region')['rating'].mean().sort_values()
ax4.barh(rating_region.index, rating_region.values, color=PALETTE['friction'], edgecolor=PALETTE['ink'])
ax4.set_xlim(0, 5)
master_ax(ax4, "AVERAGE RATING BY REGION", xlabel="Average Rating", ylabel="Region")

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/customer_satisfaction_operational.png', dpi=300, bbox_inches='tight')
plt.close()

print("\nOPERATIONAL FRICTION & LEAKAGE ANALYSIS COMPLETE.")
print("="*60)
print(f"Generated 10 advanced operational intelligence assets in: {OUTPUT_DIR}")
print("="*60)

# ----------------------------------------------------------------------------
# ASSET 11: TET HOLIDAY & RECOVERY FRICTION
# ----------------------------------------------------------------------------
print("[11/11] Asset 11: Rendering Tet Holiday & Recovery Friction...")

orders['temporal_phase'] = 'Normal'
for year, tet_str in {2019: "2019-02-05", 2020: "2020-01-25", 2021: "2021-02-12", 2022: "2022-02-01"}.items():
    tet = pd.Timestamp(tet_str)
    approach = (orders["order_date"] >= tet - pd.Timedelta(days=21)) & (orders["order_date"] < tet)
    holiday  = (orders["order_date"] >= tet) & (orders["order_date"] < tet + pd.Timedelta(days=7))
    recovery = (orders["order_date"] >= tet + pd.Timedelta(days=7)) & (orders["order_date"] < tet + pd.Timedelta(days=21))
    
    orders.loc[approach, 'temporal_phase'] = 'Tet Approach (-21d)'
    orders.loc[holiday, 'temporal_phase'] = 'Tet Holiday (DIP)'
    orders.loc[recovery, 'temporal_phase'] = 'Tet Recovery (+14d)'

tet_orders = orders[orders['temporal_phase'] != 'Normal'].copy()
tet_orders = tet_orders.merge(shipments[['order_id', 'delivery_days']], on='order_id', how='left')

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Plot delivery times by Tet Phase
phase_order = ['Tet Approach (-21d)', 'Tet Holiday (DIP)', 'Tet Recovery (+14d)']
ax1 = axes[0]
sns.boxplot(data=tet_orders, x='temporal_phase', y='delivery_days', order=phase_order, palette=['#16A34A', '#DC2626', '#F59E0B'], ax=ax1, showfliers=False)
master_ax(ax1, "DELIVERY SLA BY TET PHASE", xlabel="Temporal Phase", ylabel="Delivery Days")

# Plot cancellation rates
ax2 = axes[1]
cancel_rates = tet_orders.groupby('temporal_phase').apply(lambda x: (x['order_status'] == 'cancelled').mean() * 100).reindex(phase_order)
ax2.bar(cancel_rates.index, cancel_rates.values, color=['#16A34A', '#DC2626', '#F59E0B'])
for i, v in enumerate(cancel_rates.values):
    ax2.text(i, v + 0.1, f'{v:.1f}%', ha='center', fontweight='bold')
master_ax(ax2, "CANCELLATION RATE BY TET PHASE", xlabel="Temporal Phase", ylabel="Cancellation Rate (%)")

# Professional Styling
apply_editorial_style(fig, axes[0], "Tet Logistics Friction: The Bullwhip Effect", "Backlog peaks in Recovery Phase, causing cancellation spikes")

# Native callout
add_callout(axes[1], "Backlog recovery bottleneck", xy=(2, 4), xytext=(2.2, 8), color='#DC2626')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/tet_holiday_friction.png', dpi=300, bbox_inches='tight')
plt.close()

annotate_output(f'{OUTPUT_DIR}/returns_bar.png')
annotate_output(f'{OUTPUT_DIR}/return_deep_dive.png')
annotate_output(f'{OUTPUT_DIR}/return_reason_matrix.png')
annotate_output(f'{OUTPUT_DIR}/inventory_risk_analysis.png')
annotate_output(f'{OUTPUT_DIR}/tet_holiday_friction.png')
annotate_output(f'{OUTPUT_DIR}/line_failure_rate.png')

print("\nOPERATIONAL FRICTION & LEAKAGE ANALYSIS COMPLETE (INCLUDING PART 3 ENHANCEMENTS).")
