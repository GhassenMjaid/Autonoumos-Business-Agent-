-- ============================================================
-- OPERATIONAL ANALYTICS QUERIES
-- Brazilian E-Commerce Dataset
-- ============================================================

-- Query 1: Delivery Performance Analysis
-- Business Question: "How well are we delivering orders?"
-- Use Case: Logistics optimization, carrier evaluation
-- ============================================================

SELECT 
    strftime('%Y-%m', o.order_purchase_timestamp) as month,
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT CASE 
        WHEN o.order_status = 'delivered' THEN o.order_id 
    END) as delivered_orders,
    COUNT(DISTINCT CASE 
        WHEN o.order_status = 'canceled' THEN o.order_id 
    END) as canceled_orders,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN o.order_status = 'delivered' THEN o.order_id END) /
        COUNT(DISTINCT o.order_id),
        2
    ) as delivery_success_rate,
    ROUND(
        AVG(CASE 
            WHEN o.order_delivered_customer_date IS NOT NULL 
            THEN JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_purchase_timestamp)
        END),
        1
    ) as avg_delivery_time_days,
    COUNT(DISTINCT CASE 
        WHEN JULIANDAY(o.order_delivered_customer_date) > JULIANDAY(o.order_estimated_delivery_date)
        THEN o.order_id
    END) as late_deliveries,
    ROUND(
        100.0 * COUNT(DISTINCT CASE 
            WHEN JULIANDAY(o.order_delivered_customer_date) > JULIANDAY(o.order_estimated_delivery_date)
            THEN o.order_id
        END) / NULLIF(COUNT(DISTINCT CASE WHEN o.order_status = 'delivered' THEN o.order_id END), 0),
        2
    ) as late_delivery_rate
FROM olist_orders_dataset o
WHERE o.order_purchase_timestamp IS NOT NULL
GROUP BY strftime('%Y-%m', o.order_purchase_timestamp)
ORDER BY month DESC
LIMIT 12;


-- ============================================================
-- Query 2: Seller Performance Ranking
-- Business Question: "Which sellers are performing best?"
-- Use Case: Seller management, partnerships
-- ============================================================

SELECT 
    s.seller_id,
    s.seller_city,
    s.seller_state,
    COUNT(DISTINCT oi.order_id) as total_orders,
    COUNT(DISTINCT oi.product_id) as products_sold,
    ROUND(SUM(oi.price), 2) as total_revenue,
    ROUND(AVG(oi.price), 2) as avg_product_price,
    ROUND(AVG(r.review_score), 2) as avg_review_score,
    COUNT(DISTINCT r.review_id) as review_count,
    ROUND(
        AVG(JULIANDAY(o.order_delivered_customer_date) - 
            JULIANDAY(o.order_purchase_timestamp)),
        1
    ) as avg_delivery_days,
    CASE 
        WHEN AVG(r.review_score) >= 4.5 AND AVG(JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_purchase_timestamp)) <= 10 
            THEN 'Top Performer'
        WHEN AVG(r.review_score) >= 4.0 
            THEN 'Good Performer'
        WHEN AVG(r.review_score) >= 3.0 
            THEN 'Average Performer'
        ELSE 'Needs Improvement'
    END as performance_tier
FROM olist_sellers_dataset s
JOIN olist_order_items_dataset oi ON s.seller_id = oi.seller_id
JOIN olist_orders_dataset o ON oi.order_id = o.order_id
LEFT JOIN olist_order_reviews_dataset r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
GROUP BY s.seller_id, s.seller_city, s.seller_state
HAVING total_orders >= 10  -- Sellers with 10+ orders
ORDER BY total_revenue DESC
LIMIT 50;
