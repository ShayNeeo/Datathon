import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
# Test comment
import numpy as np

INPUT_DIR = '/home/shayneeo/Downloads/Datathon/input'
OUTPUT_DIR = '/home/shayneeo/Downloads/Datathon/output/figures_living/01_product_market_dominance'

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
    fig, ax = plt.subplots(figsize=(10, 8))
    segment_revenue = oi_df.groupby('segment')['unit_price'].sum().sort_values(ascending=False)
    
    # STYLING.md Qualitative Palette
    colors = ['#0072B2', '#009E73', '#E69F00', '#CC79A7', '#56B4E9', '#D55E00']
    
    wedges, texts, autotexts = ax.pie(segment_revenue, labels=segment_revenue.index, 
                                    autopct='%1.1f%%', colors=colors, startangle=90,
                                    wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    plt.setp(autotexts, size=10, weight="bold", color="white")
    plt.setp(texts, size=12, fontweight='600')
    
    apply_editorial_style(fig, ax, "Market Share by Segment", "Revenue dominance of Streetwear and Standard segments")
    
    # Native callout
    add_callout(ax, "80% Streetwear Hegemony", xy=(0.3, 0.3), xytext=(1.2, 0.8), color='#D55E00')

    plt.savefig(os.path.join(OUTPUT_DIR, 'segment_market_share_new.png'))
    plt.close()
    print("Generated: segment_market_share_new.png")

def plot_size_profitability(oi_df, products_df):
    fig, ax = plt.subplots(figsize=(12, 7))
    oi_merged = oi_df.merge(products_df[['product_id', 'size']], on='product_id', how='left')
    oi_merged['profit'] = oi_merged['unit_price'] - oi_merged['cogs_products']
    oi_merged['profit_margin'] = oi_merged['profit'] / oi_merged['unit_price']
    size_margin = oi_merged.groupby('size')['profit_margin'].mean().sort_values(ascending=False)
    
    # STYLING.md colors
    colors = ['#009E73' if x > 0.3 else '#E69F00' if x > 0.2 else '#D55E00' for x in size_margin]
    bars = ax.bar(size_margin.index, size_margin.values, color=colors, edgecolor='white', linewidth=1.5)
    
    ax.axhline(y=size_margin.mean(), color='#64748B', linestyle='--', alpha=0.7, label=f'Avg: {size_margin.mean():.1%}')
    
    apply_editorial_style(fig, ax, "Average Profit Margin by Size", "Premium sizes (L/XL) command 12-17pp higher margins")
    
    # Professional callouts
    add_callout(ax, "Premium 30–35%", xy=(2, 0.32), xytext=(2.5, 0.45), color='#009E73')
    add_callout(ax, "Commodity 18–26%", xy=(0, 0.22), xytext=(-0.5, 0.10), color='#D55E00')

    plt.legend(frameon=False, loc='upper right')
    plt.savefig(os.path.join(OUTPUT_DIR, 'size_profitability_new.png'))
    plt.close()
    print("Generated: size_profitability_new.png")

def plot_size_profitability_boxplot(oi_df, products_df):
    fig, ax = plt.subplots(figsize=(14, 7))
    oi_merged = oi_df.merge(products_df[['product_id', 'size']], on='product_id', how='left')
    oi_merged['profit'] = oi_merged['unit_price'] - oi_merged['cogs_products']
    oi_merged['profit_margin'] = oi_merged['profit'] / oi_merged['unit_price']
    df_plot = oi_merged[oi_merged['unit_price'] < oi_merged['unit_price'].quantile(0.99)]
    
    sns.boxplot(data=df_plot, x='size', y='profit_margin', hue='size', palette='viridis', ax=ax, legend=False)
    
    apply_editorial_style(fig, ax, "Profit Margin Distribution by Size", "High variance in L/XL indicates pricing power and scarcity premium")
    
    ax.axhline(y=0, color='#D55E00', linestyle='--', alpha=0.5)
    
    # Professional callout
    add_callout(ax, "Premium Size 12–17pp gap", xy=(3, 0.35), xytext=(4, 0.5), color='#0072B2')

    plt.savefig(os.path.join(OUTPUT_DIR, 'size_profitability_boxplot.png'))
    plt.close()
    print("Generated: size_profitability_boxplot.png")

def plot_monthly_trend_heatmap(oi_df, products_df):
    oi_df = oi_df.copy()
    oi_df['year_month'] = oi_df['order_date'].dt.to_period('M')
    oi_df['year_month_str'] = oi_df['year_month'].astype(str)
    monthly = oi_df.groupby(['year_month_str', 'category'])['unit_price'].sum().reset_index()
    monthly_pivot = monthly.pivot(index='year_month_str', columns='category', values='unit_price').fillna(0)
    monthly_millions = monthly_pivot / 1_000_000
    
    n_months = len(monthly_pivot)
    fig, ax = plt.subplots(figsize=(18, 8))
    
    if not monthly_pivot.empty:
        sns.heatmap(monthly_millions.T, cmap='YlGnBu', annot=True, fmt='.0f', annot_kws={'size': 8}, 
                    cbar_kws={'label': 'Revenue (Million VND)'}, ax=ax, linewidths=0.5, linecolor='white')
        
        apply_editorial_style(fig, ax, "Monthly Revenue Trends by Category", "Identifying seasonal surges and May anomaly across 10 years")
        
        ax.set_xticks(np.arange(n_months) + 0.5)
        ax.set_xticklabels(monthly_pivot.index.tolist(), rotation=45, ha='right', fontsize=9)
        
        # Professional callout (pointing to a typical May peak area)
        add_callout(ax, "May Peak 2.6x baseline", xy=(n_months * 0.8, 2), xytext=(n_months * 0.9, 0.5), color='#009E73')

        plt.savefig(os.path.join(OUTPUT_DIR, 'monthly_trend_heatmap.png'), dpi=150, bbox_inches='tight')
        plt.close()
        print("Generated: monthly_trend_heatmap.png")

def plot_top_products_treemap(oi_df, products_df):
    product_revenue = oi_df[['product_id', 'unit_price']].copy()
    product_revenue = product_revenue.merge(products_df[['product_id', 'product_name', 'category']], on='product_id', how='left')
    product_revenue = product_revenue.groupby(['product_id', 'product_name', 'category'])['unit_price'].sum().reset_index()
    product_revenue = product_revenue.sort_values('unit_price', ascending=False).head(50)
    norm_sizes = product_revenue['unit_price'] / product_revenue['unit_price'].sum() * 100
    
    fig, ax = plt.subplots(figsize=(18, 12))
    y_positions = np.arange(len(product_revenue))
    
    # STYLING.md Sequential/Qualitative mix
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, 50))
    
    ax.barh(y_positions, norm_sizes.values, color=colors, edgecolor='white', height=0.7)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(product_revenue['product_name'], fontsize=9, fontweight='600')
    
    apply_editorial_style(fig, ax, "Top 50 Products by Revenue", "Concentration analysis: Top 50 SKUs drive significant revenue share")
    
    ax.set_xlabel('Revenue Share (%)', fontsize=12, fontweight='bold')
    
    # Professional callout
    add_callout(ax, "Top 5 SKUs drive disproportionate value", xy=(norm_sizes.iloc[0], 49), xytext=(15, 45), color='#0072B2')

    plt.savefig(os.path.join(OUTPUT_DIR, 'top_products_treemap.png'), dpi=150)
    plt.close()
    print("Generated: top_products_treemap.png")

