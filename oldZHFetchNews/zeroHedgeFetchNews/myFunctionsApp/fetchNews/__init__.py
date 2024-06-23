import logging
import requests
from bs4 import BeautifulSoup
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        headlines = fetch_news_headlines()
        response_message = format_headlines_as_text(headlines)
        return func.HttpResponse(response_message, status_code=200)
    except Exception as e:
        return func.HttpResponse(
             f"An error occurred: {str(e)}",
             status_code=500
        )

def fetch_news_headlines():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }

    base_url = 'https://www.zerohedge.com'
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    a_tags = soup.find_all('a', href=True)
    headlines = []
    categories = ['/markets', '/geopolitical', '/medical', '/political', '/military', '/commodities', '/economics', '/technology', '/energy', '/environment', '/health']
    
    for tag in a_tags:
        href = tag['href']
        if any(category in href for category in categories):
            raw_text = tag.get_text(strip=True).replace(u'\xa0', u' ')
            cleaned_text = ' '.join(word for word in raw_text.split() if not (word.isdigit() and len(word) == 1))
            if cleaned_text:
                full_url = base_url + href
                headlines.append((cleaned_text, full_url))

    return headlines

def format_headlines_as_text(headlines):
    return "\n\n".join(f"{headline}\n{url}" for headline, url in headlines)

