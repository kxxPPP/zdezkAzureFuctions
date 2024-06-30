import logging
import requests
from bs4 import BeautifulSoup
import re
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        headlines = fetch_news_headlines()
        response_message = format_headlines_as_text(headlines)
        return func.HttpResponse(response_message, status_code=200)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
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

    base_url = 'https://www.bloomberg.com/technology'
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    main_section = soup.find('section', class_='zone_zone__7Ypxu zone_righty__eeKbc')
    
    for excluded_section in main_section.find_all('section', class_='zone_right-rail__9g5Ro'):
        excluded_section.decompose()

    links = main_section.find_all('a', href=True)
    
    headlines_seen = set()
    headlines_data = []
    for link in links:
        url = 'https://www.bloomberg.com' + link['href']
        text = re.sub(r'^\d+\.\s+', '', link.get_text(strip=True))
        if text and len(text) > 20 and url not in headlines_seen:
            headlines_seen.add(url)
            headlines_data.append((text, url))

    return headlines_data

def format_headlines_as_text(headlines):
    return "\n\n".join(f"{headline}\n{url}" for headline, url in headlines)
