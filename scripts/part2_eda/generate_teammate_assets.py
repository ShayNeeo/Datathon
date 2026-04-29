#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

INPUT_DIR = '/home/shayneeo/Downloads/Datathon/input'
OUTPUT_DIR = '/home/shayneeo/Downloads/Datathon/output/figures_living'
OUTPUT_DIR_01 = f'{OUTPUT_DIR}/01_product_market_dominance'
OUTPUT_DIR_02 = f'{OUTPUT_DIR}/02_customer_lifecycle_acquisition'
OUTPUT_DIR_03 = f'{OUTPUT_DIR}/03_operational_friction_leakage'
OUTPUT_DIR_04 = f'{OUTPUT_DIR}/04_financial_payment_dynamics'

PALETTE = {
    'authority': '#0072B2',
    'context':   '#56B4E9',
    'friction':  '#D55E00',
    'gold':      '#E69F00',
}

def apply_editorial_style(fig, ax, title, subtitle):
    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color('#CBD5E1')
    ax.spines['bottom'].set_linewidth(1.5)
    ax.tick_params(axis='both', which='both', length=0, labelsize=11, colors='#64748B')
    ax.grid(axis='y', color='#F1F5F9', linewidth=1.5, linestyle='-')
    fig.text(0.04, 0.95, title.upper(), fontsize=20, fontweight='black', color='#0F172A')
    fig.text(0.04, 0.90, subtitle, fontsize=12, color='#64748B')
    plt.subplots_adjust(top=0.82, bottom=0.12, left=0.08, right=0.95)

def add_callout(ax, text, xy, xytext, color='#0F172A'):
    ax.annotate(text, xy=xy, xytext=xytext,
                arrowprops=dict(arrowstyle='->', color='#64748B', lw=1.5, connectionstyle='arc3,rad=0.2'),
                color=color, fontweight='600', ha='center', fontsize=11,
                bbox=dict(boxstyle='round,pad=0.6', facecolor='#FFFFFF', edgecolor='#E2E8F0', alpha=0.95))

print('Porting all teammate insights...')
products = pd.read_csv(f"{INPUT_DIR}/products.csv")
order_items = pd.read_csv(f"{INPUT_DIR}/order_items.csv", low_memory=False)
orders = pd.read_csv(f"{INPUT_DIR}/orders.csv", parse_dates=['order_date'])
shipments = pd.read_csv(f"{INPUT_DIR}/shipments.csv")
sales = pd.read_csv(f"{INPUT_DIR}/sales.csv", parse_dates=['Date'])
promo = pd.read_csv(f"{INPUT_DIR}/promotions.csv", parse_dates=['start_date', 'end_date'])

# 1. Loss Leader
df_prod = products.copy()
df_prod['margin'] = (df_prod['price'] - df_prod['cogs']) / df_prod['price']
loss_ids = df_prod[df_prod['margin'] <= 0.055]['product_id'].unique()
df_items = order_items.merge(df_prod[['product_id', 'cogs']], on='product_id')
df_items['is_loss'] = df_items['product_id'].isin(loss_ids)
df_items['rev'] = df_items['unit_price'] * df_items['quantity'] - df_items['discount_amount'].fillna(0)
df_items['profit'] = df_items['rev'] - (df_items['quantity'] * df_items['cogs'])
stats = df_items.groupby('order_id').agg(has_loss=('is_loss', 'max'), total_rev=('rev', 'sum'), total_prof=('profit', 'sum')).reset_index()
grp = stats[stats['total_rev'] > 0].groupby('has_loss').agg(avg_rev=('total_rev', 'mean'), avg_prof=('total_prof', 'mean')).reset_index()
fig, ax = plt.subplots(figsize=(10, 6.5))
ax.bar(np.arange(2) - 0.17, grp['avg_rev'], 0.35, label='Avg Revenue', color='#E2E8F0')
ax.bar(np.arange(2) + 0.17, grp['avg_prof'], 0.35, label='Avg Profit', color=[PALETTE['authority'], PALETTE['friction']])
apply_editorial_style(fig, ax, 'The Loss Leader Trap', 'Sacrificing margin to drive volume is destroying profitability')
add_callout(ax, 'Loss-leader orders DESTROY profit', xy=(1.17, grp['avg_prof'].iloc[1]), xytext=(0.5, 5000), color=PALETTE['friction'])
os.makedirs(OUTPUT_DIR_01, exist_ok=True)
plt.savefig(f"{OUTPUT_DIR_01}/loss_leader_trap.png", dpi=300)

# 2. Logistics Paradox
df_ship = orders[['order_id', 'customer_id', 'order_date']].merge(shipments[['order_id', 'delivery_date']], on='order_id')
df_ship['delivery_date'] = pd.to_datetime(df_ship['delivery_date'])
df_ship['days'] = (df_ship['delivery_date'] - df_ship['order_date']).dt.days
df_ship = df_ship[(df_ship['days'] >= 0) & (df_ship['days'] <= 14)].sort_values(['customer_id', 'order_date'])
df_ship['rank'] = df_ship.groupby('customer_id').cumcount() + 1
first = df_ship[df_ship['rank'] == 1].copy()
counts = df_ship.groupby('customer_id').size()
first['repurchased'] = first['customer_id'].map(lambda x: 1 if counts[x] > 1 else 0)
first['tier'] = pd.cut(first['days'], bins=[-1, 3, 6, 9, 14], labels=['1-3d', '4-6d', '7-9d', '10-14d'])
tier = first.groupby('tier', observed=False).agg(total=('customer_id', 'count'), rep=('repurchased', 'sum')).reset_index()
tier['rate'] = tier['rep'] / tier['total'] * 100
fig, ax = plt.subplots(figsize=(10, 6.5))
ax.plot(tier['tier'], tier['rate'], color=PALETTE['authority'], marker='o', lw=3)
ax.axhline(74, color=PALETTE['friction'], linestyle='--', alpha=0.5)
apply_editorial_style(fig, ax, 'The Inelastic Logistics Paradox', 'Repurchase rates remain firmly at ~74% regardless of speed')
add_callout(ax, 'Inelastic Retention: ~74%\nLoyalty is speed-insensitive', xy=(2, 74), xytext=(1.2, 74.2), color=PALETTE['friction'])
os.makedirs(OUTPUT_DIR_03, exist_ok=True)
plt.savefig(f"{OUTPUT_DIR_03}/logistics_loyalty_paradox.png", dpi=300)

