import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

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

plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)

for i, label in enumerate(ax.get_yticklabels()):
    if i % 6 != 0:
        label.set_visible(False)

plt.tight_layout()

output_path = '/home/shayneeo/Downloads/Datathon/output/figures_living/cohort_growth.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print(f"Cohort analysis complete. Saved to {output_path}")
print(f"Total cohorts: {len(retention)}")
print(f"Max months tracked: {len(retention.columns)}")