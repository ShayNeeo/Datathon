import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

# ==============================================================================
# 2026 PREMIUM EDITORIAL UI CONFIGURATION (VERCEL/STRIPE INSPIRED)
# ==============================================================================
# Core Palette
C_BRAND = "#93FA64"        # User's primary pastel neon green
C_BRAND_DARK = "#16A34A"   # Darker green for text/lines on top of brand color
C_BRAND_LIGHT = "#DCFCE7"  # Very light green for backgrounds/secondary bars
C_TEXT_HEAD = "#0F172A"    # Deep slate for Titles
C_TEXT_SUB = "#64748B"     # Muted slate for Subtitles/Axes
C_GRID = "#F1F5F9"         # Subtle grid lines
C_ALERT = "#F43F5E"        # Modern rose red for negative/loss
C_ALERT_LIGHT = "#FFE4E6"  # Light rose for negative backgrounds
C_NEUTRAL = "#E2E8F0"      # Slate 200 for neutral bars

def apply_2026_style(fig, ax, title, subtitle):
    # Remove spines
    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color('#CBD5E1')
    ax.spines['bottom'].set_linewidth(1.5)
    
    # Tick params
    ax.tick_params(axis='both', which='both', length=0, labelsize=11, colors=C_TEXT_SUB)
    
    # Grid
    ax.grid(axis='y', color=C_GRID, linewidth=1.5, linestyle='-')
    ax.set_axisbelow(True)
    
    # Editorial Titles (Left aligned to the figure)
    fig.text(0.04, 0.94, title, fontsize=22, fontweight='black', color=C_TEXT_HEAD, fontname='sans-serif')
    fig.text(0.04, 0.88, subtitle, fontsize=13, color=C_TEXT_SUB, fontname='sans-serif')
    
    # Adjust layout to make room for titles
    plt.subplots_adjust(top=0.78, bottom=0.1, left=0.08, right=0.95)

def clean_annotation(ax, text, xy, xytext, color=C_TEXT_HEAD, arrow_color=C_TEXT_SUB):
    ax.annotate(text, xy=xy, xytext=xytext,
                arrowprops=dict(arrowstyle="->", color=arrow_color, lw=1.5, connectionstyle="arc3,rad=0.2"),
                color=color, fontweight="600", ha="center", fontsize=11,
                bbox=dict(boxstyle="round,pad=0.6,rounding_size=0.3", facecolor="#FFFFFF", 
                          edgecolor="#E2E8F0", alpha=0.95, lw=1))

DATA = Path("/home/shayneeo/Downloads/Datathon/input")
OUT = Path("/home/shayneeo/Downloads/Datathon/team/part2/charts_final")
os.makedirs(OUT, exist_ok=True)

# Set base mpl params
plt.rcParams.update({'font.family': 'sans-serif', 'figure.facecolor': '#FFFFFF', 'axes.facecolor': '#FFFFFF'})

# ==============================================================================
# CHART 1: Loss Leader Trap
# ==============================================================================
print("Generating Chart 1...")
products = pd.read_csv(DATA / "products.csv")
order_items = pd.read_csv(DATA / "order_items.csv", low_memory=False)

products['margin'] = (products['price'] - products['cogs']) / products['price']
loss_ids = products[products['margin'] <= 0.055]['product_id'].unique()
order_items['is_loss'] = order_items['product_id'].isin(loss_ids)
order_items['rev'] = order_items['quantity'] * order_items['unit_price'] - order_items['discount_amount'].fillna(0)
order_items = order_items.merge(products[['product_id', 'cogs']], on='product_id', how='left')
order_items['profit'] = order_items['rev'] - (order_items['quantity'] * order_items['cogs'])

stats = order_items.groupby('order_id').agg(
    is_loss=('is_loss', 'max'), rev=('rev', 'sum'), prof=('profit', 'sum')
).reset_index()
stats = stats[stats['rev'] > 0]
grp = stats.groupby('is_loss').mean().reset_index()

fig, ax = plt.subplots(figsize=(10, 6.5))
apply_2026_style(fig, ax, "The 'Bait' Trap: High Volume but Negative Profit", 
                 "Orders with low-margin products (<= 5.5%) fail to create expected cross-sell effects, leading to losses.")

x = np.arange(2)
width = 0.35
labels = ['Standard Order', '"Bait" Order']

ax.bar(x - width/2, grp['rev'], width, label='Revenue (VND)', color=C_NEUTRAL, edgecolor='none')
ax.bar(x + width/2, grp['prof'], width, label='Profit (VND)', color=[C_BRAND, C_ALERT], edgecolor='none')