# 3. Product Iteration
df_prod['suffix'] = df_prod['product_name'].str.extract(r'-(\d+)$')[0].astype(float).fillna(0).astype(int)
df_oi = order_items.copy()
df_oi['rev'] = df_oi['quantity'] * df_oi['unit_price'] - df_oi['discount_amount'].fillna(0)
item_rev = df_oi.groupby('product_id')['rev'].sum().reset_index()
stats = df_prod.merge(item_rev, on='product_id', how='left').fillna(0)
stats['gen'] = pd.cut(stats['suffix'], bins=[-1, 10, 30, 50, 70, 100], labels=['0-10', '11-30', '31-50', '51-70', '71-99'])
gen_stats = stats.groupby('gen', observed=False).agg(rev=('rev', 'sum'), count=('product_id', 'count')).reset_index()
gen_stats['rev_per'] = gen_stats['rev'] / gen_stats['count'] / 1e6
fig, ax = plt.subplots(figsize=(10, 6.5))
ax.bar(gen_stats['gen'], gen_stats['rev_per'], color=[PALETTE['authority'] if i >= 3 else '#E2E8F0' for i in range(5)])
apply_editorial_style(fig, ax, 'The Power of Iteration', 'Newer iterations (Suffix 71-99) generate 64% more revenue per SKU')
add_callout(ax, '+64% Revenue Lift', xy=(4, gen_stats['rev_per'].iloc[4]), xytext=(2.5, 10), color=PALETTE['authority'])
plt.savefig(f"{OUTPUT_DIR_01}/product_iteration.png", dpi=300)

# 4. Loyalty Collapse
cust_first = orders.groupby('customer_id')['order_date'].min().reset_index()
cust_first['year'] = cust_first['order_date'].dt.year
orders['order_year'] = orders['order_date'].dt.year
res = []
for y in range(2012, 2022):
    cohort = cust_first[cust_first['year'] == y]['customer_id']
    ret = orders[(orders['customer_id'].isin(cohort)) & (orders['order_year'] == y + 1)]['customer_id'].nunique()
    res.append({'year': y, 'rate': (ret/len(cohort))*100, 'count': len(cohort)})
df_loyalty = pd.DataFrame(res)
fig, ax = plt.subplots(figsize=(12, 6.5))
ax.bar(df_loyalty['year'], df_loyalty['count'], color='#E2E8F0', alpha=0.5, label='New Customers')
ax2 = ax.twinx()
ax2.plot(df_loyalty['year'], df_loyalty['rate'], color=PALETTE['friction'], marker='o', lw=3, label='Retention %')
apply_editorial_style(fig, ax, 'The Retention Crisis', 'Acquisition is rising while loyalty is collapsing')
add_callout(ax2, 'Critical loyalty decay', xy=(2020, 10), xytext=(2017, 30), color=PALETTE['friction'])
os.makedirs(OUTPUT_DIR_02, exist_ok=True)
plt.savefig(f"{OUTPUT_DIR_02}/loyalty_collapse.png", dpi=300)

# 5. Campaign ROI
sales['margin'] = (sales['Revenue'] - sales['COGS']) / sales['Revenue']
def get_type(n):
    if 'Spring' in n: return 'Spring'
    if 'Mid-Year' in n: return 'Mid-Year'
    if 'Fall' in n: return 'Fall'
    if 'Year-End' in n: return 'Year-End'
    return 'Other'
promo['type'] = promo['promo_name'].apply(get_type)
roi = []
for t in ['Spring', 'Mid-Year', 'Fall', 'Year-End']:
    days = set()
    for _, r in promo[promo['type'] == t].iterrows(): days.update(pd.date_range(r['start_date'], r['end_date']))
    in_p = sales[sales['Date'].isin(days)]
    out_p = sales[~sales['Date'].isin(days)]
    lift = (in_p['Revenue'].mean() - out_p['Revenue'].mean()) / out_p['Revenue'].mean() * 100
    roi.append({'type': t, 'lift': lift, 'margin': in_p['margin'].mean()*100})
df_roi = pd.DataFrame(roi)
fig, ax = plt.subplots(figsize=(10, 6.5))
ax.bar(df_roi['type'], df_roi['lift'], color=[PALETTE['authority'] if x > 0 else PALETTE['friction'] for x in df_roi['lift']])
apply_editorial_style(fig, ax, 'Campaign Effectiveness', 'Spring Sale wins while Year-End Sale destroys value')
add_callout(ax, 'Year-End ROI Disaster', xy=(3, -40), xytext=(2, -20), color=PALETTE['friction'])
os.makedirs(OUTPUT_DIR_04, exist_ok=True)
plt.savefig(f"{OUTPUT_DIR_04}/campaign_roi.png", dpi=300)
print('Assets generated successfully.')
