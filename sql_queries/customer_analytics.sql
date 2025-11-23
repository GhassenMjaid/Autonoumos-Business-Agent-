-- ============================================================
-- CUSTOMER ANALYTICS QUERIES
-- Brazilian E-Commerce Dataset
-- ============================================================

-- Query 1: Top Customers by Revenue
-- Business Question: "Who are my most valuable customers?"
-- Use Case: Identify VIP customers for retention programs
-- ============================================================

SELECT 
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT oi.product_id) as unique_products_purchased,
    ROUND(SUM(oi.price + oi.freight_value), 2) as total_revenue,
    ROUND(AVG(oi.price + oi.freight_value), 2) as avg_order_value,
    MIN(o.order_purchase_timestamp) as first_order_date,
    MAX(o.order_purchase_timestamp) as last_order_date,
    ROUND(
        JULIANDAY(MAX(o.order_purchase_timestamp)) - 
        JULIANDAY(MIN(o.order_purchase_timestamp))
    ) as customer_lifetime_days
FROM olist_customers_dataset c
JOIN olist_orders_dataset o ON c.customer_id = o.customer_id
JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_unique_id, c.customer_city, c.customer_state
HAVING total_orders >= 2  -- Only repeat customers
ORDER BY total_revenue DESC
LIMIT 50;


-- ============================================================
-- Query 2: Customer Churn Risk Analysis
-- Business Question: "Which customers are at risk of leaving?"
-- Use Case: Proactive retention campaigns
-- ============================================================

SELECT 
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    COUNT(DISTINCT o.order_id) as total_orders,
    ROUND(SUM(oi.price + oi.freight_value), 2) as total_revenue,
    MAX(o.order_purchase_timestamp) as last_order_date,
    ROUND(JULIANDAY('now') - JULIANDAY(MAX(o.order_purchase_timestamp))) as days_since_last_order,
    CASE 
        WHEN JULIANDAY('now') - JULIANDAY(MAX(o.order_purchase_timestamp)) > 180 THEN 'High Risk'
        WHEN JULIANDAY('now') - JULIANDAY(MAX(o.order_purchase_timestamp)) > 90 THEN 'Medium Risk'
        WHEN JULIANDAY('now') - JULIANDAY(MAX(o.order_purchase_timestamp)) > 60 THEN 'Low Risk'
        ELSE 'Active'
    END as churn_risk_level
FROM olist_customers_dataset c
JOIN olist_orders_dataset o ON c.customer_id = o.customer_id
JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_unique_id, c.customer_city, c.customer_state
HAVING total_orders >= 2  -- Focus on repeat customers
    AND days_since_last_order > 60  -- Haven't ordered in 60+ days
ORDER BY total_revenue DESC, days_since_last_order DESC
LIMIT 100;


-- ============================================================
-- Query 3: Customer Geographic Distribution
-- Business Question: "Where are my customers located?"
-- Use Case: Target marketing, logistics optimization
-- ============================================================

SELECT 
    customer_state,
    customer_city,
    COUNT(DISTINCT c.customer_unique_id) as unique_customers,
    COUNT(DISTINCT o.order_id) as total_orders,
    ROUND(SUM(oi.price + oi.freight_value), 2) as total_revenue,
    ROUND(AVG(oi.price + oi.freight_value), 2) as avg_order_value,
    ROUND(
        100.0 * COUNT(DISTINCT c.customer_unique_id) / 
        (SELECT COUNT(DISTINCT customer_unique_id) FROM olist_customers_dataset), 
        2
    ) as pct_of_customer_base
FROM olist_customers_dataset c
JOIN olist_orders_dataset o ON c.customer_id = o.customer_id
JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY customer_state, customer_city
HAVING unique_customers >= 10  -- Only cities with 10+ customers
ORDER BY total_revenue DESC
LIMIT 30;