import os
import feedparser
from google import genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_blogger_service():
    creds = Credentials(
        None,
        refresh_token=os.environ['BLOGGER_REFRESH_TOKEN'],
        client_id=os.environ['BLOGGER_CLIENT_ID'],
        client_secret=os.environ['BLOGGER_CLIENT_SECRET'],
        token_uri="https://oauth2.googleapis.com/token"
    )
    return build('blogger', 'v3', credentials=creds)

def run_bot():
    try:
        # පුවත් මූලාශ්‍ර කිහිපයක් පරීක්ෂා කිරීම (Ada Derana, Hiru, BBC)
        feeds = [
            "https://www.adaderana.lk/rss.php",
            "http://www.hirunews.lk/rss/sinhala.xml",
            "https://feeds.bbci.co.uk/news/world/rss.xml"
        ]
        
        news_entry = None
        for url in feeds:
            feed = feedparser.parse(url)
            if feed.entries:
                news_entry = feed.entries[0]
                break
        
        if not news_entry:
            print("No news entries found from any source.")
            return
        
        # Gemini AI Client
        client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
        
        # සිංහල සහ ඉංග්‍රීසි පුවත් සැකසීමට උපදෙස්
        prompt = (
            f"Generate a professional blog post. First write a detailed Sinhala version, "
            f"then an English version for this news: {news_entry.title}. "
            f"Summary: {news_entry.summary}. Use HTML <br> for spacing and <b> for highlights."
        )
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        content = response.text.replace('\n', '<br>')
        
        # Blogger වෙත යැවීම
        service = get_blogger_service()
        blog_id = os.environ['BLOGGER_ID']
        
        body = {
            'title': news_entry.title,
            'content': content,
            'labels': ['News', 'AI-Update']
        }
        
        result = service.posts().insert(blogId=blog_id, body=body, isDraft=False).execute()
        
        print("-" * 30)
        print(f"SUCCESS: Post Published!")
        print(f"URL: {result.get('url')}")
        print("-" * 30)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        exit(1)

if __name__ == "__main__":
    run_bot()
