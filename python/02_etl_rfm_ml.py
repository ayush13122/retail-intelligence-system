import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

os.makedirs('data', exist_ok=True)

# Generate Synthetic Retail Transactions matching Online Retail Data
np.random.seed(42)
n_rows = 5000

customers = np.random.randint(12000, 18000, size=n_rows)
stock_codes = ['85123A', '71053', '84406B', '84029G', '22752', '21730']
descriptions = ['WHITE HANGING HEART T-LIGHT HOLDER', 'WHITE METAL LANTERN', 
                'CREAM CUPID HEARTS COAT HANGER', 'KNITTED UNION FLAG HOT WATER BOTTLE', 
                'SET 7 BABUSHKA NESTING BOXES', 'GLASS STAR FROSTED T-LIGHT HOLDER']
quantities = np.random.randint(1, 12, size=n_rows)
unit_prices = np.random.choice([2.55, 3.39, 2.75, 3.39, 7.65, 4.25], size=n_rows)
dates = pd.date_range(start='2025-01-01', periods=n_rows, freq='10min')

df = pd.DataFrame({
    'InvoiceNo': np.random.randint(536365, 540000, size=n_rows).astype(str),
    'StockCode': np.random.choice(stock_codes, size=n_rows),
    'Description': np.random.choice(descriptions, size=n_rows),
    'Quantity': quantities,
    'InvoiceDate': dates,
    'UnitPrice': unit_prices,
    'CustomerID': customers,
    'Country': np.random.choice(['United Kingdom', 'Germany', 'France', 'EIRE'], size=n_rows)
})
df['TotalAmount'] = df['Quantity'] * df['UnitPrice']

# Save Raw Transaction Data
df.to_csv('data/retail_clean.csv', index=False)
print("[ETL] Data saved to data/retail_clean.csv")

# RFM Analysis
snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
rfm = df.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
    'InvoiceNo': 'nunique',
    'TotalAmount': 'sum'
}).reset_index()

rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

# Standard Scaling
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm[['Recency', 'Frequency', 'Monetary']])

# K-Means Clustering (k=3)
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)

# Business Labeling
summary = rfm.groupby('Cluster')['Monetary'].mean().sort_values()
cluster_map = {
    summary.index[0]: 'Low Value / Hibernating',
    summary.index[1]: 'Mid-Tier / Potential Loyal',
    summary.index[2]: 'High Value / Champions'
}
rfm['Segment'] = rfm['Cluster'].map(cluster_map)

# Silhouette Score Evaluation
sil_score = silhouette_score(rfm_scaled, rfm['Cluster'])
print(f"[ML Model] K-Means Silhouette Score: {sil_score:.4f}")

rfm.to_csv('data/customer_segments.csv', index=False)
print("[ML Model] Customer segments saved to data/customer_segments.csv")