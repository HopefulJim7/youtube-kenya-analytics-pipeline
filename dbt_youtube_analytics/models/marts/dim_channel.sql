WITH channel_stats AS (
    SELECT *
    FROM {{ ref('stg_youtube__channel_stats') }}
),

latest_channel_snapshot AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY channel_id
            ORDER BY snapshot_date DESC
        ) AS row_number
    FROM channel_stats
)

SELECT
    channel_id,
    configured_name,
    channel_title,
    channel_description,
    published_at,
    country,
    configured_country,
    configured_niche
FROM latest_channel_snapshot
WHERE row_number = 1