-- ============================================================
-- PRODUCT ANALYTICS QUERIES
-- Brazilian E-Commerce Dataset
-- ============================================================

-- ============================================================
-- Query 1: Best-Selling Products
-- Business Question: "What are our top-performing products?"
-- Use Case: Inventory management, supplier negotiation
-- ============================================================

SELECT 
    oi.product_id,
    COALESCE(p.product_category_name, 'Unknown') as category,
    COUNT(DISTINCT oi.order_id) as times_ordered,
    COUNT(*) as total_units_sold,
    ROUND(SUM(oi.price), 2) as total_revenue,
    ROUND(AVG(oi.price), 2) as avg_unit_price,
    ROUND(SUM(oi.freight_value), 2) as total_shipping_costs,
    COUNT(DISTINCT CASE WHEN r.review_score >= 4 THEN r.review_id END) as positive_reviews,
    COUNT(DISTINCT r.review_id) as total_reviews,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN r.review_score >= 4 THEN r.review_id END) /
        NULLIF(COUNT(DISTINCT r.review_id), 0),
        2
    ) as positive_review_rate
FROM olist_order_items_dataset oi
JOIN olist_orders_dataset o ON oi.order_id = o.order_id
LEFT JOIN olist_products_dataset p ON oi.product_id = p.product_id
LEFT JOIN olist_order_reviews_dataset r ON oi.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY oi.product_id, p.product_category_name
HAVING times_ordered >= 5
ORDER BY total_revenue DESC
LIMIT 50;


-- ============================================================
-- Query 2: Product Category Performance Matrix
-- Business Question: "How do different categories perform?"
-- Use Case: Category management, merchandising strategy
-- ============================================================

SELECT 
    COALESCE(p.product_category_name, 'Unknown') as category,
    COUNT(DISTINCT oi.product_id) as unique_products,
    COUNT(DISTINCT oi.order_id) as total_orders,
    ROUND(SUM(oi.price), 2) as revenue,
    ROUND(AVG(oi.price), 2) as avg_price,
    ROUND(SUM(oi.freight_value), 2) as shipping_costs,
    ROUND(AVG(r.review_score), 2) as avg_review_score,
    COUNT(DISTINCT r.review_id) as review_count,
    ROUND(
        AVG(JULIANDAY(o.order_delivered_customer_date) - 
            JULIANDAY(o.order_purchase_timestamp)),
        1
    ) as avg_delivery_days,
    CASE 
        WHEN AVG(oi.price) > 100 AND AVG(r.review_score) >= 4 THEN 'Premium'
        WHEN AVG(oi.price) > 100 AND AVG(r.review_score) < 4 THEN 'High Price, Low Satisfaction'
        WHEN AVG(oi.price) <= 100 AND AVG(r.review_score) >= 4 THEN 'Value'
        WHEN AVG(oi.price) <= 100 AND AVG(r.review_score) < 4 THEN 'Low Performance'
        ELSE 'Unrated'
    END as category_segment
FROM olist_order_items_dataset oi
JOIN olist_orders_dataset o ON oi.order_id = o.order_id
LEFT JOIN olist_products_dataset p ON oi.product_id = p.product_id
LEFT JOIN olist_order_reviews_dataset r ON oi.order_id = r.order_id
WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
GROUP BY p.product_category_name
HAVING total_orders >= 10
ORDER BY revenue DESC;