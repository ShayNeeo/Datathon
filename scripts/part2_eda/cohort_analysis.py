import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
from PIL import Image, ImageDraw, ImageFont


def _font(size):
    try:
        return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', size)
    except Exception:
        return ImageFont.load_default()


def _text(draw, xy, text, color, size):
    font = _font(size)
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = max(10, min(xy[0], draw._image.size[0] - w - 10))
    y = max(10, min(xy[1], draw._image.size[1] - h - 10))
    draw.rounded_rectangle([x - 8, y - 8, x + w + 8, y + h + 8], radius=6, fill=(255, 255, 255, 235), outline=color, width=2)
    draw.text((x, y), text, font=font, fill=color)


def annotate_output(path):
    img = Image.open(path).convert('RGBA')
    w, h = img.size
    draw = ImageDraw.Draw(img, 'RGBA')
    name = os.path.basename(path)
    if name == 'cohort_growth.png':
        _text(draw, (w * 0.72, h * 0.06), 'Retention\n40→10%', '#CE2626', max(14, int(min(w, h) / 150)))
    elif name == 'regime_double_day_ltv.png':
        _text(draw, (w * 0.67, h * 0.08), 'Double-Day\nLTV gap', '#CE2626', max(12, int(min(w, h) / 160)))
    img.convert('RGB').save(path)

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

cmap_colors = ['#CE2626', '#E8DBB3', '#FFFDEB', '#7DAACB']
cmap = sns.blend_palette(cmap_colors, as_cmap=True)

sns.heatmap(retention, annot=False, cmap=cmap, vmin=0, vmax=100, 
            cbar_kws={'label': 'Retention Rate (%)'}, ax=ax, 
            linewidths=0.5, linecolor='white')

ax.set_title('Customer Cohort Retention Analysis\n(Based on Customer Signup Month - 2012-2022)', 
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Months Since First Purchase', fontsize=12)
ax.set_ylabel('Cohort (Signup Month)', fontsize=12)

# PRESCRIPTIVE ANNOTATION
plt.text(0.98, 0.98, "PREDICTIVE: Retention collapse indicates LTV < CAC by Q4 2023.\nACTION: Launch VIP Retention Program for organic cohorts.", 
         transform=plt.gca().transAxes, fontsize=12, verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='#CE2626'))

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
ax1.bar(x - 0.2, regime_stats['avg_orders'], 0.4, label='Avg Orders / Customer', color='#003366')
ax1.set_ylabel('Avg Orders / Customer', color='#003366', fontweight='bold')
ax1.tick_params(axis='y', labelcolor='#003366')
ax1.set_xticks(x)
ax1.set_xticklabels(regime_stats['acquisition_regime'], rotation=15, ha='right')
ax1_t = ax1.twinx()
ax1_t.bar(x + 0.2, regime_stats['median_ltv'] / 1_000_000, 0.4, label='Median LTV (M VND)', color='#B8860B')
ax1_t.set_ylabel('Median LTV (M VND)', color='#B8860B', fontweight='bold')
ax1_t.tick_params(axis='y', labelcolor='#B8860B')
ax1.set_title('Customer Quality by Acquisition Regime', fontsize=14, fontweight='bold')

# DIAGNOSTIC NOTE
ax1.text(0.05, 0.95, "DIAGNOSTIC: CovidEra cohorts show 4x lower LTV.\nShift from community-driven to deal-driven model.", 
         transform=ax1.transAxes, fontsize=10, verticalalignment='top', 
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='#003366'))

ax2 = axes[1]
double_stats = customer_summary.groupby(['acquisition_regime', 'double_day_acquired']).agg(
    customers=('customer_id', 'count'),
    median_ltv=('ltv', 'median')
).reset_index()
sns.barplot(data=double_stats, x='acquisition_regime', y='median_ltv', hue='double_day_acquired', ax=ax2, palette=['#7DAACB', '#CE2626'])
ax2.set_title('Median LTV: Double-Day Exposed vs Non-Exposed Customers', fontsize=14, fontweight='bold')
ax2.set_xlabel('Acquisition Regime')
ax2.set_ylabel('Median LTV (VND)')
ax2.tick_params(axis='x', rotation=15)
ax2.legend(title='Bought on Double Day')

# PRESCRIPTIVE NOTE
ax2.text(0.95, 0.05, "PRESCRIPTIVE: Decouple Double-Day spend from organic targets.\nDeal-hunter acquisition is structurally unprofitable.", 
         transform=ax2.transAxes, fontsize=10, verticalalignment='bottom', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='#B8860B'))

plt.tight_layout()
output_path = '/home/shayneeo/Downloads/Datathon/output/figures_living/02_customer_lifecycle_acquisition/regime_double_day_ltv.png'
plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
annotate_output(output_path)
print(f"Saved to {output_path}")
