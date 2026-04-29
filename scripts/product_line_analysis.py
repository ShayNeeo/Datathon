import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
import numpy as np
import re

INPUT_DIR = '/home/shayneeo/Downloads/Datathon/input'
OUTPUT_DIR = '/home/shayneeo/Downloads/Datathon/output/figures_living'
REPO_ROOT = '/home/shayneeo/Downloads/Datathon'

if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

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

sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def load_data():
    print("Loading data...")
    products = pd.read_csv(os.path.join(INPUT_DIR, 'products.csv'))
    products = products.rename(columns={'cogs': 'cogs_products'})
    order_items = pd.read_csv(os.path.join(INPUT_DIR, 'order_items.csv'))
    orders = pd.read_csv(os.path.join(INPUT_DIR, 'orders.csv'), parse_dates=['order_date'])
    customers = pd.read_csv(os.path.join(INPUT_DIR, 'customers.csv'))
    
    # Extract brand (first word) and line code (middle part like UC, UM, etc.)
    products['brand'] = products['product_name'].str.split().str[0]
    products['line_code'] = products['product_name'].str.extract(r'([A-Z]+)-')[0]
    products['margin_pct'] = (products['price'] - products['cogs_products']) / products['price']
    
    # Merge data (need customer_id from orders first)
    oi = order_items.merge(orders[['order_id', 'order_date', 'order_status', 'customer_id']], on='order_id', how='left')
    oi = oi.merge(products[['product_id', 'cogs_products', 'brand', 'line_code', 'category', 'segment', 'size', 'margin_pct']], on='product_id', how='left')
    
    oi_delivered = oi[oi['order_status'] == 'delivered'].copy()
    oi_delivered['month'] = oi_delivered['order_date'].dt.to_period('M')
    
    # Also attach customer info (map to available columns)
    customer_cols = customers[['customer_id', 'gender', 'age_group', 'city', 'acquisition_channel']].copy()
    customer_cols = customer_cols.rename(columns={
        'age_group': 'age',
        'city': 'location',
        'acquisition_channel': 'device'
    })
    oi_with_cust = oi_delivered.merge(customer_cols, on='customer_id', how='left')
    
    return oi_delivered, oi_with_cust, products

