import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

INPUT_DIR = '/home/shayneeo/Downloads/Datathon/input'
OUTPUT_DIR = '/home/shayneeo/Downloads/Datathon/output/figures_living/04_financial_payment_dynamics'

sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'


def ensure_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_and_prepare():
    print("Loading data...")
    orders = pd.read_csv(os.path.join(INPUT_DIR, 'orders.csv'), parse_dates=['order_date'])
    order_items = pd.read_csv(os.path.join(INPUT_DIR, 'order_items.csv'), low_memory=False)
    payments = pd.read_csv(os.path.join(INPUT_DIR, 'payments.csv'))
    promotions = pd.read_csv(os.path.join(INPUT_DIR, 'promotions.csv'), parse_dates=['start_date', 'end_date'])
    customers = pd.read_csv(os.path.join(INPUT_DIR, 'customers.csv'), parse_dates=['signup_date'])

    orders_payments = orders.merge(payments, on='order_id', how='inner', suffixes=('', '_pay'))
    if 'payment_method_pay' in orders_payments.columns:
        orders_payments['payment_method'] = orders_payments['payment_method_pay']
        orders_payments = orders_payments.drop(columns=['payment_method_pay'])

    oi = order_items.merge(orders[['order_id', 'order_date', 'order_status']], on='order_id', how='left')
    oi_delivered = oi[oi['order_status'] == 'delivered'].copy()

    orders_payments['month'] = orders_payments['order_date'].dt.to_period('M')
    oi_delivered['month'] = oi_delivered['order_date'].dt.to_period('M')

    return orders_payments, oi_delivered, promotions, customers, payments


def plot_installment_aov_distribution(df):
    """Distribution of AOV by installment usage"""
    fig, ax = plt.subplots(figsize=(12, 6))
    df = df.copy()
    df['has_installment'] = df['installments'] > 1
    data = df[df['payment_value'] < df['payment_value'].quantile(0.99)]
    sns.boxplot(data=data, x='has_installment', y='payment_value', hue='has_installment',
                palette='Set2', legend=False, ax=ax)
    ax.set_title('AOV Distribution: Installment vs Non-Installment Orders', fontsize=16, fontweight='bold')
    ax.set_xlabel('Uses Installment Plan', fontsize=12)
    ax.set_ylabel('Order Value (VND)', fontsize=12)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['No', 'Yes'])
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'installment_aov_boxplot.png'))
    plt.close()
    print("Generated: installment_aov_boxplot.png")


def plot_payment_method_market_share(df):
    """Revenue share by payment method"""
    plt.figure(figsize=(10, 8))
    revenue_by_method = df.groupby('payment_method')['payment_value'].sum().sort_values(ascending=False)
    revenue_by_method.plot(kind='pie', autopct='%1.1f%%', startangle=90, cmap='tab20')
    plt.title('Revenue Share by Payment Method', fontsize=16, fontweight='bold')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'payment_method_share.png'))
    plt.close()
    print("Generated: payment_method_share.png")


def plot_monthly_avg_installments(df):
    """Trend of average installments over time"""
    plt.figure(figsize=(14, 6))
    monthly_inst = df.groupby('month')['installments'].mean()
    monthly_inst.plot(kind='line', marker='o', color='#8e44ad', linewidth=2)
    plt.title('Average Installment Plan Duration Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Avg. Installments', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'monthly_installments_trend.png'))
    plt.close()
    print("Generated: monthly_installments_trend.png")


def plot_promo_depth_vs_volume(oi_df, promotions_df):
    """Promotion discount depth vs order volume impact"""
    oi_promo = oi_df.merge(promotions_df[['promo_id', 'promo_type', 'discount_value']], on='promo_id', how='inner')
    oi_promo['discount_rate'] = oi_promo['discount_amount'] / (oi_promo['unit_price'] + oi_promo['discount_amount'])
    oi_promo = oi_promo.replace([np.inf, -np.inf], np.nan).dropna(subset=['discount_rate'])

    oi_promo['discount_bin'] = pd.qcut(oi_promo['discount_rate'], q=5, precision=2, duplicates='drop')
    bin_stats = oi_promo.groupby('discount_bin').agg({'discount_rate': 'mean', 'quantity': 'sum'}).reset_index()

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.scatter(bin_stats['discount_rate'], bin_stats['quantity'], s=100, color='#3498db', alpha=0.7)
    ax1.set_xlabel('Average Discount Rate', fontsize=12)
    ax1.set_ylabel('Total Units Sold', fontsize=12, color='#3498db')
    ax1.tick_params(axis='y', labelcolor='#3498db')

    ax2 = ax1.twinx()
    bin_counts = oi_promo.groupby('discount_bin').size()
    ax2.plot(bin_stats['discount_rate'], bin_counts.values, color='#e74c3c', marker='s', linewidth=2)
    ax2.set_ylabel('Number of Orders (with promo)', fontsize=12, color='#e74c3c')
    ax2.tick_params(axis='y', labelcolor='#e74c3c')

    plt.title('Promotion Discount Depth: Volume vs Order Count', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'promo_depth_volume.png'))
    plt.close()
    print("Generated: promo_depth_volume.png")


