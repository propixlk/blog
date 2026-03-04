import os
import feedparser
from google import genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_blogger_service():
    creds = Credentials(
        None,
        refresh_token=os.environ['BLOGGER_REFRESH_TOKEN'],
        client_id=os.environ['BLOGGER_CLIENT_ID'], #
        client_secret=os.environ['BLOGGER_CLIENT_SECRET'], #
        token_uri="https://oauth2.googleapis.com/token"
    )
    return build('blogger', 'v3', credentials=creds)

def run_bot():
    try:
        # පුවත් ලබා ගැනීම
        feed = feedparser.parse("https://www.adaderana.lk/rss.php")
        if not feed.entries:
            print("No news entries found.")
            return
        
        entry = feed.entries[0]
        
        # අලුත් Gemini AI Client එක (google-genai)
        client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
        
        prompt = f"Create a blog post with a Sinhala section and an English section for: {entry.title}. Summary: {entry.summary}. Use HTML <br> for line breaks."
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        content = response.text.replace('\n', '<br>')
        
        # Blogger වෙත යැවීම
        service = get_blogger_service()
        blog_id = os.environ['BLOGGER_ID'] #
        
        body = {
            'title': entry.title,
            'content': content,
            'labels': ['AI-News', 'Update']
        }
        
        # isDraft=False මගින් කෙලින්ම සජීවී (Live) වේ
        result = service.posts().insert(blogId=blog_id, body=body, isDraft=False).execute()
        
        print("-" * 30)
        print(f"පෝස්ට් එක සාර්ථකයි!")
        print(f"පෝස්ට් එකේ URL එක: {result.get('url')}")
        print("-" * 30)

    except Exception as e:
        print(f"දෝෂයක් සිදු විය: {str(e)}")
        exit(1)

if __name__ == "__main__":
    run_bot()