def plot_star_vs_bait(oi_df, products_df):
    """Star vs Bait Analysis - Product line portfolio optimization"""
    output_path = os.path.join(OUTPUT_DIR, '01_product_market_dominance')
    ensure_dir(output_path)
    
    # Calculate metrics by line_code
    line_stats = products_df.groupby('line_code').agg({
        'price': 'mean',
        'margin_pct': 'mean',
        'product_id': 'count'
    }).rename(columns={'product_id': 'product_count'})
    line_stats = line_stats.sort_values('margin_pct', ascending=False)
    
    # Classify stars vs bait
    avg_margin = line_stats['margin_pct'].mean()
    line_stats['classification'] = line_stats['margin_pct'].apply(
        lambda x: 'STAR' if x > avg_margin * 1.1 else ('BAIT' if x < avg_margin * 0.9 else 'BALANCED')
    )
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    
    # 1. Bar chart: Price vs Margin by line code
    ax1 = axes[0, 0]
    colors = ['#009E73' if x > avg_margin * 1.1 else '#D55E00' if x < avg_margin * 0.9 else '#E69F00' for x in line_stats['margin_pct']]
    bars = ax1.bar(range(len(line_stats)), line_stats['margin_pct'] * 100, color=colors, edgecolor='white', linewidth=1.5)
    ax1.set_xticks(range(len(line_stats)))
    ax1.set_xticklabels(line_stats.index, rotation=45, ha='right')
    ax1.axhline(y=avg_margin * 100, color='gray', linestyle='--', alpha=0.7, label=f'Avg: {avg_margin*100:.1f}%')
    ax1.set_title('Margin by Line Code (Star vs Bait)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Line Code', fontsize=12)
    ax1.set_ylabel('Margin %', fontsize=12)
    ax1.legend()
    
    # 2. Scatter: Price vs Margin with product count
    ax2 = axes[0, 1]
    scatter = ax2.scatter(line_stats['price'], line_stats['margin_pct'] * 100, 
                       s=line_stats['product_count'] * 10, 
                       c=line_stats['margin_pct'], cmap='RdYlGn', alpha=0.7, edgecolors='black')
    for i, txt in enumerate(line_stats.index):
        ax2.annotate(txt, (line_stats['price'].iloc[i], line_stats['margin_pct'].iloc[i] * 100), 
                    fontsize=9, ha='center', va='bottom')
    ax2.set_title('Price vs Margin (Size = Product Count)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Average Price (VND)', fontsize=12)
    ax2.set_ylabel('Margin %', fontsize=12)
    plt.colorbar(scatter, ax=ax2, label='Margin %')
    
    # 3. Horizontal bar: Product count by line
    ax3 = axes[1, 0]
    line_stats_sorted = line_stats.sort_values('product_count', ascending=True)
    colors3 = ['#009E73' if c == 'STAR' else '#D55E00' if c == 'BAIT' else '#E69F00' for c in line_stats_sorted['classification']]
    ax3.barh(line_stats_sorted.index, line_stats_sorted['product_count'], color=colors3, edgecolor='white')
    ax3.set_title('Product Count by Line Code', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Number of Products', fontsize=12)
    
    # 4. Classification pie chart
    ax4 = axes[1, 1]
    class_counts = line_stats['classification'].value_counts()
    colors4 = {'STAR': '#009E73', 'BALANCED': '#E69F00', 'BAIT': '#D55E00'}
    ax4.pie(class_counts, labels=class_counts.index, autopct='%1.0f%%', 
           colors=[colors4[c] for c in class_counts.index], startangle=90)
    ax4.set_title('Line Code Classification', fontsize=14, fontweight='bold')
    
    # Professional Styling
    apply_editorial_style(fig, axes[0,0], "Star vs Bait Analysis: Product Portfolio", "Identifying high-margin growth drivers vs low-margin traffic generators")
    
    # Native callout
    add_callout(axes[1,1], "Prioritize STAR expansion", xy=(0.5, 0.5), xytext=(0.5, 0.8), color='#009E73')

    plt.tight_layout()
    plt.savefig(os.path.join(output_path, 'star_vs_bait_analysis.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Generated: {output_path}/star_vs_bait_analysis.png")
    
    return line_stats

def plot_brand_performance(oi_df, products_df):
    """Brand performance analysis"""
    output_path = os.path.join(OUTPUT_DIR, '01_product_market_dominance')
    
    brand_stats = products_df.groupby('brand').agg({
        'price': 'mean',
        'margin_pct': 'mean',
        'product_id': 'count'
    }).rename(columns={'product_id': 'product_count'})
    brand_stats = brand_stats.sort_values('margin_pct', ascending=False)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    x = np.arange(len(brand_stats))
    width = 0.35
    
    ax.bar(x - width/2, brand_stats['margin_pct'] * 100, width, label='Margin %', color='#3498db', alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(brand_stats.index, rotation=45, ha='right')
    ax.set_ylabel('Margin %', fontsize=12, color='#3498db')
    ax.tick_params(axis='y', labelcolor='#3498db')
    
    ax2 = ax.twinx()
    ax2.bar(x + width/2, brand_stats['product_count'], width, label='Product Count', color='#e74c3c', alpha=0.6)
    ax2.set_ylabel('Product Count', fontsize=12, color='#e74c3c')
    ax2.tick_params(axis='y', labelcolor='#e74c3c')
    
    ax.set_title('Brand Performance: Margin vs Product Count', fontsize=16, fontweight='bold')
    ax.set_xlabel('Brand', fontsize=12)
    
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, 'brand_performance.png'), dpi=150)
    plt.close()
    print(f"Generated: {output_path}/brand_performance.png")
    
    return brand_stats

def plot_line_by_customer_segment(oi_df, products_df):
    """Which product lines drive which customer segments"""
    output_path = os.path.join(OUTPUT_DIR, '02_customer_lifecycle_acquisition')
    ensure_dir(output_path)
    
    # oi_df already has line_code from load_data
    oi_merged = oi_df
    
    # Calculate revenue by line_code
    line_revenue = oi_merged.groupby('line_code')['unit_price'].sum().sort_values(ascending=False)
    line_count = oi_merged.groupby('line_code').size().sort_values(ascending=False)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # Revenue by line code
    axes[0].bar(range(len(line_revenue)), line_revenue.values, color='#3498db', edgecolor='white')
    axes[0].set_xticks(range(len(line_revenue)))
    axes[0].set_xticklabels(line_revenue.index, rotation=45, ha='right')
    axes[0].set_title('Revenue by Product Line', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Line Code', fontsize=12)
    axes[0].set_ylabel('Revenue (VND)', fontsize=12)
    
    # Order count by line code
    axes[1].bar(range(len(line_count)), line_count.values, color='#e74c3c', edgecolor='white')
    axes[1].set_xticks(range(len(line_count)))
    axes[1].set_xticklabels(line_count.index, rotation=45, ha='right')
    axes[1].set_title('_order Count by Product Line', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Line Code', fontsize=12)
    axes[1].set_ylabel('Order Count', fontsize=12)
    
    plt.suptitle('Product Line Performance in Customer Acquisition', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, 'line_revenue_acquisition.png'), dpi=150)
    plt.close()
    print(f"Generated: {output_path}/line_revenue_acquisition.png")

def plot_line_operational_friction(oi_df, products_df):
    """Product line operational friction analysis"""
    output_path = os.path.join(OUTPUT_DIR, '03_operational_friction_leakage')
    ensure_dir(output_path)
    
    # Get all orders (not just delivered) to see friction
    order_items = pd.read_csv(os.path.join(INPUT_DIR, 'order_items.csv'))
    orders = pd.read_csv(os.path.join(INPUT_DIR, 'orders.csv'), parse_dates=['order_date'])
    
    oi_all = order_items.merge(products_df[['product_id', 'line_code', 'brand']], on='product_id', how='left')
    oi_all = oi_all.merge(orders[['order_id', 'order_status']], on='order_id', how='left')
    
    # Calculate cancellation/failure rate by line
    line_status = oi_all.groupby(['line_code', 'order_status']).size().unstack(fill_value=0)
    
    if 'cancelled' in line_status.columns or 'failed' in line_status.columns:
        total = line_status.sum(axis=1)
        failed = 0
        if 'cancelled' in line_status.columns:
            failed += line_status['cancelled']
        if 'failed' in line_status.columns:
            failed += line_status['failed']
        
        failure_rate = (failed / total * 100).sort_values(ascending=False)
        
        fig, ax = plt.subplots(figsize=(14, 7))
        bars = ax.bar(range(len(failure_rate)), failure_rate.values, 
                   color=['#e74c3c' if x > 10 else '#f39c12' if x > 5 else '#2ecc71' for x in failure_rate.values],
                   edgecolor='white')
        ax.set_xticks(range(len(failure_rate)))
        ax.set_xticklabels(failure_rate.index, rotation=45, ha='right')
        ax.axhline(y=10, color='red', linestyle='--', alpha=0.5, label='Critical 10%')
        ax.axhline(y=5, color='orange', linestyle='--', alpha=0.5, label='Warning 5%')
        ax.set_title('Order Failure Rate by Product Line', fontsize=16, fontweight='bold')
        ax.set_xlabel('Line Code', fontsize=12)
        ax.set_ylabel('Failure Rate %', fontsize=12)
        
        # Professional Styling
        apply_editorial_style(fig, ax, "Order Failure Rate by Product Line", "Identifying operational leakage across major product lines")

        # Native callout
        add_callout(ax, "Significant failure hotspots", xy=(0, 10), xytext=(2, 15), color='#D55E00')

        ax.legend(frameon=False)
        plt.tight_layout()
        plt.savefig(os.path.join(output_path, 'line_failure_rate.png'), dpi=150)
        plt.close()
        print(f"Generated: {output_path}/line_failure_rate.png")

    else:
        print("No failure data available for line analysis")

def plot_line_financial_impact(oi_df, products_df):
    """Product line financial impact analysis"""
    output_path = os.path.join(OUTPUT_DIR, '04_financial_payment_dynamics')
    ensure_dir(output_path)
    
    # Revenue and margin by line
    oi_merged = oi_df.copy()
    oi_merged['profit'] = oi_merged['unit_price'] - oi_merged['cogs_products']
    
    line_financial = oi_merged.groupby('line_code').agg({
        'unit_price': 'sum',
        'profit': 'sum'
    })
    line_financial['margin'] = line_financial['profit'] / line_financial['unit_price'] * 100
    line_financial = line_financial.sort_values('unit_price', ascending=False)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # Revenue by line
    axes[0].bar(range(len(line_financial)), line_financial['unit_price'], color='#3498db', edgecolor='white')
    axes[0].set_xticks(range(len(line_financial)))
    axes[0].set_xticklabels(line_financial.index, rotation=45, ha='right')
    axes[0].set_title('Revenue by Product Line', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Revenue (VND)', fontsize=12)
    
    # Margin by line
    axes[1].bar(range(len(line_financial)), line_financial['margin'], color='#2ecc71', edgecolor='white')
    axes[1].set_xticks(range(len(line_financial)))
    axes[1].set_xticklabels(line_financial.index, rotation=45, ha='right')
    axes[1].set_title('Margin % by Product Line', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('Margin %', fontsize=12)
    
    plt.suptitle('Product Line Financial Impact', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, 'line_financial_impact.png'), dpi=150)
    plt.close()
    print(f"Generated: {output_path}/line_financial_impact.png")

def main():
    oi_df, oi_with_cust, products_df = load_data()
    
    print("\n=== Generating Star vs Bait Analysis for 01 ===")
    line_stats = plot_star_vs_bait(oi_df, products_df)
    brand_stats = plot_brand_performance(oi_df, products_df)
    
    print("\n=== Generating Customer Acquisition Analysis for 02 ===")
    plot_line_by_customer_segment(oi_df, products_df)
    
    print("\n=== Generating Operational Friction Analysis for 03 ===")
    plot_line_operational_friction(oi_df, products_df)
    
    print("\n=== Generating Financial Impact Analysis for 04 ===")
    plot_line_financial_impact(oi_df, products_df)

    print("\n=== Product Line Analysis Complete ===")
    print("\nLine Code Statistics:")
    print(line_stats)

if __name__ == "__main__":
    main()
