import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

print("="*65)
print("  ENTERPRISE RETAIL INTELLIGENCE (REAL ONLINE RETAIL DATASET)")
print("="*65)

# 1. READ ORIGINAL DATASET
excel_path = 'data/Online Retail.xlsx'
csv_clean_path = 'data/retail_clean.csv'

if os.path.exists(excel_path):
    print(f"\n[STEP 1] Loading Original '{excel_path}'...")
    df = pd.read_excel(excel_path)
    
    # Clean data (Remove cancellations and missing CustomerIDs)
    df = df.dropna(subset=['CustomerID'])
    df = df[df['Quantity'] > 0]
    df = df[df['UnitPrice'] > 0]
    df['CustomerID'] = df['CustomerID'].astype(int)
    df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
    
    # Save cleaned CSV for downstream pipeline
    df.to_csv(csv_clean_path, index=False)
    print(f" -> Cleaned records: {len(df):,} transactions.")
else:
    print(f"\n[STEP 1] Loading pre-processed data from '{csv_clean_path}'...")
    df = pd.read_csv(csv_clean_path)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

# 2. RFM AGGREGATION & MACHINE LEARNING
print("\n[STEP 2] Computing RFM Metrics & Training K-Means Cluster Model...")
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
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

# K-Means Clustering
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)

# Segment Mapping
summary = rfm.groupby('Cluster')['Monetary'].mean().sort_values()
cluster_map = {
    summary.index[0]: 'Low Value / Hibernating',
    summary.index[1]: 'Mid-Tier / Potential Loyal',
    summary.index[2]: 'High Value / Champions'
}
rfm['Segment'] = rfm['Cluster'].map(cluster_map)
sil_score = silhouette_score(rfm_scaled, rfm['Cluster'])

os.makedirs('data', exist_ok=True)
os.makedirs('outputs', exist_ok=True)
rfm.to_csv('data/customer_segments.csv', index=False)

print(f" -> Model Evaluation Silhouette Score: {sil_score:.4f}")
print(f" -> Segment Summary:\n{rfm['Segment'].value_counts().to_string()}")

# 3. PRINT SYSTEM KPIs
print("\n" + "="*65)
print("                    BUSINESS METRICS SUMMARY")
print("="*65)
print(f" Total Revenue        : ${df['TotalAmount'].sum():,.2f}")
print(f" Total Invoices       : {df['InvoiceNo'].nunique():,}")
print(f" Unique Customers     : {rfm['CustomerID'].nunique():,}")
print(f" Average Order Value  : ${df['TotalAmount'].mean():,.2f}")
print("="*65)

# 4. VISUALIZATION POPUP
print("\n[STEP 3] Generating Visual Plots...")
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Enterprise Retail Intelligence & Customer Clusters', fontsize=14, fontweight='bold')

prod_rev = df.groupby('Description')['TotalAmount'].sum().sort_values(ascending=True).tail(5)
axes[0].barh(prod_rev.index, prod_rev.values, color='#1f77b4')
axes[0].set_title('Top 5 Products by Revenue', fontweight='bold')
axes[0].set_xlabel('Total Revenue ($)')

seg_counts = rfm['Segment'].value_counts()
axes[1].pie(seg_counts.values, labels=seg_counts.index, autopct='%1.1f%%', 
            colors=['#2ca02c', '#ff7f0e', '#d62728'], startangle=140)
axes[1].set_title('Customer Clusters (K-Means)', fontweight='bold')

for seg, color in zip(['Low Value / Hibernating', 'Mid-Tier / Potential Loyal', 'High Value / Champions'], ['#2ca02c', '#ff7f0e', '#d62728']):
    subset = rfm[rfm['Segment'] == seg]
    axes[2].scatter(subset['Recency'], subset['Monetary'], label=seg, alpha=0.6, color=color, edgecolors='none')
axes[2].set_title('RFM Space: Recency vs Monetary', fontweight='bold')
axes[2].set_xlabel('Recency (Days)')
axes[2].set_ylabel('Monetary Spend ($)')
axes[2].legend(fontsize=8)

plt.tight_layout()
plt.savefig('outputs/dashboard_analytics.png', dpi=300)
plt.show()