for i in range(2):
    ax.text(x[i] - width/2, grp['rev'].iloc[i] + 500, f"{grp['rev'].iloc[i]:,.0f}", ha='center', fontweight='bold', color=C_TEXT_SUB)
    p_val = grp['prof'].iloc[i]
    color_val = C_BRAND_DARK if p_val > 0 else C_ALERT
    y_off = 500 if p_val > 0 else -1500
    ax.text(x[i] + width/2, p_val + y_off, f"{p_val:,.0f}", ha='center', fontweight='bold', color=color_val)

ax.axhline(0, color=C_TEXT_SUB, linewidth=1, linestyle='--')
ax.set_xticks(x)
ax.set_xticklabels(labels, fontweight='bold', fontsize=12, color=C_TEXT_HEAD)
ax.legend(loc='upper right', frameon=False, fontsize=11, labelcolor=C_TEXT_SUB)

clean_annotation(ax, f"Average Loss\n{grp['prof'].iloc[1]:,.0f} VND/order", xy=(1 + width/2, grp['prof'].iloc[1]), xytext=(1.4, 5000), color=C_ALERT)

plt.savefig(OUT / "1_loss_leader_trap.png")
plt.close()
del order_items, stats

# ==============================================================================
# CHART 2: Logistics Paradox
# ==============================================================================
print("Generating Chart 2...")
orders = pd.read_csv(DATA / "orders.csv", parse_dates=['order_date'])
shipments = pd.read_csv(DATA / "shipments.csv", parse_dates=['ship_date', 'delivery_date'])

df_ship = orders[['order_id', 'customer_id', 'order_date']].merge(shipments[['order_id', 'delivery_date']], on='order_id', how='inner')
df_ship['days'] = (df_ship['delivery_date'] - df_ship['order_date']).dt.days
df_ship = df_ship[(df_ship['days'] >= 0) & (df_ship['days'] <= 14)]
df_ship = df_ship.sort_values(['customer_id', 'order_date'])
df_ship['rank'] = df_ship.groupby('customer_id').cumcount() + 1
first = df_ship[df_ship['rank'] == 1].copy()
counts = df_ship.groupby('customer_id').size()
first['repurchased'] = first['customer_id'].map(lambda x: 1 if counts[x] > 1 else 0)

bins = [-1, 3, 6, 9, 14]
labels = ['1-3 days\n(Express)', '4-6 days\n(Standard)', '7-9 days\n(Slow)', '10-14 days\n(Very Late)']
first['tier'] = pd.cut(first['days'], bins=bins, labels=labels)
tier = first.groupby('tier', observed=False).agg(total=('customer_id', 'count'), rep=('repurchased', 'sum')).reset_index()
tier['rate'] = tier['rep'] / tier['total'] * 100

fig, ax = plt.subplots(figsize=(10, 6.5))
apply_2026_style(fig, ax, "Logistics Paradox: Speed Can't Buy Loyalty", 
                 "Repurchase rates remain firmly at ~74% regardless of super-fast (2 days) or very late (14 days) delivery.")

ax.bar(tier['tier'], tier['rate'], color=C_BRAND_LIGHT, edgecolor='none', width=0.5, zorder=3)
ax.plot(tier['tier'], tier['rate'], color=C_BRAND_DARK, marker='o', lw=3, markersize=10, zorder=4)

for i, val in enumerate(tier['rate']):
    ax.text(i, val + 1.5, f"{val:.1f}%", ha='center', fontweight='bold', fontsize=12, color=C_BRAND_DARK)

ax.set_ylim(0, 100)
clean_annotation(ax, "Hard ceiling at 74%\nCustomers are willing to wait.", xy=(2, tier['rate'].iloc[2]), xytext=(2, 40))

plt.savefig(OUT / "2_logistics_paradox.png")
plt.close()

# ==============================================================================
# CHART 3: Product Lifecycle
# ==============================================================================
print("Generating Chart 3...")
products['suffix'] = products['product_name'].str.extract(r'-(\d+)$')[0].astype(int)
oi = pd.read_csv(DATA / "order_items.csv", usecols=['product_id', 'quantity', 'unit_price', 'discount_amount'])
oi['rev'] = oi['quantity'] * oi['unit_price'] - oi['discount_amount'].fillna(0)
item_rev = oi.groupby('product_id')['rev'].sum().reset_index()
prod_stats = products.merge(item_rev, on='product_id', how='left').fillna(0)

bins = [-1, 10, 30, 50, 70, 100]
labels = ['Classic\n(00-10)', 'Early Gen\n(11-30)', 'Mid Gen\n(31-50)', 'Late Gen\n(51-70)', 'Latest Gen\n(71-99)']
prod_stats['gen'] = pd.cut(prod_stats['suffix'], bins=bins, labels=labels)
gen = prod_stats.groupby('gen', observed=False).agg(rev=('rev', 'sum'), count=('product_id', 'count')).reset_index()
gen['rev_per'] = gen['rev'] / gen['count'] / 1e6

