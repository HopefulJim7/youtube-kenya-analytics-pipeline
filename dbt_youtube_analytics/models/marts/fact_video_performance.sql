SELECT
    snapshot_date,
    video_id,
    channel_id,
    view_count,
    like_count,
    comment_count
FROM {{ ref('stg_youtube__videos') }}