def plot_customer_ltv_by_payment(df, customers_df):
    """Customer LTV by primary payment method"""
    customer_first = df.groupby('customer_id').first().reset_index()
    customer_ltv = df.groupby('customer_id')['payment_value'].sum().reset_index()
    customer_ltv.columns = ['customer_id', 'ltv']
    merged = customer_first[['customer_id', 'payment_method']].merge(customer_ltv, on='customer_id', how='left')

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=merged, x='payment_method', y='ltv', hue='payment_method',
                palette='Set3', showfliers=False, legend=False, ax=ax)
    ax.set_title('Customer Lifetime Value by Primary Payment Method', fontsize=16, fontweight='bold')
    ax.set_xlabel('Payment Method', fontsize=12)
    ax.set_ylabel('LTV (VND)', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'ltv_by_payment_method.png'))
    plt.close()
    print("Generated: ltv_by_payment_method.png")


def plot_monthly_net_margin_trend(orders_df, order_items_df):
    """Monthly net margin trend (Revenue - COGS - Discounts)"""
    products = pd.read_csv(os.path.join(INPUT_DIR, 'products.csv'))
    oi_with_cogs = order_items_df.merge(products[['product_id', 'cogs']], on='product_id', how='left')
    oi_with_cogs['margin'] = oi_with_cogs['unit_price'] - oi_with_cogs['cogs'] - oi_with_cogs['discount_amount']

    if 'order_date' in order_items_df.columns:
        oi_with_cogs['month'] = order_items_df['order_date'].dt.to_period('M')
    else:
        orders_subset = orders_df[['order_id', 'order_date']].copy()
        oi_with_cogs = oi_with_cogs.merge(orders_subset, on='order_id', how='left')
        oi_with_cogs['month'] = oi_with_cogs['order_date'].dt.to_period('M')

    monthly_margin = oi_with_cogs.groupby('month').agg({'margin': 'sum', 'unit_price': 'sum'})
    monthly_margin['margin_rate'] = monthly_margin['margin'] / monthly_margin['unit_price']

    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax1.plot(monthly_margin.index.astype(str), monthly_margin['unit_price'], color='#2ecc71', linewidth=2, label='Revenue')
    ax1.set_ylabel('Revenue (VND)', fontsize=12, color='#2ecc71')
    ax1.tick_params(axis='y', labelcolor='#2ecc71')
    ax1.set_xlabel('Month', fontsize=12)

    ax2 = ax1.twinx()
    ax2.plot(monthly_margin.index.astype(str), monthly_margin['margin_rate'] * 100, color='#e67e22',
             linewidth=2, marker='o', label='Margin Rate')
    ax2.set_ylabel('Margin Rate (%)', fontsize=12, color='#e67e22')
    ax2.tick_params(axis='y', labelcolor='#e67e22')

    plt.title('Monthly Revenue and Margin Rate Trend', fontsize=16, fontweight='bold')
    plt.xticks(rotation=45)
    fig.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'revenue_margin_trend.png'))
    plt.close()
    print("Generated: revenue_margin_trend.png")


def plot_cac_payback_by_channel(customers_df, orders_df, payments_df):
    """Customer acquisition cost payback period by channel"""
    orders_with_date = orders_df[['order_id', 'customer_id', 'order_date']].copy()
    first_purchase = orders_with_date.groupby('customer_id').first().reset_index()
    first_purchase['days_to_first'] = (first_purchase['order_date'] - first_purchase['order_date'].min()).dt.days

    channel_df = customers_df[['customer_id', 'acquisition_channel']].merge(
        first_purchase[['customer_id', 'days_to_first']], on='customer_id', how='left')
    channel_payback = channel_df.groupby('acquisition_channel')['days_to_first'].median().sort_values()

    plt.figure(figsize=(12, 6))
    channel_payback.plot(kind='barh', color='#34495e')
    plt.title('Median Days to First Purchase by Acquisition Channel (Proxy for CAC Payback)',
              fontsize=16, fontweight='bold')
    plt.xlabel('Median Days to First Purchase', fontsize=12)
    plt.ylabel('Acquisition Channel', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'cac_payback_by_channel.png'))
    plt.close()
    print("Generated: cac_payback_by_channel.png")


def plot_installment_contribution_margin(orders_pay_df):
    """Revenue and margin contribution of installment orders"""
    df = orders_pay_df.copy()
    df['is_installment'] = df['installments'] > 1
    df['month'] = df['order_date'].dt.to_period('M')
    monthly = df.groupby(['month', 'is_installment'])['payment_value'].sum().unstack(fill_value=0)
    monthly['total'] = monthly.sum(axis=1)
    monthly['installment_pct'] = monthly.get(True, 0) / monthly['total'] * 100

    fig, ax1 = plt.subplots(figsize=(14, 6))
    x = np.arange(len(monthly))
    ax1.bar(x, monthly.get(False, 0), label='Non-Installment', color='#95a5a6')
    ax1.bar(x, monthly.get(True, 0), bottom=monthly.get(False, 0), label='Installment', color='#9b59b6')
    ax1.set_ylabel('Revenue (VND)', fontsize=12)
    ax1.set_xlabel('Month', fontsize=12)
    ax1.legend(loc='upper left')

    ax2 = ax1.twinx()
    ax2.plot(x, monthly['installment_pct'], color='#e74c3c', marker='o', linewidth=2, label='Installment %')
    ax2.set_ylabel('Installment Share (%)', fontsize=12, color='#e74c3c')
    ax2.tick_params(axis='y', labelcolor='#e74c3c')
    ax2.legend(loc='upper right')

    plt.title('Monthly Revenue Composition: Installment vs Non-Installment', fontsize=16, fontweight='bold')
    plt.xticks(x[::3], monthly.index.astype(str)[::3], rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'installment_revenue_share.png'))
    plt.close()
    print("Generated: installment_revenue_share.png")