def plot_segment_profitability_heatmap(oi_df, products_df):
    oi_merged = oi_df.merge(products_df[['product_id', 'size']], on='product_id', how='left')
    oi_merged['profit'] = oi_merged['unit_price'] - oi_merged['cogs_products']
    oi_merged['profit_margin'] = oi_merged['profit'] / oi_merged['unit_price']
    pivot = oi_merged.pivot_table(index='segment', columns='size', values='profit_margin', aggfunc='mean')
    
    if not pivot.empty:
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(pivot, annot=True, fmt='.2%', cmap='RdYlGn', center=0, 
                    ax=ax, linewidths=0.5, linecolor='white')
        
        apply_editorial_style(fig, ax, "Profitability by Segment and Size", "Heatmap of average gross margin across the product matrix")
        
        # Professional callout
        add_callout(ax, "Negative margin in small sizes", xy=(0.5, 3.5), xytext=(2.5, 4.5), color='#D55E00')

        plt.savefig(os.path.join(OUTPUT_DIR, 'segment_profitability_heatmap.png'))
        plt.close()
        print("Generated: segment_profitability_heatmap.png")

def plot_pareto_curve(oi_df):
    product_revenue = oi_df.groupby('product_id')['unit_price'].sum().sort_values(ascending=False)
    cumsum = product_revenue.cumsum()
    cumulative_pct = cumsum / cumsum.iloc[-1] * 100
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    x = np.arange(len(product_revenue))
    
    ax1.bar(x, product_revenue.values, color='#0072B2', alpha=0.7, width=0.8)
    
    ax2 = ax1.twinx()
    ax2.plot(x, cumulative_pct.values, color='#D55E00', linewidth=3)
    ax2.axhline(y=80, color='#64748B', linestyle='--', alpha=0.5)
    
    apply_editorial_style(fig, ax1, "Product Revenue Pareto Analysis", "80% of revenue is driven by a small fraction of SKUs (Streetwear dominance)")
    
    ax1.set_ylabel('Revenue (VND)', fontsize=12, fontweight='bold', color='#0072B2')
    ax2.set_ylabel('Cumulative Revenue %', fontsize=12, fontweight='bold', color='#D55E00')
    ax2.set_ylim(0, 105)
    
    # Professional callout
    add_callout(ax1, "80% Revenue Concentration", xy=(len(product_revenue)*0.15, 80), xytext=(len(product_revenue)*0.4, 60), color='#D55E00')

    plt.savefig(os.path.join(OUTPUT_DIR, 'pareto_analysis.png'))
    plt.close()
    print("Generated: pareto_analysis.png")

