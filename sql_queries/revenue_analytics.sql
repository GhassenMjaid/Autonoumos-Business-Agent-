-- ============================================================
-- REVENUE ANALYTICS QUERIES
-- Brazilian E-Commerce Dataset
-- ============================================================

-- ============================================================
-- Query 1: Monthly Revenue Trend
-- Business Question: "How is our revenue trending over time?"
-- Use Case: Identify seasonality, growth patterns, anomalies
-- ============================================================

SELECT 
    strftime('%Y-%m', o.order_purchase_timestamp) as month,
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    ROUND(SUM(oi.price), 2) as product_revenue,
    ROUND(SUM(oi.freight_value), 2) as shipping_revenue,
    ROUND(SUM(oi.price + oi.freight_value), 2) as total_revenue,
    ROUND(AVG(oi.price + oi.freight_value), 2) as avg_order_value,
    ROUND(
        SUM(oi.price + oi.freight_value) / COUNT(DISTINCT o.customer_id),
        2
    ) as revenue_per_customer
FROM olist_orders_dataset o
JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
    AND o.order_purchase_timestamp IS NOT NULL
GROUP BY strftime('%Y-%m', o.order_purchase_timestamp)
ORDER BY month DESC
LIMIT 24;


-- Query 2: Revenue by Product Category
-- Business Question: "Which product categories drive the most revenue?"
-- Use Case: Inventory planning, marketing focus

SELECT 
    COALESCE(p.product_category_name, 'Unknown') as category,
    COUNT(DISTINCT oi.order_id) as orders,
    COUNT(*) as items_sold,
    ROUND(SUM(oi.price), 2) as product_revenue,
    ROUND(SUM(oi.freight_value), 2) as shipping_revenue,
    ROUND(SUM(oi.price + oi.freight_value), 2) as total_revenue,
    ROUND(AVG(oi.price), 2) as avg_product_price,
    ROUND(
        100.0 * SUM(oi.price + oi.freight_value) / 
        (SELECT SUM(price + freight_value) FROM olist_order_items_dataset oi2
         JOIN olist_orders_dataset o2 ON oi2.order_id = o2.order_id
         WHERE o2.order_status = 'delivered'),
        2
    ) as pct_of_total_revenue
FROM olist_order_items_dataset oi
JOIN olist_orders_dataset o ON oi.order_id = o.order_id
LEFT JOIN olist_products_dataset p ON oi.product_id = p.product_id
WHERE o.order_status = 'delivered'
GROUP BY p.product_category_name
HAVING total_revenue > 1000
ORDER BY total_revenue DESC
LIMIT 20;


-- ============================================================
-- Query 3: Revenue by State (Geographic Performance)
-- Business Question: "Which states generate the most revenue?"
-- Use Case: Regional marketing, expansion planning
-- ============================================================

SELECT 
    c.customer_state,
    COUNT(DISTINCT c.customer_unique_id) as customers,
    COUNT(DISTINCT o.order_id) as orders,
    ROUND(SUM(oi.price + oi.freight_value), 2) as total_revenue,
    ROUND(AVG(oi.price + oi.freight_value), 2) as avg_order_value,
    ROUND(
        SUM(oi.price + oi.freight_value) / COUNT(DISTINCT c.customer_unique_id),
        2
    ) as revenue_per_customer,
    ROUND(
        100.0 * SUM(oi.price + oi.freight_value) /
        (SELECT SUM(price + freight_value) FROM olist_order_items_dataset oi2
         JOIN olist_orders_dataset o2 ON oi2.order_id = o2.order_id
         WHERE o2.order_status = 'delivered'),
        2
    ) as pct_of_total_revenue
FROM olist_customers_dataset c
JOIN olist_orders_dataset o ON c.customer_id = o.customer_id
JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY total_revenue DESC;