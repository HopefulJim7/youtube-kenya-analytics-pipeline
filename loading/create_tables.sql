CREATE TABLE IF NOT EXISTS raw_channel_stats (
    snapshot_date DATE,
    channel_id TEXT,
    configured_name TEXT,
    channel_title TEXT,
    channel_description TEXT,
    published_at TIMESTAMPTZ,
    country TEXT,
    configured_country TEXT,
    configured_niche TEXT,
    subscriber_count BIGINT,
    view_count BIGINT,
    video_count BIGINT,
    hidden_subscriber_count BOOLEAN
);

CREATE TABLE IF NOT EXISTS raw_video_metadata (
    snapshot_date DATE,
    channel_id TEXT,
    configured_channel_name TEXT,
    configured_niche TEXT,
    configured_country TEXT,
    video_id TEXT,
    video_title TEXT,
    video_description TEXT,
    published_at TIMESTAMPTZ,
    youtube_channel_title TEXT,
    category_id TEXT,
    duration TEXT,
    definition TEXT,
    caption TEXT,
    licensed_content BOOLEAN,
    view_count BIGINT,
    like_count BIGINT,
    comment_count BIGINT
);
