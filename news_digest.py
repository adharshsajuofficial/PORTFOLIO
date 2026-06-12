import os
import urllib.request
import xml.etree.ElementTree as ET
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ==============================================================================
# CONFIGURATION
# ==============================================================================
SENDER_EMAIL = "adharshsajuofficial@gmail.com"
RECEIVER_EMAIL = "adharshsajuofficial@gmail.com"

# Reliable RSS feeds from 3 major global/tech news sources
NEWS_FEEDS = {
    "BBC World News": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "TechCrunch": "https://techcrunch.com/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml"
}
# ==============================================================================

def fetch_headlines(source_name, url):
    print(f"Scanning headlines from: {source_name}...")
    headlines = []
    
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            # Find all article items inside the XML tree
            # Both RSS 2.0 and Atom feeds use 'item' or 'entry' channels
            items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            for item in items[:4]:  # Grab top 4 stories per website
                title = item.find('title') or item.find('{http://www.w3.org/2005/Atom}title')
                link = item.find('link') or item.find('{http://www.w3.org/2005/Atom}link')
                pub_date = item.find('pubDate') or item.find('{http://www.w3.org/2005/Atom}published')
                
                # Extract link href text safely depending on XML structure variants
                link_text = link.text if link.text else link.get('href')
                
                if title is not None and link_text:
                    headlines.append({
                        "title": title.text.strip(),
                        "link": link_text.strip(),
                        "time": pub_date.text.strip() if pub_date is not None else "Recent"
                    })
    except Exception as e:
        print(f"Warning: Failed to parse data channel for {source_name}: {e}")
        
    return headlines

def generate_html_digest(all_news):
    today_str = datetime.now().strftime("%A, %B %d, %Y")
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #1a365d; border-bottom: 2px solid #3182ce; padding-bottom: 10px;">📰 Your Daily News Briefing</h2>
        <p style="color: #718096; font-size: 0.9rem;">Generated automatically on {today_str}</p>
    """
    
    for source, articles in all_news.items():
        html += f"<h3 style='color: #2b6cb0; margin-top: 25px; margin-bottom: 10px;'>{source}</h3>"
        if not articles:
            html += "<p style='color: #a0aec0; font-style: italic;'>No headlines retrieved today.</p>"
            continue
            
        html += "<ul style='padding-left: 20px; margin: 0;'>"
        for art in articles:
            html += f"""
            <li style="margin-bottom: 12px;">
                <a href="{art['link']}" style="color: #2b6cb0; text-decoration: none; font-weight: bold;">{art['title']}</a><br>
                <span style="font-size: 0.75rem; color: #a0aec0;">⏱️ Published: {art['time']}</span>
            </li>
            """
        html += "</ul>"
        
    html += """
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin-top: 30px;">
        <p style="font-size: 0.8rem; color: #a0aec0; text-align: center;">Automated Digest Channel powered by GitHub Actions</p>
    </body>
    </html>
    """
    return html

def main():
    email_password = os.getenv("EMAIL_APP_PASSWORD")
    if not email_password:
        print("Missing Email App Password credentials. Execution terminated.")
        return

    all_news = {}
    for source_name, url in NEWS_FEEDS.items():
        all_news[source_name] = fetch_headlines(source_name, url)
        
    html_content = generate_html_digest(all_news)
    
    # Pack and dispatch email payload
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"📰 Morning Briefing: Top Headlines Summary"
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        print("Connecting to secure Gmail SMTP relay server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SENDER_EMAIL, email_password)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("Daily news summary compiled and emailed successfully!")
    except Exception as e:
        print(f"Failed to dispatch news packet: {e}")

if __name__ == "__main__":
    main()
