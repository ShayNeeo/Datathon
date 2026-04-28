import pandas as pd
import os

INPUT_DIR = '/home/shayneeo/Downloads/Datathon/input'

def explore():
    print("Loading data...")
    products = pd.read_csv(os.path.join(INPUT_DIR, 'products.csv'))
    order_items = pd.read_csv(os.path.join(INPUT_DIR, 'order_items.csv'))
    orders = pd.read_csv(os.path.join(INPUT_DIR, 'orders.csv'), parse_dates=['order_date'])
    reviews = pd.read_csv(os.path.join(INPUT_DIR, 'reviews.csv'), parse_dates=['review_date'])
    
    # Merge to get product revenue
    oi_merged = order_items.merge(orders[['order_id', 'order_date', 'order_status']], on='order_id', how='left')
    oi_delivered = oi_merged[oi_merged['order_status'] == 'delivered']
    oi_delivered = oi_delivered.merge(products, on='product_id', how='left')
    
    # 1. Category revenue contribution
    cat_revenue = oi_delivered.groupby('category')['unit_price'].sum().sort_values(ascending=False)
    print("\n--- Revenue by Category (Top 5) ---")
    print(cat_revenue.head())
    
    # 2. Segment revenue contribution
    seg_revenue = oi_delivered.groupby('segment')['unit_price'].sum().sort_values(ascending=False)
    print("\n--- Revenue by Segment (Top 5) ---")
    print(seg_revenue.head())
    
    # 3. Product-level revenue distribution (Pareto analysis)
    product_revenue = oi_delivered.groupby('product_id')['unit_price'].sum().sort_values(ascending=False)
    top20_count = int(len(product_revenue) * 0.2)
    top20_revenue = product_revenue.head(top20_count).sum()
    total_revenue = product_revenue.sum()
    print(f"\n--- Pareto Analysis ---")
    print(f"Total products: {len(product_revenue)}")
    print(f"Top 20% products ({top20_count}) revenue: {top20_revenue:,.0f}")
    print(f"Total revenue: {total_revenue:,.0f}")
    print(f"Top 20% contribution: {top20_revenue/total_revenue*100:.1f}%")
    
    # 4. Margin analysis by category
    oi_delivered['margin'] = oi_delivered['unit_price'] - oi_delivered['cogs']
    cat_margin = oi_delivered.groupby('category').agg({
        'margin': 'mean',
        'unit_price': 'count'
    }).rename(columns={'unit_price': 'count'})
    cat_margin = cat_margin.sort_values('margin', ascending=False)
    print("\n--- Average Margin by Category ---")
    print(cat_margin.head())
    
    # 5. Size revenue distribution
    size_revenue = oi_delivered.groupby('size')['unit_price'].sum().sort_values(ascending=False)
    print("\n--- Revenue by Size ---")
    print(size_revenue)
    
    # 6. Color popularity
    color_revenue = oi_delivered.groupby('color')['unit_price'].sum().sort_values(ascending=False)
    print("\n--- Revenue by Color (Top 5) ---")
    print(color_revenue.head())
    
    # 7. Monthly category trend (top categories)
    oi_delivered['month'] = oi_delivered['order_date'].dt.to_period('M')
    monthly_cat = oi_delivered.groupby(['month', 'category'])['unit_price'].sum().unstack()
    print("\n--- Monthly Revenue by Category (Latest 3 months) ---")
    print(monthly_cat.tail(3))
    
    # 8. Review ratings by category
    reviews_with_cat = reviews.merge(products[['product_id', 'category']], on='product_id', how='left')
    avg_rating_by_cat = reviews_with_cat.groupby('category')['rating'].mean().sort_values(ascending=False)
    print("\n--- Average Rating by Category ---")
    print(avg_rating_by_cat.head())
    
    # 9. Product price elasticity (avg discount vs volume correlation)
    product_agg = oi_delivered.groupby('product_id').agg({
        'unit_price': ['mean', 'sum'],
        'quantity': 'sum',
        'discount_amount': 'mean'
    }).reset_index()
    product_agg.columns = ['product_id', 'avg_price', 'total_revenue', 'total_units', 'avg_discount']
    product_agg['discount_rate'] = product_agg['avg_discount'] / product_agg['avg_price']
    print("\n--- Price Elasticity Analysis (Correlation) ---")
    correlation = product_agg['discount_rate'].corr(product_agg['total_units'])
    print(f"Correlation between discount rate and units sold: {correlation:.3f}")
    
    # 10. Product lifecycle - New vs Old products
    # Identify first appearance of each product
    first_appearance = oi_delivered.groupby('product_id')['order_date'].min()
    product_age_days = (oi_delivered['order_date'].max() - first_appearance).dt.days
    age_bins = pd.qcut(product_age_days, q=3, labels=['New', 'Mature', 'Old'])
    age_revenue = pd.DataFrame({
        'product_id': first_appearance.index,
        'age_group': age_bins,
        'first_seen': first_appearance
    }).merge(product_agg[['product_id', 'total_revenue']], on='product_id')
    revenue_by_age = age_revenue.groupby('age_group')['total_revenue'].sum()
    print("\n--- Revenue Contribution by Product Age ---")
    print(revenue_by_age)

if __name__ == "__main__":
    explore()