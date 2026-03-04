import os
import feedparser
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_blogger_service():
    """Blogger API සම්බන්ධතාවය ලබා ගැනීම."""
    creds = Credentials(
        None,
        refresh_token=os.environ['BLOGGER_REFRESH_TOKEN'],
        client_id=os.environ['BLOGGER_CLIENT_ID'],
        client_secret=os.environ['BLOGGER_CLIENT_SECRET'],
        token_uri="https://oauth2.googleapis.com/token"
    )
    return build('blogger', 'v3', credentials=creds)

def post_to_blogger(title, content, labels):
    """Blogger වෙත පෝස්ට් එක යැවීම (කෙලින්ම Publish වේ)."""
    service = get_blogger_service()
    blog_id = os.environ['BLOGGER_ID'] #
    
    body = {
        'title': title,
        'content': content,
        'labels': labels
    }
    # isDraft=False මගින් පෝස්ට් එක කෙලින්ම සජීවී වේ
    service.posts().insert(blogId=blog_id, body=body, isDraft=False).execute()

def run_bot():
    genai.configure(api_key=os.environ['GEMINI_API_KEY'])
    model = genai.GenerativeModel('gemini-1.5-flash')

    # පුවත් මූලාශ්‍ර ලැයිස්තුව (English සහ Sinhala)
    sources = [
        {"url": "https://feeds.bbci.co.uk/news/world/rss.xml", "lang": "English", "label": "Global News"},
        {"url": "https://www.adaderana.lk/rss.php", "lang": "Sinhala", "label": "Local News"}
    ]

    for source in sources:
        try:
            feed = feedparser.parse(source["url"])
            if not feed.entries: continue
            
            entry = feed.entries[0] # අලුත්ම පුවත
            
            # AI එකට උපදෙස් දීම
            prompt = (
                f"Create a professional blog post in {source['lang']} based on this: "
                f"Title: {entry.title}. Summary: {entry.summary}. "
                f"Format it beautifully with HTML tags like <b> and <p>."
            )
            
            response = model.generate_content(prompt)
            final_content = response.text.replace('\n', '<br>')
            
            # පෝස්ට් එක පළ කිරීම
            post_to_blogger(entry.title, final_content, [source['label'], "AI-Powered"])
            print(f"Successfully posted: {entry.title}")
            
        except Exception as e:
            print(f"Error with {source['lang']} source: {e}")

if __name__ == "__main__":
    run_bot()
