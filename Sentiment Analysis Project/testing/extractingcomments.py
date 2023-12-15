import os
import csv
from googleapiclient.discovery import build

class YouTubeCommentsExtractor:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build("youtube", "v3", developerKey=api_key)

    def extract_comments(self, video_id, max_results=1000):
        comments = []
        next_page_token = None

        while True:
            comment_request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(100, max_results),
                pageToken=next_page_token
            )
            response = comment_request.execute()

            for comment in response.get("items", []):
                snippet = comment["snippet"]["topLevelComment"]["snippet"]
                comment_text = snippet["textDisplay"]
                author = snippet["authorDisplayName"]
                published_at = snippet["publishedAt"]
                comments.append([comment_text, author, published_at])

            next_page_token = response.get("nextPageToken")
            if not next_page_token or len(comments) >= max_results:
                break

        return comments

    def save_to_csv(self, comments, output_file):
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Comment", "Author", "Published At"])
            csv_writer.writerows(comments)

