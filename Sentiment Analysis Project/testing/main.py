import os
from extractingcomments import YouTubeCommentsExtractor
from flask import Flask, request, render_template
from onlycomments import OnlyComments
import pandas
import re
import nltk
import string
from nltk.corpus import stopwords
from textblob import TextBlob
import yt_video
from dotenv import load_dotenv

load_dotenv()
api_key=os.getenv("API_KEY")

def get_result(videoID: str):
    ''' Overall Procedure of taking Video ID and returning dictionary consisting of sentiments analyzed '''
    def extract_comments(video_id):
        # Create an instance of the YouTubeCommentsExtractor
        extractor = YouTubeCommentsExtractor(api_key)
        # Define the maximum number of comments to retrieve
        max_results = 1000  # You can adjust this number
        # Extract comments
        comments = extractor.extract_comments(video_id, max_results)
        # Specify the output file
        output_file = "youtube_comments.csv"
        # Save comments to CSV
        extractor.save_to_csv(comments, output_file)
        return output_file
    
    output_file_for_extracted_comments = extract_comments(videoID)
    only_comments = OnlyComments()
    only_comments.extract_only_comments(output_file_for_extracted_comments)


    data = pandas.read_csv("extracted_comments_new.csv")
    # Removing stop words
    stop_words = set(stopwords.words('english'))
    def remove_stop(x):
        return " ".join([word for word in str(x).split() if word.lower() not in stop_words])
    
    removed_stop_word = data["Comment"].apply(lambda x: remove_stop(x))  # text without stop words
    data_to_clean = removed_stop_word.to_string()  # convert into string to apply further data cleaning process

    # Removing emojis using re
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F700-\U0001F77F"  # alchemical symbols
                               u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                               u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                               u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                               u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                               u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                               u"\U00002702-\U000027B0"  # Dingbats
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)


    def remove_emojis(text):
        return emoji_pattern.sub(r'', text)
    removed_emoji = remove_emojis(data_to_clean)  # text without emojis
  
    def clean_data(text):
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        # Convert it into lower case
        text = text.lower()
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        # Remove digits
        text = re.sub(r'\d+', '', text)
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        # Remove user mentions
        text = re.sub(r'@\w+', '', text)

        return text.strip()


    cleaned_text = clean_data(removed_emoji)
    cleaned_comments_list = [comment.strip(" ") for comment in cleaned_text.split("\n")]

    # Function to analyze sentiment using TextBlob
    def analyze_sentiment(comment):
        analysis = TextBlob(comment)
        if analysis.sentiment.polarity > 0:
            return 'Positive'
        elif analysis.sentiment.polarity == 0:
            return 'Neutral'
        else:
            return 'Negative'


    # Apply sentiment analysis to the comments and aggregate results
    sentiments = [analyze_sentiment(comment) for comment in cleaned_comments_list]
    positive_count = sentiments.count('Positive')
    neutral_count = sentiments.count('Neutral')
    negative_count = sentiments.count('Negative')
    return {
        "positive_count": positive_count,
        "neutral_count": neutral_count,
        "negative_count": negative_count
    }



app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/process_input", methods=["POST"])
def take_input():
    video_id = request.form["query"]
    result = get_result(videoID=video_id)
    my_youtube_video = yt_video.YoutubeInput(video_id=video_id)
    image_thumbnail_url = my_youtube_video.get_thumbnail()
    video_name = my_youtube_video.yt.title
    positive = result["positive_count"]
    neutral = result["neutral_count"]
    negative = result["negative_count"]
    result_list: list = [positive, neutral, negative]
    no_of_comments = sum(result_list)
    p_result_list = [round(count*100/no_of_comments, 2) for count in result_list]

    return render_template("datavisualization.html",
                           result=p_result_list,
                           result_dict=result,
                           image_thumbnail_url=image_thumbnail_url,
                           video_name=video_name,
                           comments=result_list
                           )

if __name__ == "__main__":
    app.run(debug=True)
