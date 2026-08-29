# retail-intelligence-system

# Enterprise Retail Intelligence & Customer Segmentation System

An end-to-end enterprise data engineering, relational warehousing, and unsupervised machine learning platform designed to ingest raw e-commerce transaction logs, automate database calculations via procedural triggers, perform multi-dimensional RFM (Recency, Frequency, Monetary) feature engineering, and segment customer cohorts for targeted retail marketing automation.

---

## 📋 Project Overview

Modern retail platforms accumulate high-volume transaction datasets containing missing attributes, returns, and noise. This system bridges the gap between relational data warehousing and machine learning analytics by providing:
1. **Relational Warehousing & Integrity:** Star Schema architecture (`dim_customers`, `dim_products`, `fact_transactions`) backed by automated row-level calculation triggers.
2. **Behavioral Feature Engineering:** Automated transformation of raw transaction dates, invoice IDs, and monetary values into standardized 3D RFM vector spaces.
3. **Unsupervised Machine Learning:** StandardScaler Z-score normalization and K-Means clustering ($K=3$) validated through geometric Silhouette scoring coefficients.
4. **Multi-Platform Interfaces:** Interactive Streamlit web analytics dashboard and a native Tkinter desktop graphical user interface.

---

## 🛠️ Tech Stack & Dependencies

* **Programming Language:** Python 3.10+ (64-bit)
* **Database Engine:** SQLite Relational Database Engine (ANSI / Oracle SQL standard DDL/DML)
* **Data Processing & Analytics:** Pandas, NumPy
* **Machine Learning:** Scikit-Learn (`KMeans`, `StandardScaler`, `silhouette_score`)
* **Visualization & GUI:** Matplotlib, Streamlit, Tkinter
* **Development Environment:** Visual Studio Code, Git Version Control

---

## 📂 Project Directory Structure


retail_analytics/
│
├── dashboard/               # Interactive frontend presentation layers
│   ├── app.py               # Streamlit browser-based web dashboard
│   └── app_gui.py           # Tkinter native desktop GUI interface
│
├── data/                    # Persistent storage and pipeline artifacts
│   ├── Online Retail.xlsx   # Raw enterprise transactional dataset
│   ├── retail_clean.csv     # Sanitized transaction dataset
│   └── customer_segments.csv# Final RFM clustering and segment outputs
│
├── outputs/                 # Exported visual analytics charts and figures
│   └── dashboard_analytics.png
│
├── python/                  # Core logic and ML execution scripts
│   └── 02_etl_rfm_ml.py     # ETL, Z-score scaling, and K-Means training pipeline
│
├── Report AND PPT/          # Final academic project documentation
│   ├── Ayush_Raj_CSE343_CSE443_Report.docx
│   └── Ayush_Raj_CSE343_CSE443_Presentation.pptx
│
├── run_project/             # Master automation runner scripts
│   └── run_project.py       # Headless batch processing and terminal KPI logger
│
├── sql/                     # Relational database architecture
│   └── run_sql_pipeline.py  # DDL Star Schema and PL/SQL trigger execution
│
└── README.md                # Project documentation

⚙️ Core Architecture & Pipeline WorkflowData Ingestion & Sanitization: Raw transactional logs (Online Retail.xlsx) are cleaned by dropping missing customer identifiers and negative/zero order returns.
Database Warehousing & Triggers: Cleaned records are inserted into normalized SQL tables. An AFTER INSERT trigger (trg_calc_transaction_total) dynamically computes total line revenue ($\text{Quantity} \times \text{UnitPrice}$) at the database layer.

RFM Feature Formulation: Customer behavioral vectors are computed using a snapshot date ($T_{\text{max}} + 1\text{ day}$):Recency ($R$): Days since customer's last purchase.Frequency ($F$): Total count of distinct invoices.Monetary ($M$): Cumulative gross spend across all orders.

Machine Learning Clustering: Features are normalized using StandardScaler ($z = \frac{x - \mu}{\sigma}$) and clustered using Unsupervised K-Means ($K=3$), achieving a verified Silhouette Score of 0.3789.📊 Enterprise Business Metrics SummaryTotal Gross Revenue: $\$121,314.76$Total Invoices Handled: $2,733\text{ Orders}$Unique Customers Profiled: $3,330\text{ Active Customers}$Average Order Value (AOV): $\$24.26$Customer Cohort Distribution:Mid-Tier / Potential Loyal ($1,412$ customers | $42.4\%$): Moderate frequency and regular repeat intervals; prime candidates for cross-selling.Low Value / Hibernating ($1,277$ customers | $38.3\%$): High recency days and single-order history; targets for email re-engagement discounts.
High Value / Champions ($641$ customers | $19.3\%$): Highest spenders and frequent buyers; eligible for exclusive VIP loyalty perks.🚀 Installation & Execution GuideClone the Repository:DOSgit clone [https://github.com/ayush13122/retail-intelligence-system.git](https://github.com/ayush13122/retail-intelligence-system.git)

cd retail_analytics
Install Required Dependencies:DOSpy -m pip install pandas numpy scikit-learn matplotlib streamlit openpyxl python-docx python-pptx
Run Master Batch Pipeline:DOSpy run_project/run_project.py
Launch Streamlit Web Dashboard:DOSstreamlit run dashboard/app.py
Launch Desktop GUI Interface:DOSpy dashboard/app_gui.py
✒️ Author & Academic DetailsAuthor: Ayush Raj
Registration Number: 12315673
Course Code: CSE343 / CSE443 (Summer Training / Internship Project)
Department: School of Computer Science and Engineering
Institution: Lovely Professional University, Phagwara, Punjab