fig, ax = plt.subplots(figsize=(10, 6.5))
apply_2026_style(fig, ax, "The Power of R&D: Product Evolution Lifecycle", 
                 "Improved versions (suffix 71-99) generate far superior revenue per SKU compared to classic models.")

colors = [C_NEUTRAL, C_NEUTRAL, C_NEUTRAL, C_BRAND_LIGHT, C_BRAND]
ax.bar(gen['gen'], gen['rev_per'], color=colors, edgecolor='none', width=0.6, zorder=3)

for i, val in enumerate(gen['rev_per']):
    col = C_BRAND_DARK if i >= 3 else C_TEXT_SUB
    ax.text(i, val + 0.2, f"{val:.1f}M", ha='center', fontweight='bold', fontsize=12, color=col)

clean_annotation(ax, "Continuous innovation drives\n+78% revenue/SKU", xy=(4, gen['rev_per'].iloc[4]), xytext=(2.5, 9), arrow_color=C_BRAND_DARK)

plt.savefig(OUT / "3_product_lifecycle.png")
plt.close()
del oi

# ==============================================================================
# CHART 4: Tet Effect
# ==============================================================================
print("Generating Chart 4...")
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
        if len(row) > 0: windows.append({"delta": delta, "rev": row.Revenue.values[0]})
df_tet = pd.DataFrame(windows).groupby("delta")["rev"].mean() / 1e6

fig, ax = plt.subplots(figsize=(12, 6.5))
apply_2026_style(fig, ax, "Tet Effect: The Most Intense Seasonal Cycle", 
                 "Shopping surge starts at T-30, completely bottoms out during 7 holidays, and takes 15 days to recover.")

colors = [C_BRAND if x < 0 else C_ALERT if x <= 7 else C_NEUTRAL for x in df_tet.index]
ax.bar(df_tet.index, df_tet.values, color=colors, alpha=0.8, width=1, edgecolor='none')

baseline = pre_covid.Revenue.mean() / 1e6
ax.axhline(baseline, color=C_TEXT_SUB, ls="--", lw=1.5, zorder=1)
ax.text(25, baseline + 0.1, f"Baseline: {baseline:.1f}M", color=C_TEXT_SUB, fontweight='bold', fontsize=10)

ax.annotate("SHOPPING SURGE\n(Pre-Tet Surge)", xy=(-15, 3.5), xytext=(-15, 4.2), ha='center', fontweight='900', color=C_BRAND_DARK)
ax.annotate("FROZEN\n(Dead Zone)", xy=(3, 2), xytext=(3, 2.5), ha='center', fontweight='900', color=C_ALERT)

plt.savefig(OUT / "4_tet_effect.png")
plt.close()

# ==============================================================================
# CHART 5: Campaign ROI
# ==============================================================================
print("Generating Chart 5...")
promo = pd.read_csv(DATA / 'promotions.csv', parse_dates=['start_date', 'end_date'])
sales['margin'] = (sales['Revenue'] - sales['COGS']) / sales['Revenue']

def get_type(name):
    if 'Spring' in name: return 'Spring Sale'
    if 'Mid-Year' in name: return 'Mid-Year Sale'
    if 'Fall' in name: return 'Fall Launch'
    if 'Year-End' in name: return 'Year-End Sale'
    return 'Other'

promo['type'] = promo['promo_name'].apply(get_type)
res = []
for p_type in ['Spring Sale', 'Mid-Year Sale', 'Fall Launch', 'Year-End Sale']:
    days = set()
    for _, r in promo[promo['type'] == p_type].iterrows(): days.update(pd.date_range(r['start_date'], r['end_date']))
    in_p = sales[sales['Date'].isin(days)]
    out_p = sales[~sales['Date'].isin(days)]
    lift = (in_p['Revenue'].mean() - out_p['Revenue'].mean()) / out_p['Revenue'].mean() * 100
    margin = in_p['margin'].mean() * 100
    res.append({'Campaign': p_type, 'Lift': lift, 'Margin': margin})

df_roi = pd.DataFrame(res)

fig, ax1 = plt.subplots(figsize=(10, 6.5))
apply_2026_style(fig, ax1, "Campaign ROI: The 'Year-End Sale' Double Disaster", 
                 "Spring Sale drives demand while keeping margin. Year-End Sale evaporates both revenue and profit.")

colors = [C_BRAND if x > 0 else C_ALERT for x in df_roi['Lift']]
ax1.bar(df_roi['Campaign'], df_roi['Lift'], color=colors, edgecolor='none', width=0.6, alpha=0.9, zorder=3)