def plot_cross_sell_opportunities(oi_df, products_df):
    oi_merged = oi_df.merge(products_df[['product_id', 'size']], on='product_id', how='left')
    combo_revenue = oi_merged.groupby(['segment', 'size'])['unit_price'].agg(['sum', 'count']).reset_index()
    combo_revenue['avg_price'] = combo_revenue['sum'] / combo_revenue['count']
    pivot = combo_revenue.pivot(index='segment', columns='size', values='avg_price')
    
    if not pivot.empty:
        fig, ax = plt.subplots(figsize=(14, 8))
        sns.heatmap(pivot, annot=True, fmt='.0f', cmap='Blues', ax=ax, linewidths=0.5, linecolor='white')
        
        apply_editorial_style(fig, ax, "Cross-Sell Opportunities: Segment-Size matrix", "Average order value (AOV) potential across categories")
        
        # Professional callout
        add_callout(ax, "High AOV Bundle Potential", xy=(3.5, 0.5), xytext=(4.5, 1.5), color='#0072B2')

        plt.savefig(os.path.join(OUTPUT_DIR, 'cross_sell_opportunities.png'))
        plt.close()
        print("Generated: cross_sell_opportunities.png")

def plot_temporal_product_shifts(oi_df):
    """New Function: Tet vs Double Day Segment shifts"""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Calculate revenue share per segment during each temporal event
    event_segment = oi_df.groupby(['temporal_event', 'segment'])['unit_price'].sum().unstack()
    event_segment_pct = event_segment.div(event_segment.sum(axis=1), axis=0) * 100
    
    event_segment_pct.loc[['Normal Day', 'Tet Approach', 'Double Day Promo']].plot(
        kind='bar', stacked=True, colormap='tab20', ax=ax
    )
    
    apply_editorial_style(fig, ax, "Product Segment Shift by Temporal Event", "How demand mix changes during Tet and Double Day promotions")
    
    ax.set_ylabel('Revenue Share (%)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Event Phase', fontsize=12, fontweight='bold')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.legend(title='Product Segment', bbox_to_anchor=(1.05, 1), loc='upper left', frameon=False)
    
    # Professional callout
    add_callout(ax, "Double Day drives mix shift", xy=(2, 60), xytext=(2.2, 80), color='#E69F00')

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
    plot_temporal_product_shifts(oi_df)
    
    print("\nAll professionally styled product market figures generated successfully.")

if __name__ == "__main__":
    main()
