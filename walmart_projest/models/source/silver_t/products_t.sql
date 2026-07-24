{{
    config(
        materialized='incremental',
        unique_key='product_id'
    ) 
    }}

SELECT 
  *,
    CURRENT_TIMESTAMP() AS processed_at
FROM {{ source('walmart_database', 'products') }}


{% if is_incremental() %}

    AND updated_timestamp > (SELECT COALESCE(MAX(updated_timestamp), '1900-01-01') FROM {{ this }})

{% endif %}