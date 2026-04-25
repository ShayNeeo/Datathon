import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

INPUT_DIR = '/home/shayneeo/Downloads/Datathon/input'
OUTPUT_DIR = '/home/shayneeo/Downloads/Datathon/output/figures_living/01_product_market_dominance'

sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'

def ensure_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def load_and_prepare():
    print("Loading data...")
    products = pd.read_csv(os.path.join(INPUT_DIR, 'products.csv'))
    products = products.rename(columns={'cogs': 'cogs_products'})
    order_items = pd.read_csv(os.path.join(INPUT_DIR, 'order_items.csv'))
    orders = pd.read_csv(os.path.join(INPUT_DIR, 'orders.csv'), parse_dates=['order_date'])
    
    oi = order_items.merge(products[['product_id', 'cogs_products']], on='product_id', how='left')
    oi = oi.merge(orders[['order_id', 'order_date', 'order_status']], on='order_id', how='left')
    oi = oi.merge(products[['product_id', 'category', 'segment']], on='product_id', how='left')
    
    oi_delivered = oi[oi['order_status'] == 'delivered'].copy()
    oi_delivered['month'] = oi_delivered['order_date'].dt.to_period('M')

    # Apply Tet Feature Logic from Part 3
    TET_DATES = {
        2013: "2013-02-10", 2014: "2014-01-31", 2015: "2015-02-19",
        2016: "2016-02-08", 2017: "2017-01-28", 2018: "2018-02-16",
        2019: "2019-02-05", 2020: "2020-01-25", 2021: "2021-02-12",
        2022: "2022-02-01", 2023: "2023-01-22", 2024: "2024-02-10",
    }
    
    oi_delivered['temporal_event'] = 'Normal Day'
    for year, tet_str in TET_DATES.items():
        tet = pd.Timestamp(tet_str)
        approach = (oi_delivered["order_date"] >= tet - pd.Timedelta(days=21)) & (oi_delivered["order_date"] < tet)
        holiday  = (oi_delivered["order_date"] >= tet) & (oi_delivered["order_date"] < tet + pd.Timedelta(days=7))
        recovery = (oi_delivered["order_date"] >= tet + pd.Timedelta(days=7)) & (oi_delivered["order_date"] < tet + pd.Timedelta(days=21))
        
        oi_delivered.loc[approach, 'temporal_event'] = 'Tet Approach'
        oi_delivered.loc[holiday, 'temporal_event'] = 'Tet Holiday'
        oi_delivered.loc[recovery, 'temporal_event'] = 'Tet Recovery'

    # Add Double Day Logic
    is_double = (
        ((oi_delivered['order_date'].dt.month == 9) & (oi_delivered['order_date'].dt.day == 9)) |
        ((oi_delivered['order_date'].dt.month == 10) & (oi_delivered['order_date'].dt.day == 10)) |
        ((oi_delivered['order_date'].dt.month == 11) & (oi_delivered['order_date'].dt.day == 11)) |
        ((oi_delivered['order_date'].dt.month == 12) & (oi_delivered['order_date'].dt.day == 12))
    )
    oi_delivered.loc[is_double, 'temporal_event'] = 'Double Day Promo'

    return oi_delivered, products

def plot_segment_market_share(oi_df, products_df):
    plt.figure(figsize=(10, 8))
    segment_revenue = oi_df.groupby('segment')['unit_price'].sum().sort_values(ascending=False)
    plt.figure(figsize=(10, 8))
    colors = plt.cm.Set2(np.linspace(0, 1, len(segment_revenue)))
    wedges, texts, autotexts = plt.pie(segment_revenue, labels=segment_revenue.index, 
                                    autopct='%1.1f%%', colors=colors, startangle=90)
    plt.setp(autotexts, size=10, weight="bold", color="white")
    plt.setp(texts, size=12)
    plt.title('Market Share by Segment', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'segment_market_share_new.png'))
    plt.close()
    print("Generated: segment_market_share_new.png")

def plot_size_profitability(oi_df, products_df):
    plt.figure(figsize=(12, 7))
    oi_merged = oi_df.merge(products_df[['product_id', 'size']], on='product_id', how='left')
    oi_merged['profit'] = oi_merged['unit_price'] - oi_merged['cogs_products']
    oi_merged['profit_margin'] = oi_merged['profit'] / oi_merged['unit_price']
    size_margin = oi_merged.groupby('size')['profit_margin'].mean().sort_values(ascending=False)
    colors = ['#2ecc71' if x > 0.3 else '#f39c12' if x > 0.2 else '#e74c3c' for x in size_margin]
    bars = plt.bar(size_margin.index, size_margin.values, color=colors, edgecolor='white', linewidth=1.5)
    plt.axhline(y=size_margin.mean(), color='gray', linestyle='--', alpha=0.7, label=f'Avg: {size_margin.mean():.1%}')
    plt.title('Average Profit Margin by Size', fontsize=16, fontweight='bold')
    plt.xlabel('Size', fontsize=12)
    plt.ylabel('Profit Margin', fontsize=12)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'size_profitability_new.png'))
    plt.close()
    print("Generated: size_profitability_new.png")

