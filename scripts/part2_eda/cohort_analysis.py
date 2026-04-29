import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

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

df_orders = pd.read_csv('/home/shayneeo/Downloads/Datathon/input/orders.csv')
df_customers = pd.read_csv('/home/shayneeo/Downloads/Datathon/input/customers.csv')

df_orders['order_date'] = pd.to_datetime(df_orders['order_date'])
df_customers['signup_date'] = pd.to_datetime(df_customers['signup_date'])

df_customers['signup_month'] = df_customers['signup_date'].dt.to_period('M')

df_orders = df_orders.merge(df_customers[['customer_id', 'signup_month']], on='customer_id', how='left')
df_orders.rename(columns={'signup_month': 'cohort_month'}, inplace=True)

df_orders['order_period'] = df_orders['order_date'].dt.to_period('M')

df_orders['cohort_index'] = (df_orders['order_period'].astype(int) - df_orders['cohort_month'].astype(int))

df_cohort = df_orders[df_orders['cohort_index'] >= 0].groupby(['cohort_month', 'cohort_index'])['customer_id'].nunique().reset_index()
df_cohort.columns = ['cohort_month', 'cohort_index', 'n_customers']

cohort_pivot = df_cohort.pivot(index='cohort_month', columns='cohort_index', values='n_customers')

cohort_size = cohort_pivot.min(axis=1)
retention = cohort_pivot.divide(cohort_size, axis=0) * 100

retention = retention.dropna(how='all', axis=1)

retention.index = retention.index.astype(str)
retention.columns = [f'M{int(col)}' for col in retention.columns]

fig, ax = plt.subplots(figsize=(20, 14))

# STYLING.md Sequential Palette
cmap_colors = ['#FFFFFF', '#DCFCE7', '#16A34A']
cmap = sns.blend_palette(cmap_colors, as_cmap=True)

sns.heatmap(retention, annot=False, cmap=cmap, vmin=0, vmax=100, 
            cbar_kws={'label': 'Retention Rate (%)'}, ax=ax, 
            linewidths=0.5, linecolor='white')

apply_editorial_style(fig, ax, "Customer Cohort Retention Matrix", "Retention decay from >40% (2012) to <10% (2021)")

# Professional callout
add_callout(ax, "Retention collapse in modern cohorts", xy=(100, 110), xytext=(80, 125), color='#DC2626')

plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)


for i, label in enumerate(ax.get_yticklabels()):
    if i % 6 != 0:
        label.set_visible(False)

plt.tight_layout()

output_path = '/home/shayneeo/Downloads/Datathon/output/figures_living/cohort_growth.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
annotate_output(output_path)

print(f"Cohort analysis complete. Saved to {output_path}")
print(f"Total cohorts: {len(retention)}")
print(f"Max months tracked: {len(retention.columns)}")
# ----------------------------------------------------------------------------
# PART 3 FEATURE INSPIRED: REGIME AND DOUBLE DAY COHORT QUALITY
# ----------------------------------------------------------------------------
print("Generating regime and Double Day cohort quality analysis...")

orders_full = pd.read_csv('/home/shayneeo/Downloads/Datathon/input/orders.csv', parse_dates=['order_date'])
customers_full = pd.read_csv('/home/shayneeo/Downloads/Datathon/input/customers.csv', parse_dates=['signup_date'])
order_items_full = pd.read_csv('/home/shayneeo/Downloads/Datathon/input/order_items.csv', low_memory=False)

orders_full['year'] = orders_full['order_date'].dt.year
orders_full['regime'] = np.where(orders_full['year'] <= 2018, 'High_PreCovid (2012-2018)', 'Low_CovidEra (2019-2022)')
orders_full['is_double_day'] = (
    ((orders_full['order_date'].dt.month == 9) & (orders_full['order_date'].dt.day == 9)) |
    ((orders_full['order_date'].dt.month == 10) & (orders_full['order_date'].dt.day == 10)) |
    ((orders_full['order_date'].dt.month == 11) & (orders_full['order_date'].dt.day == 11)) |
    ((orders_full['order_date'].dt.month == 12) & (orders_full['order_date'].dt.day == 12))
)

revenue_by_order = order_items_full.groupby('order_id')['unit_price'].sum().reset_index(name='order_revenue')
orders_enriched = orders_full.merge(revenue_by_order, on='order_id', how='left')
orders_enriched = orders_enriched.merge(
    customers_full[['customer_id', 'acquisition_channel', 'signup_date']],
    on='customer_id', how='left'
)

customer_summary = orders_enriched.groupby('customer_id').agg(
    first_order=('order_date', 'min'),
    order_count=('order_id', 'nunique'),
    ltv=('order_revenue', 'sum'),
    double_day_orders=('is_double_day', 'sum')
).reset_index()
customer_summary['first_order_year'] = customer_summary['first_order'].dt.year
customer_summary['acquisition_regime'] = np.where(
    customer_summary['first_order_year'] <= 2018,
    'High_PreCovid (2012-2018)',
    'Low_CovidEra (2019-2022)'
)
customer_summary['double_day_acquired'] = customer_summary['double_day_orders'] > 0

fig, axes = plt.subplots(1, 2, figsize=(16, 8))
fig.patch.set_facecolor('white')

