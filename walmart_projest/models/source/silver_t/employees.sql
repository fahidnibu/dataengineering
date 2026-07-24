{{
    config(
        materialized='incremental',
        unique_key='employee_id'
    ) 
    }}

SELECT 
  *,
    CURRENT_TIMESTAMP() AS processed_at
FROM {{ source('walmart_database', 'employees') }}


{% if is_incremental() %}

    AND updated_timestamp > (SELECT COALESCE(MAX(updated_timestamp), '1900-01-01') FROM {{ this }})

{% endif %}