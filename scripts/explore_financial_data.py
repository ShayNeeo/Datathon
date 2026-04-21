import pandas as pd
import os

INPUT_DIR = '/home/shayneeo/Downloads/Datathon/input'

def explore():
    print("Loading data...")
    orders = pd.read_csv(os.path.join(INPUT_DIR, 'orders.csv'), parse_dates=['order_date'])
    order_items = pd.read_csv(os.path.join(INPUT_DIR, 'order_items.csv'), low_memory=False)
    payments = pd.read_csv(os.path.join(INPUT_DIR, 'payments.csv'))
    promotions = pd.read_csv(os.path.join(INPUT_DIR, 'promotions.csv'), parse_dates=['start_date', 'end_date'])
    products = pd.read_csv(os.path.join(INPUT_DIR, 'products.csv'))

    # Merge order items with orders and products
    oi = order_items.merge(orders[['order_id', 'order_date', 'order_status']], on='order_id', how='left')
    oi = oi.merge(products[['product_id', 'category', 'segment']], on='product_id', how='left')

    # Completed orders only
    oi_completed = oi[oi['order_status'] == 'delivered']

    # 1. Monthly Revenue Trend (verify existing)
    oi_completed['month'] = oi_completed['order_date'].dt.to_period('M')
    monthly_revenue = oi_completed.groupby('month')['unit_price'].sum()
    print("\n--- Monthly Revenue (First 3) ---")
    print(monthly_revenue.head(3))

    # 2. AOV by Payment Method
    orders_with_payments = orders.merge(payments, on='order_id')
    aov_by_payment = orders_with_payments.groupby('payment_method_y')['payment_value'].mean().sort_values(ascending=False)
    print("\n--- AOV by Payment Method ---")
    print(aov_by_payment)

    # 3. Installment usage rate
    installment_orders = orders_with_payments[orders_with_payments['installments'] > 1]
    print(f"\n--- Installment Usage ---")
    print(f"Orders with installments: {len(installment_orders)}")
    print(f"Total orders: {len(orders_with_payments)}")
    print(f"Installment rate: {len(installment_orders)/len(orders_with_payments)*100:.2f}%")

    # 4. Promotions: frequency and average discount
    promo_counts = promotions['promo_type'].value_counts()
    print("\n--- Promo Types ---")
    print(promo_counts)

    # 5. Revenue contribution by product category
    category_revenue = oi_completed.groupby('category')['unit_price'].sum().sort_values(ascending=False)
    print("\n--- Revenue by Category (Top 5) ---")
    print(category_revenue.head())

    # 6. Average discount amount by promo type
    order_items_with_promo = order_items.merge(promotions[['promo_id', 'promo_type']], left_on='promo_id', right_on='promo_id', how='left')
    avg_discount_by_type = order_items_with_promo.groupby('promo_type')['discount_amount'].mean()
    print("\n--- Avg Discount by Promo Type ---")
    print(avg_discount_by_type)

    # 7. Monthly average discount rate
    order_items_with_promo['discount_rate'] = order_items_with_promo['discount_amount'] / (order_items_with_promo['discount_amount'] + order_items_with_promo['unit_price'])
    oi_with_discount = order_items_with_promo[~order_items_with_promo['discount_rate'].isna()]
    oi_with_discount['month'] = oi_with_discount['order_id'].map(orders.set_index('order_id')['order_date']).dt.to_period('M')
    monthly_avg_discount = oi_with_discount.groupby('month')['discount_rate'].mean()
    print("\n--- Monthly Avg Discount Rate (First 3) ---")
    print(monthly_avg_discount.head(3))

    # 8. Bundle stacking behavior
    stacked_promos = order_items[(order_items['promo_id'].notna()) & (order_items['promo_id_2'].notna())]
    print(f"\n--- Promo Stacking ---")
    print(f"Orders with stacked promos: {len(stacked_promos)}")
    print(f"Unique orders with any promo: {order_items[order_items['promo_id'].notna()]['order_id'].nunique()}")
    print(f"Stacking rate: {len(stacked_promos)/order_items[order_items['promo_id'].notna()]['order_id'].nunique()*100:.2f}%")

if __name__ == "__main__":
    explore()
