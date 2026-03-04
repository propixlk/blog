import os
import feedparser
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import time

def get_blogger_service():
    """GitHub Secrets භාවිතා කර Blogger API වෙත සම්බන්ධ වේ."""
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
        # 1. පුවත් මූලාශ්‍රය (Ada Derana RSS) පරීක්ෂා කිරීම
        feed = feedparser.parse("https://www.adaderana.lk/rss.php")
        if not feed.entries:
            print("පුවත් කිසිවක් හමු නොවීය.")
            return

        top_news = feed.entries[0]
        news_title = top_news.title
        news_summary = top_news.summary
        news_link = top_news.link

        # 2. පින්තූරය ලබා ගැනීමට උත්සාහ කිරීම (RSS Feed එකෙන්)
        image_html = ""
        if 'links' in top_news:
            for link in top_news.links:
                if 'image' in link.get('type', ''):
                    image_html = f'<div style="text-align:center;"><img src="{link.href}" style="width:100%; max-width:600px; border-radius:10px;"></div><br>'

        # 3. Gemini AI සැකසුම සහ පෝස්ට් එක ලිවීම
        genai.configure(api_key=os.environ['GEMINI_API_KEY'])
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = (
            f"Write a professional and engaging news article in Sinhala for a blog. "
            f"Use a creative heading. Format with bold text where necessary. "
            f"Original News Title: {news_title}. "
            f"Original Summary: {news_summary}."
        )
        
        response = model.generate_content(prompt)
        sinhala_content = response.text.replace('\n', '<br>')

        # 4. Blogger වෙත පෝස්ට් එක යැවීම
        service = get_blogger_service()
        blog_id = os.environ['BLOGGER_ID'] #

        post_body = {
            'title': f"{news_title} - AI පුවත්",
            'content': f"{image_html}{sinhala_content}<br><br><p><small>මූලාශ්‍රය: <a href='{news_link}'>{news_link}</a></small></p>",
            'labels': ['News', 'Automated'],
        }

        # isDraft=False මගින් පෝස්ට් එක කෙලින්ම Publish කරනු ලබයි
        request = service.posts().insert(blogId=blog_id, body=post_body, isDraft=False)
        result = request.execute()

        print(f"පෝස්ට් එක සාර්ථකව පළ විය! URL: {result.get('url')}")

    except Exception as e:
        print(f"දෝෂයක් ඇති විය: {e}")
        # GitHub Actions වලට failure එකක් ලෙස පෙන්වීමට exit(1) භාවිතා කරයි
        exit(1)

if __name__ == "__main__":
    run_bot()
