WITH videos AS (
    SELECT *
    FROM {{ ref('stg_youtube__videos') }}
),

latest_video_snapshot AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY video_id
            ORDER BY snapshot_date DESC
        ) AS row_number
    FROM videos
)

SELECT
    video_id,
    channel_id,
    configured_channel_name,
    configured_niche,
    configured_country,
    video_title,
    video_description,
    published_at,
    youtube_channel_title,
    category_id,
    duration,
    definition,
    caption,
    licensed_content
FROM latest_video_snapshot
WHERE row_number = 1