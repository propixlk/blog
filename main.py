import os
import feedparser
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_blogger_service():
    # Credentials භාවිතා කිරීම
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
        # පුවත් මූලාශ්‍රය
        feed = feedparser.parse("https://www.adaderana.lk/rss.php")
        if not feed.entries: return
        
        top_news = feed.entries[0]
        genai.configure(api_key=os.environ['GEMINI_API_KEY'])
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # සිංහල සහ ඉංග්‍රීසි යන භාෂා දෙකෙන්ම ලිවීමට උපදෙස්
        prompt = f"Write a professional blog post. First write a Sinhala version and then an English version of this news: {top_news.title} - {top_news.summary}. Use HTML tags like <b> and <br>."
        response = model.generate_content(prompt)
        content = response.text.replace('\n', '<br>')
        
        service = get_blogger_service()
        blog_id = os.environ['BLOGGER_ID'] #

        body = {
            'title': top_news.title,
            'content': content,
            'labels': ['News', 'AI-Update']
        }

        # isDraft=False මගින් කෙලින්ම සජීවී වේ
        result = service.posts().insert(blogId=blog_id, body=body, isDraft=False).execute()
        
        # සාර්ථකව පෝස්ට් වූ බව තහවුරු කිරීමට Link එක පෙන්වයි
        print(f"පෝස්ට් එක සාර්ථකයි! URL: {result.get('url')}")

    except Exception as e:
        print(f"වැරදීමක් සිදු විය: {e}")
        exit(1)

if __name__ == "__main__":
    run_bot()
