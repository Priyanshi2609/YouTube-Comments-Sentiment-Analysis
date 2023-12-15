from pytube import YouTube

class YoutubeInput:
    def __init__(self, video_id):
        self.id = video_id
        self.yt = YouTube(url=f'https://youtu.be/{self.id}?')

    def get_thumbnail(self):
        image_url = self.yt.thumbnail_url
        return image_url

