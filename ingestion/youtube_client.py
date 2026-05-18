from googleapiclient.discovery import build


class YouTubeClient:
    def __init__(self, api_key: str):
        self.client = build("youtube", "v3", developerKey=api_key)

    def search_channel(self, query: str) -> dict:
        request = self.client.search().list(
            part="snippet",
            q=query,
            type="channel",
            maxResults=5,
        )
        return request.execute()

    def get_channel_by_id(self, channel_id: str) -> dict:
        request = self.client.channels().list(
            part="snippet,statistics,contentDetails",
            id=channel_id,
        )
        return request.execute()

    def get_channel_by_handle(self, handle: str) -> dict:
        request = self.client.channels().list(
            part="snippet,statistics,contentDetails",
            forHandle=handle,
        )
        return request.execute()

    def get_uploads_playlist_id(self, channel_id: str) -> str | None:
        response = self.get_channel_by_id(channel_id)
        items = response.get("items", [])

        if not items:
            return None

        return (
            items[0]
            .get("contentDetails", {})
            .get("relatedPlaylists", {})
            .get("uploads")
        )
    
    def get_playlist_items(
        self,
        playlist_id: str,
        page_token: str | None = None,
        max_results: int = 50,
    ) -> dict:
        request = self.client.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=max_results,
            pageToken=page_token,
        )
        return request.execute()

    def get_videos_by_ids(self, video_ids: list[str]) -> dict:
        request = self.client.videos().list(
            part="snippet,contentDetails,statistics",
            id=",".join(video_ids),
            maxResults=50,
        )
        return request.execute()