def plot_promo_urgency_stackability(oi_df, promotions_df):
    """NEW (Part 3 Inspired): Urgency (days to promo end) and Stackability Margin Dilution"""
    promo_cols = ['promo_id', 'promo_type', 'discount_value', 'end_date', 'stackable_flag']
    oi_promo = oi_df.merge(promotions_df[promo_cols], on='promo_id', how='inner')

    # Ensure end_date is datetime
    oi_promo['end_date'] = pd.to_datetime(oi_promo['end_date'])
    oi_promo['order_date'] = pd.to_datetime(oi_promo['order_date'])
    oi_promo['days_to_promo_end'] = (oi_promo['end_date'] - oi_promo['order_date']).dt.days
    oi_promo = oi_promo[oi_promo['days_to_promo_end'] >= 0]  # only during active period

    # Cap at 14 days for visualization
    oi_promo['days_to_end_cap'] = oi_promo['days_to_promo_end'].clip(0, 14)

    # Revenue by days to end
    urgency_rev = oi_promo.groupby('days_to_end_cap')['unit_price'].sum().sort_index()

    # Effective discount rate per order line
    oi_promo['discount_rate'] = np.where(
        (oi_promo['unit_price'] + oi_promo['discount_amount']) > 0,
        oi_promo['discount_amount'] / (oi_promo['unit_price'] + oi_promo['discount_amount']),
        np.nan
    )
    oi_promo = oi_promo.dropna(subset=['discount_rate'])

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # --- Urgency Curve: Revenue as countdown to promo end ---
    ax1 = axes[0]
    ax1.bar(urgency_rev.index.astype(str), urgency_rev.values / 1e9, color='#e74c3c', alpha=0.8)
    ax1.invert_xaxis()
    ax1.set_title("Promo Urgency: Revenue Surge Toward End-of-Promo", fontsize=13, fontweight='bold')
    ax1.set_xlabel("Days Until Promo Ends (0 = last day)", fontsize=11)
    ax1.set_ylabel("Revenue (Billion VND)", fontsize=11)
    ax1.grid(axis='y', alpha=0.3)
    # Annotate last 2 days
    for i, (day, rev) in enumerate(zip(urgency_rev.index, urgency_rev.values / 1e9)):
        if day <= 1:
            ax1.text(str(day), rev + rev * 0.02, f'{rev:.2f}B', ha='center', fontsize=9, color='darkred')

    # --- Stackability Margin Dilution ---
    ax2 = axes[1]
    stack_labels = {0: 'Non-Stackable', 1: 'Stackable'}
    oi_promo['stack_label'] = oi_promo['stackable_flag'].map(stack_labels)
    sns.boxplot(data=oi_promo, x='stack_label', y='discount_rate', hue='stack_label',
                palette={'Non-Stackable': '#34495e', 'Stackable': '#e74c3c'},
                showfliers=False, legend=False, ax=ax2)
    ax2.axhline(y=0.30, color='red', linestyle='--', linewidth=2, label='30% Danger Threshold')
    ax2.set_title("Margin Dilution:\nNon-Stackable vs Stackable Promotions", fontsize=13, fontweight='bold')
    ax2.set_xlabel("Promotion Stackability", fontsize=11)
    ax2.set_ylabel("Effective Discount Rate", fontsize=11)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'))
    ax2.legend(loc='upper left')

    plt.suptitle("Part 3 Feature → Part 2 Insight: Promo Urgency & Stackability Risk",
                 fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'promo_urgency_stackability.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print("Generated: promo_urgency_stackability.png")


def main():
    ensure_dir()
    orders_pay, oi_delivered, promotions, customers, payments = load_and_prepare()

    plot_installment_aov_distribution(orders_pay)
    plot_payment_method_market_share(orders_pay)
    plot_monthly_avg_installments(orders_pay)
    plot_promo_depth_vs_volume(oi_delivered, promotions)
    plot_customer_ltv_by_payment(orders_pay, customers)
    plot_monthly_net_margin_trend(orders_pay, oi_delivered)
    plot_cac_payback_by_channel(customers, orders_pay, payments)
    plot_installment_contribution_margin(orders_pay)
    plot_promo_urgency_stackability(oi_delivered, promotions)  # Part 3-inspired new chart

    print("\nAll enhanced financial figures generated (including Part 3 urgency mechanics).")


if __name__ == "__main__":
    main()
