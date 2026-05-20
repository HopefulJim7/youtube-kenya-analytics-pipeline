WITH source AS (
    SELECT *
    FROM {{ source('youtube_raw', 'raw_video_metadata') }}
),

renamed AS (
    SELECT
        snapshot_date,
        channel_id,
        configured_channel_name,
        configured_niche,
        configured_country,
        video_id,
        video_title,
        video_description,
        published_at,
        youtube_channel_title,
        category_id,
        duration,
        definition,
        caption,
        licensed_content,
        view_count,
        like_count,
        comment_count
    FROM source
)

SELECT *
FROM renamed