def plot_size_profitability_boxplot(oi_df, products_df):
    plt.figure(figsize=(14, 7))
    oi_merged = oi_df.merge(products_df[['product_id', 'size']], on='product_id', how='left')
    oi_merged['profit'] = oi_merged['unit_price'] - oi_merged['cogs_products']
    oi_merged['profit_margin'] = oi_merged['profit'] / oi_merged['unit_price']
    df_plot = oi_merged[oi_merged['unit_price'] < oi_merged['unit_price'].quantile(0.99)]
    sns.boxplot(data=df_plot, x='size', y='profit_margin', palette='RdYlGn')
    plt.title('Profit Margin Distribution by Size', fontsize=16, fontweight='bold')
    plt.xlabel('Size', fontsize=12)
    plt.ylabel('Profit Margin', fontsize=12)
    plt.axhline(y=0, color='red', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'size_profitability_boxplot.png'))
    plt.close()
    print("Generated: size_profitability_boxplot.png")

def plot_monthly_trend_heatmap(oi_df, products_df):
    import matplotlib.ticker as ticker
    import matplotlib.dates as mdates
    oi_df = oi_df.copy()
    oi_df['year_month'] = oi_df['order_date'].dt.to_period('M')
    oi_df['year_month_str'] = oi_df['year_month'].astype(str)
    monthly = oi_df.groupby(['year_month_str', 'category'])['unit_price'].sum().reset_index()
    monthly_pivot = monthly.pivot(index='year_month_str', columns='category', values='unit_price').fillna(0)
    monthly_millions = monthly_pivot / 1_000_000
    n_months = len(monthly_pivot)
    fig_height = 8
    fig_width = max(18, min(28, n_months * 0.12 + 4))
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    if len(monthly_pivot) > 0:
        sns.heatmap(monthly_millions.T, cmap='YlOrRd', annot=True, fmt='.0f', annot_kws={'size': 6}, 
                    cbar_kws={'label': 'Revenue (Million VND)'}, ax=ax, linewidths=0.1, linecolor='white')
        plt.title('Monthly Revenue Trends by Category (2012-2022)\nValues in Million VND', fontsize=14, fontweight='bold')
        plt.xlabel('Year-Month', fontsize=12)
        plt.ylabel('Category', fontsize=12)
        plt.xticks(rotation=45, ha='right', fontsize=7)
        plt.yticks(fontsize=10)
        ax.set_xticks(range(n_months))
        ax.set_xticklabels(monthly_pivot.index.tolist(), rotation=45, ha='right', fontsize=7)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'monthly_trend_heatmap.png'), dpi=150, bbox_inches='tight')
        plt.close()
        print("Generated: monthly_trend_heatmap.png (READABLE: Year-Month labels, Revenue in Millions)")

def plot_top_products_treemap(oi_df, products_df):
    product_revenue = oi_df[['product_id', 'unit_price']].copy()
    product_revenue = product_revenue.merge(products_df[['product_id', 'product_name', 'category']], on='product_id', how='left')
    product_revenue = product_revenue.groupby(['product_id', 'product_name', 'category'])['unit_price'].sum().reset_index()
    product_revenue = product_revenue.sort_values('unit_price', ascending=False).head(50)
    norm_sizes = product_revenue['unit_price'] / product_revenue['unit_price'].sum() * 100
    fig, ax = plt.subplots(figsize=(18, 12))
    y_positions = np.arange(len(product_revenue))
    unique_cats = product_revenue['category'].unique()
    colors = plt.cm.tab20(np.linspace(0, 1, len(unique_cats)))
    category_color_map = {cat: colors[i] for i, cat in enumerate(unique_cats)}
    ax.barh(y_positions, norm_sizes.values, left=np.zeros(len(product_revenue)),
           color=[category_color_map[cat] for cat in product_revenue['category']],
           edgecolor='white', height=0.7)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(product_revenue['product_name'], fontsize=8)
    ax.set_xlabel('Revenue Share (%)', fontsize=12)
    ax.set_title('Top 50 Products by Revenue (Treemap Style)', fontsize=16, fontweight='bold')
    for i, (name, val) in enumerate(zip(product_revenue['product_name'], norm_sizes.values)):
        if val > 2:
            ax.text(val + 0.5, i, f'{val:.1f}%', va='center', fontsize=7)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'top_products_treemap.png'), dpi=150)
    plt.close()
    print("Generated: top_products_treemap.png")

def plot_segment_profitability_heatmap(oi_df, products_df):
    plt.figure(figsize=(12, 8))
    oi_merged = oi_df.merge(products_df[['product_id', 'size']], on='product_id', how='left')
    oi_merged['profit'] = oi_merged['unit_price'] - oi_merged['cogs_products']
    oi_merged['profit_margin'] = oi_merged['profit'] / oi_merged['unit_price']
    pivot = oi_merged.pivot_table(index='segment', columns='size', values='profit_margin', aggfunc='mean')
    if not pivot.empty:
        sns.heatmap(pivot, annot=True, fmt='.3f', cmap='RdYlGn', center=0, 
                    vmin=-0.5, vmax=0.5, cbar_kws={'label': 'Avg Profit Margin'})
        plt.title('Profitability by Segment and Size', fontsize=16, fontweight='bold')
        plt.xlabel('Size', fontsize=12)
        plt.ylabel('Segment', fontsize=12)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'segment_profitability_heatmap.png'))
        plt.close()
        print("Generated: segment_profitability_heatmap.png")

