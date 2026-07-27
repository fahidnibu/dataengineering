SELECT
    DISTINCT
    order_id,
    order_item_id,
    order_timestamp,
    payment_method,
    order_status,
    total_amount,
    order_created_timestamp,
    order_updated_timestamp,
    order_is_active,
    order_processed_at,
    CURRENT_TIMESTAMP() AS eph_orders_processed_at
FROM {{ ref('obt_b') }}