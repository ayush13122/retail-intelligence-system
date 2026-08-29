-- Dimensional & Fact Tables
CREATE TABLE dim_customers (
    customer_id NUMBER PRIMARY KEY,
    country VARCHAR2(100) DEFAULT 'United Kingdom',
    created_at DATE DEFAULT SYSDATE
);

CREATE TABLE dim_products (
    stock_code VARCHAR2(50) PRIMARY KEY,
    description VARCHAR2(255),
    unit_price NUMBER(10, 2) CHECK (unit_price >= 0)
);

CREATE TABLE fact_transactions (
    invoice_no VARCHAR2(50),
    stock_code VARCHAR2(50),
    customer_id NUMBER,
    quantity NUMBER CHECK (quantity > 0),
    invoice_date DATE,
    unit_price NUMBER(10, 2),
    total_amount NUMBER(12, 2),
    CONSTRAINT fk_fact_cust FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
    CONSTRAINT fk_fact_prod FOREIGN KEY (stock_code) REFERENCES dim_products(stock_code)
);

-- Trigger: Auto calculate total_amount before insert
CREATE OR REPLACE TRIGGER trg_calc_transaction_total
BEFORE INSERT ON fact_transactions
FOR EACH ROW
BEGIN
    :NEW.total_amount := :NEW.quantity * :NEW.unit_price;
END;
/

-- Function: Customer Lifetime Value (CLV)
CREATE OR REPLACE FUNCTION fn_customer_clv (p_cust_id IN NUMBER)
RETURN NUMBER
IS
    v_total NUMBER(12, 2) := 0;
BEGIN
    SELECT NVL(SUM(total_amount), 0)
    INTO v_total
    FROM fact_transactions
    WHERE customer_id = p_cust_id;
    RETURN v_total;
END;
/

-- Procedure with Cursor: Compute RFM Summary Metrics
CREATE OR REPLACE PROCEDURE sp_compute_rfm_summary
IS
    CURSOR cur_rfm IS
        SELECT 
            customer_id,
            TRUNC(MAX(invoice_date)) AS last_purchase,
            COUNT(DISTINCT invoice_no) AS freq,
            SUM(total_amount) AS monetary
        FROM fact_transactions
        GROUP BY customer_id;
    v_rec cur_rfm%ROWTYPE;
BEGIN
    OPEN cur_rfm;
    LOOP
        FETCH cur_rfm INTO v_rec;
        EXIT WHEN cur_rfm%NOTFOUND;
        DBMS_OUTPUT.PUT_LINE('Customer ' || v_rec.customer_id || 
                             ' | Frequency: ' || v_rec.freq || 
                             ' | Monetary: ' || v_rec.monetary);
    END LOOP;
    CLOSE cur_rfm;
END;
/