def plot_pareto_curve(oi_df):
    plt.figure(figsize=(12, 6))
    product_revenue = oi_df.groupby('product_id')['unit_price'].sum().sort_values(ascending=False)
    cumsum = product_revenue.cumsum()
    cumulative_pct = cumsum / cumsum.iloc[-1] * 100
    fig, ax1 = plt.subplots(figsize=(12, 6))
    x = np.arange(len(product_revenue))
    ax1.bar(x, product_revenue.values, color='#3498db', alpha=0.7, width=0.8)
    ax1.set_xlabel('Product Rank', fontsize=12)
    ax1.set_ylabel('Revenue (VND)', fontsize=12, color='#3498db')
    ax1.tick_params(axis='y', labelcolor='#3498db')
    ax2 = ax1.twinx()
    ax2.plot(x, cumulative_pct.values, color='#e74c3c', marker='o', markersize=3, linewidth=2)
    ax2.axhline(y=80, color='gray', linestyle='--', alpha=0.5, label='80% threshold')
    ax2.set_ylabel('Cumulative Revenue %', fontsize=12, color='#e74c3c')
    ax2.tick_params(axis='y', labelcolor='#e74c3c')
    ax2.set_ylim(0, 105)
    ax1.set_title('Product Revenue Pareto Analysis', fontsize=16, fontweight='bold')
    key_points = [0, len(product_revenue)//4, len(product_revenue)//2, 3*len(product_revenue)//4, -1]
    for pt in key_points:
        if pt >= 0 and pt < len(cumulative_pct):
            ax2.annotate(f'{cumulative_pct.iloc[pt]:.1f}%', 
                        (pt, cumulative_pct.iloc[pt]),
                        textcoords="offset points", xytext=(10,10), fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'pareto_analysis.png'))
    plt.close()
    print("Generated: pareto_analysis.png")

def plot_cross_sell_opportunities(oi_df, products_df):
    plt.figure(figsize=(14, 8))
    oi_merged = oi_df.merge(products_df[['product_id', 'size']], on='product_id', how='left')
    combo_revenue = oi_merged.groupby(['segment', 'size'])['unit_price'].agg(['sum', 'count']).reset_index()
    combo_revenue['avg_price'] = combo_revenue['sum'] / combo_revenue['count']
    pivot = combo_revenue.pivot(index='segment', columns='size', values='avg_price')
    if not pivot.empty:
        sns.heatmap(pivot, annot=True, fmt='.0f', cmap='Blues', cbar_kws={'label': 'Avg Order Value'})
        plt.title('Cross-Sell Opportunities: Segment-Size Combinations', fontsize=16, fontweight='bold')
        plt.xlabel('Size', fontsize=12)
        plt.ylabel('Segment', fontsize=12)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'cross_sell_opportunities.png'))
        plt.close()
        print("Generated: cross_sell_opportunities.png")

def plot_temporal_product_shifts(oi_df):
    """New Function: Tet vs Double Day Segment shifts"""
    plt.figure(figsize=(14, 8))
    
    # Calculate revenue share per segment during each temporal event
    event_segment = oi_df.groupby(['temporal_event', 'segment'])['unit_price'].sum().unstack()
    event_segment_pct = event_segment.div(event_segment.sum(axis=1), axis=0) * 100
    
    event_segment_pct.loc[['Normal Day', 'Tet Approach', 'Double Day Promo']].plot(
        kind='bar', stacked=True, colormap='tab20', figsize=(12, 7)
    )
    plt.title('Product Segment Shift by Temporal Event\n(Normal vs Tet vs Double Day)', fontsize=16, fontweight='bold')
    plt.ylabel('Revenue Share (%)', fontsize=12)
    plt.xlabel('Event Phase', fontsize=12)
    plt.xticks(rotation=0)
    plt.legend(title='Product Segment', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'temporal_product_shifts.png'))
    plt.close()
    print("Generated: temporal_product_shifts.png")

def main():
    ensure_dir()
    oi_df, products_df = load_and_prepare()
    print(f'Data loaded: {len(oi_df)} delivered order items')
    
    plot_segment_market_share(oi_df, products_df)
    plot_size_profitability(oi_df, products_df)
    plot_size_profitability_boxplot(oi_df, products_df)
    plot_monthly_trend_heatmap(oi_df, products_df)
    plot_top_products_treemap(oi_df, products_df)
    plot_segment_profitability_heatmap(oi_df, products_df)
    plot_pareto_curve(oi_df)
    plot_cross_sell_opportunities(oi_df, products_df)
    plot_temporal_product_shifts(oi_df)  # Added function
    
    print("\nAll enhanced product market figures generated successfully.")

if __name__ == "__main__":
    main()
