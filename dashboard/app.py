import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import os

st.set_page_config(page_title="Retail Intelligence Dashboard", layout="wide")

st.title("🛍️ Enterprise Retail Analytics & Customer Segmentation")
st.markdown("**Dual Stack:** Oracle PL/SQL Data Warehouse & K-Means Clustering Model")

# Data loading with fallback generator
paths_to_check = [
    'data/retail_clean.csv',
    '../data/retail_clean.csv',
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'retail_clean.csv')
]

df = None
rfm = None

for p in paths_to_check:
    if os.path.exists(p):
        df = pd.read_csv(p)
        seg_p = p.replace('retail_clean.csv', 'customer_segments.csv')
        if os.path.exists(seg_p):
            rfm = pd.read_csv(seg_p)
        break

# Auto-compute if not loaded from file
if df is None or rfm is None:
    np.random.seed(42)
    n_rows = 5000
    df = pd.DataFrame({
        'InvoiceNo': np.random.randint(536365, 540000, size=n_rows).astype(str),
        'Description': np.random.choice(['WHITE HANGING HEART T-LIGHT HOLDER', 'WHITE METAL LANTERN', 
                                         'CREAM CUPID HEARTS COAT HANGER', 'KNITTED UNION FLAG HOT WATER BOTTLE', 
                                         'SET 7 BABUSHKA NESTING BOXES'], size=n_rows),
        'Quantity': np.random.randint(1, 12, size=n_rows),
        'InvoiceDate': pd.date_range(start='2025-01-01', periods=n_rows, freq='10min'),
        'UnitPrice': np.random.choice([2.55, 3.39, 2.75, 7.65, 4.25], size=n_rows),
        'CustomerID': np.random.randint(12000, 18000, size=n_rows),
        'Country': np.random.choice(['United Kingdom', 'Germany', 'France', 'EIRE'], size=n_rows)
    })
    df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
    
    snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        'InvoiceNo': 'nunique',
        'TotalAmount': 'sum'
    }).reset_index()
    rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
    
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm[['Recency', 'Frequency', 'Monetary']])
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)
    
    summary = rfm.groupby('Cluster')['Monetary'].mean().sort_values()
    cluster_map = {
        summary.index[0]: 'Low Value / Hibernating',
        summary.index[1]: 'Mid-Tier / Potential Loyal',
        summary.index[2]: 'High Value / Champions'
    }
    rfm['Segment'] = rfm['Cluster'].map(cluster_map)

# 1. Top KPI Metrics
st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Total Revenue", f"${df['TotalAmount'].sum():,.2f}")
c2.metric("🧾 Total Orders", f"{df['InvoiceNo'].nunique():,}")
c3.metric("👥 Active Customers", f"{rfm['CustomerID'].nunique():,}")
c4.metric("📊 Avg Order Value", f"${df['TotalAmount'].mean():,.2f}")
st.markdown("---")

# 2. Visual Analytics Row
col1, col2 = st.columns(2)
with col1:
    st.subheader("📦 Top 5 Products by Revenue")
    prod_rev = df.groupby('Description')['TotalAmount'].sum().sort_values(ascending=True).tail(5)
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.barh(prod_rev.index, prod_rev.values, color='#1f77b4')
    ax1.set_xlabel("Revenue ($)")
    st.pyplot(fig1)

with col2:
    st.subheader("🎯 Customer Clusters (K-Means)")
    seg_counts = rfm['Segment'].value_counts()
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.pie(seg_counts.values, labels=seg_counts.index, autopct='%1.1f%%', 
            colors=['#2ca02c', '#ff7f0e', '#d62728'], startangle=140)
    st.pyplot(fig2)

# 3. RFM Behavioral Space Plot
st.subheader("🔬 RFM Behavioral Clustering Space (Recency vs Monetary)")
fig3, ax3 = plt.subplots(figsize=(10, 4))
for seg, color in zip(['Low Value / Hibernating', 'Mid-Tier / Potential Loyal', 'High Value / Champions'], ['#2ca02c', '#ff7f0e', '#d62728']):
    sub = rfm[rfm['Segment'] == seg]
    ax3.scatter(sub['Recency'], sub['Monetary'], label=seg, alpha=0.6, color=color)
ax3.set_xlabel("Recency (Days)")
ax3.set_ylabel("Monetary ($)")
ax3.legend()
st.pyplot(fig3)