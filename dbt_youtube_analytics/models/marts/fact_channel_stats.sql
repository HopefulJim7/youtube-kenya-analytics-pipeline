SELECT
    snapshot_date,
    channel_id,
    subscriber_count,
    view_count,
    video_count,
    hidden_subscriber_count
FROM {{ ref('stg_youtube__channel_stats') }}