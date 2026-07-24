{% set configs = [{
    "table":"walmart_database.silver_t.orders_t",
    "columns":"""o.order_id, o.customer_id, o.store_id, o.order_timestamp, o.payment_method,
    o.order_status, o.total_amount,
    o.created_timestamp, o.updated_timestamp, o.is_active, o.processed_at"""
    "alias":"o"
    },
    {
        "table":"walmart_database.silver_t.customers",
        "columns":"""customer_id, first_name, last_name, email, phone,
    city, province, country,
    created_timestamp, updated_timestamp, is_active, processed_at"""
    },
    {
        "table":"walmart_database.silver_t.employees",
        "columns":"""o.employee_id, o.store_id, o.first_name, o.last_name, o.email, o.job_title, o.salary,
    o.created_timestamp, o.updated_timestamp, o.is_active, o.processed_at"""
        "alias":"o"
    },
    {
        "table":"walmart_database.silver_t.order_items",
        "columns":"""ot.order_item_id, ot.order_id, ot.product_id, ot.quantity, ot.unit_price, ot.line_amount,
    ot.created_timestamp, ot.updated_timestamp, ot.is_active, ot.processed_at"""
        "alias":"ot"
    },

    {
        "table":"walmart_database.silver_t.products_t",
        "columns":"""product_id, product_name, category, brand, price,
    created_timestamp, updated_timestamp, is_active, processed_at"""
    },
    {
        "table":"walmart_database.silver_t.stores",
        "columns":"""store_id, store_name, city, province, country,
    created_timestamp, updated_timestamp, is_active, processed_at"""
    }
]}





-- customers
SELECT
    customer_id, first_name, last_name, email, phone,
    city, province, country,
    created_timestamp, updated_timestamp, is_active, processed_at
FROM walmart.silver_t.customers;

-- employees
SELECT
    employee_id, store_id, first_name, last_name, email, job_title, salary,
    created_timestamp, updated_timestamp, is_active, processed_at
FROM walmart.silver_t.employees;

-- order_items
SELECT
    order_item_id, order_id, product_id, quantity, unit_price, line_amount,
    created_timestamp, updated_timestamp, is_active, processed_at
FROM walmart.silver_t.order_items;

-- orders_t
SELECT
    order_id, customer_id, store_id, order_timestamp, payment_method,
    order_status, total_amount,
    created_timestamp, updated_timestamp, is_active, processed_at
FROM walmart.silver_t.orders_t;

-- products_t
SELECT
    product_id, product_name, category, brand, price,
    created_timestamp, updated_timestamp, is_active, processed_at
FROM walmart.silver_t.products_t;

-- stores
SELECT
    store_id, store_name, city, province, country,
    created_timestamp, updated_timestamp, is_active, processed_at
FROM walmart.silver_t.stores;