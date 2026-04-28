import pandas as pd
import numpy as np
import os

INPUT_DIR = '/home/shayneeo/Downloads/Datathon/input'

def calculate_stats():
    print("Loading data for Forensic Summary...")
    products = pd.read_csv(os.path.join(INPUT_DIR, 'products.csv'))
    orders = pd.read_csv(os.path.join(INPUT_DIR, 'orders.csv'), parse_dates=['order_date'])
    order_items = pd.read_csv(os.path.join(INPUT_DIR, 'order_items.csv'))
    payments = pd.read_csv(os.path.join(INPUT_DIR, 'payments.csv'))
    returns = pd.read_csv(os.path.join(INPUT_DIR, 'returns.csv'))
    inventory = pd.read_csv(os.path.join(INPUT_DIR, 'inventory.csv'))
    
    # 1. Total Revenue & Margin
    oi = order_items.merge(products[['product_id', 'price', 'cogs']], on='product_id', how='left')
    oi['revenue'] = oi['unit_price'] * oi['quantity']
    oi['profit'] = (oi['unit_price'] - oi['cogs']) * oi['quantity']
    
    total_rev = oi['revenue'].sum()
    total_profit = oi['profit'].sum()
    avg_margin = (total_profit / total_rev) * 100
    
    # 2. Sizing Crisis
    size_returns = returns.merge(products[['product_id', 'size']], on='product_id')
    return_reasons = returns['return_reason'].value_counts(normalize=True) * 100
    wrong_size_pct = return_reasons.get('wrong_size', 0)
    
    # 3. Loyalty Paradox (Simplified Cohort)
    orders['year'] = orders['order_date'].dt.year
    first_orders = orders.groupby('customer_id')['year'].min().reset_index()
    first_orders.columns = ['customer_id', 'cohort_year']
    
    orders_with_cohort = orders.merge(first_orders, on='customer_id')
    retention_2012 = orders_with_cohort[orders_with_cohort['cohort_year'] == 2012]['customer_id'].nunique()
    repeat_2012 = orders_with_cohort[(orders_with_cohort['cohort_year'] == 2012) & (orders_with_cohort['year'] > 2012)]['customer_id'].nunique()
    
    retention_2021 = orders_with_cohort[orders_with_cohort['cohort_year'] == 2021]['customer_id'].nunique()
    repeat_2021 = orders_with_cohort[(orders_with_cohort['cohort_year'] == 2021) & (orders_with_cohort['year'] > 2021)]['customer_id'].nunique()
    
    # 4. Financial Lever (Installments)
    pay_inst = payments.groupby('installments')['payment_value'].mean()
    aov_1 = pay_inst.get(1, 0)
    aov_12 = pay_inst.get(12, 0)
    installment_lift = ((aov_12 - aov_1) / aov_1) * 100 if aov_1 > 0 else 0
    
    # 5. Inventory Risk
    total_stockout_days = inventory['stockout_days'].sum()
    avg_fill_rate = inventory['fill_rate'].mean() * 100
    
    print("\n--- FORENSIC GROUND TRUTH ---")
    print(f"Total Revenue: {total_rev/1e9:.2f}B VND")
    print(f"Blended Gross Margin: {avg_margin:.1f}%")
    print(f"Wrong Size Return Rate: {wrong_size_pct:.1f}%")
    print(f"Cohort Retention (2012): {(repeat_2012/retention_2012)*100:.1f}%")
    print(f"Cohort Retention (2021): {(repeat_2021/retention_2021)*100:.1f}%")
    print(f"Installment AOV Lift (12m vs 1m): {installment_lift:.1f}%")
    print(f"Average Inventory Fill Rate: {avg_fill_rate:.1f}%")
    
if __name__ == "__main__":
    calculate_stats()
