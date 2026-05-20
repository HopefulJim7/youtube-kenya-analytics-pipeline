WITH source AS (
    SELECT *
    FROM {{ source('youtube_raw', 'raw_channel_stats') }}
),

renamed AS (
    SELECT
        snapshot_date,
        channel_id,
        configured_name,
        channel_title,
        channel_description,
        published_at,
        country,
        configured_country,
        configured_niche,
        subscriber_count,
        view_count,
        video_count,
        hidden_subscriber_count
    FROM source
)

SELECT *
FROM renamed