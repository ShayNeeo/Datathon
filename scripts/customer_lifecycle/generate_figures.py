import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set paths
INPUT_DIR = '/home/shayneeo/Downloads/Datathon/input'
OUTPUT_DIR = '/home/shayneeo/Downloads/Datathon/output/figures_living/02_customer_lifecycle_acquisition'

# Set plot style
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'

def generate_figures():
    print("Loading data...")
    customers = pd.read_csv(os.path.join(INPUT_DIR, 'customers.csv'), parse_dates=['signup_date'])
    orders = pd.read_csv(os.path.join(INPUT_DIR, 'orders.csv'), parse_dates=['order_date'])
    payments = pd.read_csv(os.path.join(INPUT_DIR, 'payments.csv'))

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Pre-processing
    customers['signup_month'] = customers['signup_date'].dt.to_period('M').astype(str)
    
    # LTV calculation
    customer_payments = orders.merge(payments, on='order_id')
    customer_ltv = customer_payments.groupby('customer_id')['payment_value'].sum().reset_index()
    customer_ltv.columns = ['customer_id', 'ltv']
    
    # Customer info with LTV
    customer_info_ltv = customers.merge(customer_ltv, on='customer_id', how='left').fillna(0)

    # 1. Acquisition Trend (Monthly Signups)
    print("Generating acquisition_trend.png...")
    plt.figure(figsize=(12, 6))
    monthly_signups = customers.groupby('signup_month').size()
    monthly_signups.plot(kind='line', marker='o', color='#2c3e50', linewidth=2)
    plt.title('Customer Acquisition Trend (Monthly Signups)', fontsize=16, fontweight='bold')
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('New Customers', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'acquisition_trend.png'))
    plt.close()

    # 2. LTV by Channel
    print("Generating ltv_by_channel.png...")
    plt.figure(figsize=(12, 6))
    ltv_by_channel = customer_info_ltv.groupby('acquisition_channel')['ltv'].mean().sort_values(ascending=False).reset_index()
    sns.barplot(data=ltv_by_channel, x='ltv', y='acquisition_channel', palette='viridis')
    plt.title('Average Customer Lifetime Value (LTV) by Acquisition Channel', fontsize=16, fontweight='bold')
    plt.xlabel('Avg LTV (VND)', fontsize=12)
    plt.ylabel('Acquisition Channel', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'ltv_by_channel.png'))
    plt.close()

    # 3. Repeat Purchase Rate by Channel
    print("Generating repeat_rate_by_channel.png...")
    plt.figure(figsize=(12, 6))
    order_counts = orders.groupby('customer_id').size().reset_index(name='order_count')
    customer_repeat = customers.merge(order_counts, on='customer_id', how='left').fillna(0)
    customer_repeat['is_repeat'] = customer_repeat['order_count'] > 1
    repeat_rate_by_channel = customer_repeat.groupby('acquisition_channel')['is_repeat'].mean().sort_values(ascending=False).reset_index()
    repeat_rate_by_channel['is_repeat'] *= 100 # Convert to percentage
    
    sns.barplot(data=repeat_rate_by_channel, x='is_repeat', y='acquisition_channel', palette='magma')
    plt.title('Repeat Purchase Rate by Acquisition Channel', fontsize=16, fontweight='bold')
    plt.xlabel('Repeat Rate (%)', fontsize=12)
    plt.ylabel('Acquisition Channel', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'repeat_rate_by_channel.png'))
    plt.close()

    # 4. LTV Demographics Heatmap
    print("Generating ltv_demographics_heatmap.png...")
    plt.figure(figsize=(12, 8))
    ltv_demographics = customer_info_ltv.groupby(['age_group', 'gender'])['ltv'].mean().unstack()
    # Reorder age groups if necessary (assuming they are somewhat alphabetical or can be ordered)
    age_order = ['18-24', '25-34', '35-44', '45-54', '55+'] # Example order
    existing_age_groups = [age for age in age_order if age in ltv_demographics.index]
    ltv_demographics = ltv_demographics.reindex(existing_age_groups)
    
    sns.heatmap(ltv_demographics, annot=True, fmt=".0f", cmap='YlGnBu', cbar_kws={'label': 'Avg LTV (VND)'})
    plt.title('Average LTV by Age Group and Gender', fontsize=16, fontweight='bold')
    plt.xlabel('Gender', fontsize=12)
    plt.ylabel('Age Group', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'ltv_demographics_heatmap.png'))
    plt.close()

    # 5. Order Frequency Distribution
    print("Generating order_frequency_dist.png...")
    plt.figure(figsize=(10, 6))
    sns.histplot(order_counts['order_count'], bins=range(1, order_counts['order_count'].max() + 2), kde=False, color='#3498db')
    plt.title('Distribution of Order Frequency per Customer', fontsize=16, fontweight='bold')
    plt.xlabel('Number of Orders', fontsize=12)
    plt.ylabel('Customer Count', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'order_frequency_dist.png'))
    plt.close()

    print("All figures generated successfully.")

if __name__ == "__main__":
    generate_figures()
