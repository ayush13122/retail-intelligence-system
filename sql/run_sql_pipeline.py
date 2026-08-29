import sqlite3
import pandas as pd
import os

print("="*75)
print("   ORACLE SQL & PL/SQL PIPELINE EXECUTION ENGINE")
print("="*75)

# Purani locked file ka conflict hatane ke liye in-memory ya fresh file use karein
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

print("\n[STEP 1] Creating Relational Schema (Fact & Dimension Tables)...")

# DDL: Dimension Customers
cursor.execute('''
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id INTEGER PRIMARY KEY,
    country TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

# DDL: Dimension Products
cursor.execute('''
CREATE TABLE IF NOT EXISTS dim_products (
    stock_code TEXT PRIMARY KEY,
    description TEXT,
    unit_price REAL CHECK (unit_price >= 0)
);
''')

# DDL: Fact Transactions
cursor.execute('''
CREATE TABLE IF NOT EXISTS fact_transactions (
    invoice_no TEXT,
    stock_code TEXT,
    customer_id INTEGER,
    quantity INTEGER,
    invoice_date TEXT,
    unit_price REAL,
    total_amount REAL,
    FOREIGN KEY(customer_id) REFERENCES dim_customers(customer_id),
    FOREIGN KEY(stock_code) REFERENCES dim_products(stock_code)
);
''')
print(" -> Tables Created: dim_customers, dim_products, fact_transactions [OK]")

# 2. TRIGGER IMPLEMENTATION
print("\n[STEP 2] Creating Automated Trigger: trg_calc_transaction_total...")
cursor.execute('''
CREATE TRIGGER IF NOT EXISTS trg_calc_transaction_total
AFTER INSERT ON fact_transactions
FOR EACH ROW
BEGIN
    UPDATE fact_transactions 
    SET total_amount = NEW.quantity * NEW.unit_price
    WHERE rowid = NEW.rowid;
END;
''')
print(" -> Trigger 'trg_calc_transaction_total' compiled successfully. [OK]")

# 3. POPULATE SAMPLE DATA
print("\n[STEP 3] Populating Master & Transactional Tuples...")

customers_data = [
    (12345, 'United Kingdom'),
    (12346, 'Germany'),
    (12347, 'France'),
    (12348, 'EIRE'),
    (12349, 'United Kingdom')
]
cursor.executemany('INSERT OR IGNORE INTO dim_customers (customer_id, country) VALUES (?, ?)', customers_data)

products_data = [
    ('85123A', 'WHITE HANGING HEART T-LIGHT HOLDER', 2.55),
    ('71053', 'WHITE METAL LANTERN', 3.39),
    ('84406B', 'CREAM CUPID HEARTS COAT HANGER', 2.75),
    ('84029G', 'KNITTED UNION FLAG HOT WATER BOTTLE', 3.39),
    ('22752', 'SET 7 BABUSHKA NESTING BOXES', 7.65)
]
cursor.executemany('INSERT OR IGNORE INTO dim_products (stock_code, description, unit_price) VALUES (?, ?, ?)', products_data)

transactions_data = [
    ('536365', '85123A', 12345, 6, '2025-01-10 10:00:00', 2.55, 0),
    ('536365', '71053', 12345, 2, '2025-01-10 10:00:00', 3.39, 0),
    ('536366', '84406B', 12346, 8, '2025-01-11 11:30:00', 2.75, 0),
    ('536367', '22752', 12347, 4, '2025-01-12 14:15:00', 7.65, 0),
    ('536368', '84029G', 12348, 10, '2025-01-15 09:20:00', 3.39, 0),
    ('536369', '85123A', 12349, 12, '2025-01-18 16:45:00', 2.55, 0)
]
cursor.executemany('INSERT INTO fact_transactions VALUES (?, ?, ?, ?, ?, ?, ?)', transactions_data)
conn.commit()
print(" -> Data loaded & Trigger executed auto-computation. [OK]")

# 4. RUN ANALYTICAL SQL QUERIES
print("\n" + "="*75)
print("       QUERY 1: FACT-DIMENSION INNER JOIN (Live Transaction View)")
print("="*75)
query1 = '''
SELECT 
    t.invoice_no,
    p.description AS product_name,
    c.country,
    t.quantity,
    t.unit_price,
    t.total_amount
FROM fact_transactions t
INNER JOIN dim_customers c ON t.customer_id = c.customer_id
INNER JOIN dim_products p ON t.stock_code = p.stock_code;
'''
df_q1 = pd.read_sql_query(query1, conn)
print(df_q1.to_string(index=False))

print("\n" + "="*75)
print("       QUERY 2: PL/SQL BATCH AGGREGATION (Customer Lifetime Value)")
print("="*75)
query2 = '''
SELECT 
    c.customer_id,
    c.country,
    COUNT(DISTINCT t.invoice_no) AS total_orders,
    SUM(t.quantity) AS total_units_bought,
    ROUND(SUM(t.total_amount), 2) AS customer_lifetime_value
FROM dim_customers c
LEFT JOIN fact_transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id, c.country
ORDER BY customer_lifetime_value DESC;
'''
df_q2 = pd.read_sql_query(query2, conn)
print(df_q2.to_string(index=False))

print("\n" + "="*75)
print("       QUERY 3: SUBQUERY ANALYTICS (Above Average Spend Transactions)")
print("="*75)
query3 = '''
SELECT 
    invoice_no, 
    customer_id, 
    stock_code, 
    total_amount 
FROM fact_transactions 
WHERE total_amount > (SELECT AVG(total_amount) FROM fact_transactions);
'''
df_q3 = pd.read_sql_query(query3, conn)
print(df_q3.to_string(index=False))

print("\n" + "="*75)
print(" [SUCCESS] SQL & PL/SQL Database Execution Completed Successfully!")
print("="*75)
conn.close()