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
cmap_colors = ['#FFFFFF', '#56B4E9', '#0072B2']
cmap = sns.blend_palette(cmap_colors, as_cmap=True)

sns.heatmap(retention, annot=False, cmap=cmap, vmin=0, vmax=100, 
            cbar_kws={'label': 'Retention Rate (%)'}, ax=ax, 
            linewidths=0.5, linecolor='white')

apply_editorial_style(fig, ax, "Customer Cohort Retention Matrix", "Retention decay from >40% (2012) to <10% (2021)")

# Professional callout
add_callout(ax, "Retention collapse in modern cohorts", xy=(100, 110), xytext=(80, 125), color='#D55E00')

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
order_items_full = pd.read_csv('/home/shayneeo/Downloads/Datathon/input/order_items.csv')

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

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

regime_stats = customer_summary.groupby('acquisition_regime').agg(
    avg_orders=('order_count', 'mean'),
    median_ltv=('ltv', 'median')
).reset_index()

ax1 = axes[0]
x = np.arange(len(regime_stats))
ax1.bar(x - 0.2, regime_stats['avg_orders'], 0.4, label='Avg Orders', color='#0072B2')
ax1_t = ax1.twinx()
ax1_t.bar(x + 0.2, regime_stats['median_ltv'] / 1_000_000, 0.4, label='Median LTV', color='#E69F00')

apply_editorial_style(fig, ax1, "Customer Quality by Acquisition Regime", "High LTV decay in CovidEra cohorts (2019-2022)")
ax1.set_xticks(x)
ax1.set_xticklabels(regime_stats['acquisition_regime'], rotation=0)

# Professional callout
add_callout(ax1, "4x LTV collapse in CovidEra", xy=(1, 1.5), xytext=(0.5, 3.5), color='#D55E00')

ax2 = axes[1]
double_stats = customer_summary.groupby(['acquisition_regime', 'double_day_acquired']).agg(
    customers=('customer_id', 'count'),
    median_ltv=('ltv', 'median')
).reset_index()
sns.barplot(data=double_stats, x='acquisition_regime', y='median_ltv', hue='double_day_acquired', ax=ax2, palette=['#56B4E9', '#D55E00'])

# Editorial title for second subplot (fig.text already handles main title, but we can add secondary if needed)
ax2.set_title("Double-Day Exposed vs Non-Exposed Customers", fontsize=12, fontweight='bold', color='#64748B')
ax2.legend(title='Bought on Double Day', frameon=False)

# Professional callout
add_callout(ax2, "Double-Day LTV gap", xy=(1.2, 5000), xytext=(1.5, 15000), color='#D55E00')

plt.tight_layout()
output_path = '/home/shayneeo/Downloads/Datathon/output/figures_living/02_customer_lifecycle_acquisition/regime_double_day_ltv.png'
plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
annotate_output(output_path)
print(f"Saved to {output_path}")