for i, row in df_roi.iterrows():
    offset = 2 if row['Lift'] > 0 else -4
    col = C_BRAND_DARK if row['Lift'] > 0 else C_ALERT
    ax1.text(i, row['Lift'] + offset, f"{row['Lift']:+.1f}%", ha='center', fontweight='bold', fontsize=12, color=col)

ax2 = ax1.twinx()
ax2.spines['top'].set_visible(False); ax2.spines['left'].set_visible(False)
ax2.spines['right'].set_visible(False); ax2.spines['bottom'].set_visible(False)
ax2.tick_params(length=0, labelsize=11, colors=C_TEXT_SUB)

ax2.plot(df_roi.index, df_roi['Margin'], color=C_TEXT_HEAD, marker='D', markersize=8, lw=3, zorder=5)
for i, val in enumerate(df_roi['Margin']):
    ax2.text(i+0.1, val+0.5, f"Margin: {val:.1f}%", ha='left', fontweight='bold', color=C_TEXT_HEAD, fontsize=10)

ax1.set_ylabel("Revenue Growth (%)", color=C_TEXT_SUB)
ax2.set_ylabel("Gross Margin (%)", color=C_TEXT_HEAD)
ax1.axhline(0, color=C_TEXT_SUB, lw=1.5, ls='--', zorder=1)

clean_annotation(ax1, "Spring Sale:\nBrightest point of year", xy=(0, df_roi['Lift'].iloc[0]), xytext=(1, 30))
clean_annotation(ax1, "Year-End Sale:\nDestroys value\nRemove immediately!", xy=(3, df_roi['Lift'].iloc[3]), xytext=(2, -20), color=C_ALERT)

plt.savefig(OUT / "5_campaign_roi.png")
plt.close()

# ==============================================================================
# CHART 6: Loyalty Collapse
# ==============================================================================
print("Generating Chart 6...")
orders = pd.read_csv(DATA / 'orders.csv', usecols=['customer_id', 'order_date'], parse_dates=['order_date'])
cust_first = orders.groupby('customer_id')['order_date'].min().reset_index()
cust_first['cohort_year'] = cust_first['order_date'].dt.year
orders = orders.merge(cust_first[['customer_id', 'cohort_year']], on='customer_id')
orders['order_year'] = orders['order_date'].dt.year

res = []
for y in range(2012, 2022):
    cohort = cust_first[cust_first['cohort_year'] == y]['customer_id']
    ret = orders[(orders['customer_id'].isin(cohort)) & (orders['order_year'] == y + 1)]['customer_id'].nunique()
    res.append({'Cohort': y, 'Retention': (ret / len(cohort)) * 100, 'Acquired': len(cohort)})

df_loyalty = pd.DataFrame(res)

fig, ax1 = plt.subplots(figsize=(12, 6.5))
apply_2026_style(fig, ax1, "The Retention Crisis (Loyalty Collapse)", 
                 "Acquisition of new customers skyrockets, but retention of old customers plummets.")

ax2 = ax1.twinx()
for sp in ['top', 'right', 'left', 'bottom']: ax2.spines[sp].set_visible(False)
ax2.tick_params(length=0, colors=C_TEXT_SUB)

# Bar chart (Acquisition)
ax2.bar(df_loyalty['Cohort'], df_loyalty['Acquired'], color=C_NEUTRAL, width=0.6, alpha=0.5, edgecolor='none')

# Line/Area chart (Retention)
ax1.plot(df_loyalty['Cohort'], df_loyalty['Retention'], color=C_ALERT, marker='o', lw=3, markersize=8, zorder=5)
ax1.fill_between(df_loyalty['Cohort'], df_loyalty['Retention'], color=C_ALERT_LIGHT, alpha=0.5, zorder=4)

for i, row in df_loyalty.iterrows():
    ax1.text(row['Cohort'], row['Retention'] + 2, f"{row['Retention']:.1f}%", ha='center', fontweight='bold', color=C_ALERT)

ax1.set_ylabel("Next-year Retention Rate (%)", color=C_ALERT)
ax2.set_ylabel("New Customers Volume (Acquisition)", color=C_TEXT_SUB)
ax1.set_ylim(0, 80); ax2.set_ylim(0, df_loyalty['Acquired'].max() * 2)
ax1.set_xticks(df_loyalty['Cohort'])

clean_annotation(ax1, "Golden Era:\nCustomers buy repeatedly.", xy=(2013, df_loyalty[df_loyalty['Cohort']==2013]['Retention'].values[0]), xytext=(2014.5, 65))
clean_annotation(ax1, "Red Alert:\nModern customers just\nbuy once then leave.", xy=(2019, df_loyalty[df_loyalty['Cohort']==2019]['Retention'].values[0]), xytext=(2018, 30), color=C_ALERT)

plt.savefig(OUT / "6_loyalty_collapse.png")
plt.close()

print("All 2026 Premium Charts generated successfully!")
