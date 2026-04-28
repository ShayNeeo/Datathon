import pandas as pd
import os

# Set paths
INPUT_DIR = '/home/shayneeo/Downloads/Datathon/input'

def explore():
    print("Loading data...")
    customers = pd.read_csv(os.path.join(INPUT_DIR, 'customers.csv'), parse_dates=['signup_date'])
    orders = pd.read_csv(os.path.join(INPUT_DIR, 'orders.csv'), parse_dates=['order_date'])
    payments = pd.read_csv(os.path.join(INPUT_DIR, 'payments.csv'))

    print(f"Customers: {len(customers)}")
    print(f"Orders: {len(orders)}")
    print(f"Payments: {len(payments)}")

    # 1. Monthly Signups
    customers['signup_month'] = customers['signup_date'].dt.to_period('M')
    monthly_signups = customers.groupby('signup_month').size()
    print("\n--- Monthly Signups (First 5) ---")
    print(monthly_signups.head())

    # 2. LTV Calculation
    # Join orders and payments to get customer_id and payment_value
    customer_payments = orders.merge(payments, on='order_id')
    customer_ltv = customer_payments.groupby('customer_id')['payment_value'].sum().reset_index()
    customer_ltv.columns = ['customer_id', 'ltv']

    # 3. Join LTV with Customer info
    customer_info_ltv = customers.merge(customer_ltv, on='customer_id', how='left').fillna(0)

    # 4. LTV by Acquisition Channel
    ltv_by_channel = customer_info_ltv.groupby('acquisition_channel')['ltv'].mean().sort_values(ascending=False)
    print("\n--- Avg LTV by Channel ---")
    print(ltv_by_channel)

    # 5. Repeat Purchase Rate by Channel
    # Count orders per customer
    order_counts = orders.groupby('customer_id').size().reset_index(name='order_count')
    customer_repeat = customers.merge(order_counts, on='customer_id', how='left').fillna(0)
    customer_repeat['is_repeat'] = customer_repeat['order_count'] > 1

    repeat_rate_by_channel = customer_repeat.groupby('acquisition_channel')['is_repeat'].mean().sort_values(ascending=False)
    print("\n--- Repeat Purchase Rate by Channel ---")
    print(repeat_rate_by_channel)

    # 6. LTV by Age Group and Gender
    ltv_demographics = customer_info_ltv.groupby(['age_group', 'gender'])['ltv'].mean().unstack()
    print("\n--- Avg LTV by Age Group and Gender ---")
    print(ltv_demographics)

    # 7. Order Frequency Distribution
    print("\n--- Order Count Distribution ---")
    print(order_counts['order_count'].value_counts().sort_index())

if __name__ == "__main__":
    explore()
