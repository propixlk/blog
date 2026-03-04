import os
import feedparser
import google.generativeai as genai
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
    # Ada Derana RSS Feed එකෙන් පුවත් ගනී
    feed = feedparser.parse("https://www.adaderana.lk/rss.php")
    if not feed.entries: return
    
    top_news = feed.entries[0]
    
    # Gemini AI සැකසුම
    genai.configure(api_key=os.environ['GEMINI_API_KEY'])
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"Rewrite this news in professional Sinhala for a blog. Title: {top_news.title}. Content: {top_news.summary}"
    response = model.generate_content(prompt)
    sinhala_content = response.text.replace('\n', '<br>')
    
    # Blogger වෙත යැවීම
    service = get_blogger_service()
    body = {
        'title': f"පුවත්: {top_news.title}",
        'content': f"{sinhala_content}<br><br><small>Source: {top_news.link}</small>"
    }
    service.posts().insert(blogId=os.environ['BLOGGER_ID'], body=body).execute()

if __name__ == "__main__":
    run_bot()