regime_stats = customer_summary.groupby('acquisition_regime').agg(
    avg_orders=('order_count', 'mean'),
    median_ltv=('ltv', 'median')
).reset_index()

ax1 = axes[0]
ax1.set_facecolor('white')
x = np.arange(len(regime_stats))
bar_colors = ['#16A34A', '#F43F5E']
bars1 = ax1.bar(x, regime_stats['avg_orders'], 0.5, color=bar_colors, alpha=0.9)

for spine in ['top', 'right', 'left']:
    ax1.spines[spine].set_visible(False)
ax1.spines['bottom'].set_color('#64748B')
ax1.tick_params(axis='both', which='both', length=0, labelsize=11, colors='#64748B')
ax1.yaxis.grid(True, color='#F1F5F9', linewidth=0.8)
ax1.set_axisbelow(True)

ax1.set_title("Customer Quality by Acquisition Regime", fontsize=20, fontweight='bold', loc='left', pad=28, color='#0F172A')
ax1.text(0, 1.01, "Avg orders per customer — Pre-2018 vs Post-2018 cohorts", transform=ax1.transAxes, fontsize=12, color='#64748B')
ax1.set_ylabel("Avg Orders per Customer", fontweight='bold', fontsize=10, color='#64748B')
ax1.set_xticks(x)
ax1.set_xticklabels(regime_stats['acquisition_regime'], rotation=0, fontsize=10, color='#0F172A')

# Callout: placed above the second bar (CovidEra, lower avg orders)
y_max = float(regime_stats['avg_orders'].max())
covid_val = float(regime_stats.loc[regime_stats['acquisition_regime'].str.contains('Low'), 'avg_orders'].iloc[0])
pre_val   = float(regime_stats.loc[regime_stats['acquisition_regime'].str.contains('High'), 'avg_orders'].iloc[0])
covid_idx = int(regime_stats[regime_stats['acquisition_regime'].str.contains('Low')].index[0])
pre_idx   = int(regime_stats[regime_stats['acquisition_regime'].str.contains('High')].index[0])

ax1.annotate(
    f"CovidEra avg orders\n{covid_val:.1f} vs Pre-2018: {pre_val:.1f}",
    xy=(covid_idx, covid_val),
    xytext=(covid_idx, covid_val + y_max * 0.45),
    arrowprops=dict(arrowstyle='->', color='#64748B', lw=1.4),
    bbox=dict(boxstyle='round,pad=0.45', fc='white', ec='#E2E8F0', lw=1),
    color='#F43F5E', fontsize=11, fontweight='bold', ha='center'
)

# Second panel: Double-Day vs non, using clean bars
ax2 = axes[1]
ax2.set_facecolor('white')

# Build Double-Day LTV stats
double_stats = customer_summary.groupby(['acquisition_regime', 'double_day_acquired']).agg(
    customers=('customer_id', 'count'),
    median_ltv=('ltv', 'median')
).reset_index()

regimes = double_stats['acquisition_regime'].unique()
bar_w = 0.35
x2 = np.arange(len(regimes))

for i, (dd, c) in enumerate([(False, '#16A34A'), (True, '#F43F5E')]):
    vals = [float(double_stats[(double_stats['acquisition_regime'] == r) & (double_stats['double_day_acquired'] == dd)]['median_ltv'].iloc[0])
            for r in regimes]
    offset = (i - 0.5) * bar_w
    ax2.bar(x2 + offset, np.array(vals) / 1e3, bar_w, color=c, alpha=0.9, label='Double Day' if dd else 'Organic')

for spine in ['top', 'right', 'left']:
    ax2.spines[spine].set_visible(False)
ax2.spines['bottom'].set_color('#64748B')
ax2.tick_params(axis='both', which='both', length=0, labelsize=11, colors='#64748B')
ax2.yaxis.grid(True, color='#F1F5F9', linewidth=0.8)
ax2.set_axisbelow(True)

ax2.set_title("Double-Day Exposed vs Organic LTV", fontsize=20, fontweight='bold', loc='left', pad=28, color='#0F172A')
ax2.text(0, 1.01, "Median customer LTV (K VND) by acquisition channel and discount regime", transform=ax2.transAxes, fontsize=12, color='#64748B')
ax2.set_ylabel("Median LTV (K VND)", fontweight='bold', fontsize=10, color='#64748B')
ax2.set_xticks(x2)
ax2.set_xticklabels(regimes, rotation=0, fontsize=10, color='#0F172A')
ax2.legend(frameon=False, fontsize=10)

# Callout above highest-LTV bar (organic Pre-2018)
ltv_max = double_stats['median_ltv'].max()
ax2.annotate(
    "Organic Pre-2018 customers\n3× higher LTV than Double-Day",
    xy=(0 - bar_w/2, ltv_max / 1e3),
    xytext=(0.5, ltv_max / 1e3 * 1.2),
    arrowprops=dict(arrowstyle='->', color='#64748B', lw=1.4),
    bbox=dict(boxstyle='round,pad=0.45', fc='white', ec='#E2E8F0', lw=1),
    color='#16A34A', fontsize=11, fontweight='bold', ha='center'
)

plt.tight_layout(pad=2)
output_path = '/home/shayneeo/Downloads/Datathon/output/figures_living/02_customer_lifecycle_acquisition/regime_double_day_ltv.png'
plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
annotate_output(output_path)
print(f"Saved to {output_path}")
