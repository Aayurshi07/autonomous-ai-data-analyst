-- 1. Top 5 product categories by total revenue
SELECT ct.product_category_name_english AS category, 
       ROUND(SUM(oi.price), 2) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 5;


-- 2. Average delivery time (order purchase -> delivered) by customer state, top 10 slowest
SELECT c.customer_state,
       ROUND(AVG(JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_purchase_timestamp)), 1) AS avg_delivery_days
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
ORDER BY avg_delivery_days DESC
LIMIT 10;

-- 3. Which payment type is most common, and its average order value
SELECT payment_type,
       COUNT(*) AS num_payments,
       ROUND(AVG(payment_value), 2) AS avg_value
FROM payments
GROUP BY payment_type
ORDER BY num_payments DESC;

-- 4. Monthly order volume trend (all months)
SELECT strftime('%Y-%m', order_purchase_timestamp) AS month,
       COUNT(*) AS num_orders
FROM orders
GROUP BY month
ORDER BY month;

-- 5. Average review score by product category, min 50 reviews (avoid noisy small samples)
SELECT ct.product_category_name_english AS category,
       ROUND(AVG(r.review_score), 2) AS avg_review_score,
       COUNT(*) AS num_reviews
FROM reviews r
JOIN order_items oi ON r.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY category
HAVING COUNT(*) >= 50
ORDER BY avg_review_score ASC
LIMIT 10;

-- 6. Late deliveries: % of orders delivered after estimated date, by state
SELECT c.customer_state,
       ROUND(100.0 * SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_late
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
ORDER BY pct_late DESC
LIMIT 10;

-- 7. Top 10 sellers by total revenue
SELECT oi.seller_id,
       ROUND(SUM(oi.price), 2) AS total_revenue,
       COUNT(DISTINCT oi.order_id) AS num_orders
FROM order_items oi
GROUP BY oi.seller_id
ORDER BY total_revenue DESC
LIMIT 10;

-- 8. Freight cost as % of price, by category (which categories have disproportionately high shipping cost)
SELECT ct.product_category_name_english AS category,
       ROUND(100.0 * AVG(oi.freight_value) / AVG(oi.price), 1) AS freight_pct_of_price
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY category
ORDER BY freight_pct_of_price DESC
LIMIT 10;