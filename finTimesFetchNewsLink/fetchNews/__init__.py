import logging
import azure.functions as func
import requests
from bs4 import BeautifulSoup
import re

def fetch_ft_technology_headlines():
    try:
        logging.info('Fetching FT technology headlines.')
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }

        base_url = 'https://www.ft.com/technology'
        response = requests.get(base_url, headers=headers)
        logging.info(f'HTTP GET to {base_url} returned status code {response.status_code}.')

        if response.status_code != 200:
            logging.error(f'Failed to fetch page: {response.status_code}')
            return []

        soup = BeautifulSoup(response.content, 'html.parser')

        main_list = soup.find('ul', class_='o-teaser-collection__list js-stream-list')
        
        if not main_list:
            logging.warning('Main list not found.')
            return []

        links = main_list.find_all('a', {'data-trackable': 'heading-link', 'class': 'js-teaser-heading-link'})
        
        headlines_seen = set()
        headlines_data = []
        for link in links:
            url = 'https://www.ft.com' + link['href']
            text = re.sub(r'^\d+\.\s+', '', link.get_text(strip=True))
            if text and len(text) > 20 and url not in headlines_seen:
                headlines_seen.add(url)
                headlines_data.append(f'<a href="{url}">{text}</a>')

        logging.info(f'Found {len(headlines_data)} headlines.')
        return headlines_data
    
    except Exception as e:
        logging.error(f'Error in fetch_ft_technology_headlines: {e}')
        raise

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        headlines_data = fetch_ft_technology_headlines()
        html_response = "<br><br>".join(headlines_data)

        return func.HttpResponse(
            html_response,
            mimetype="text/html",
            status_code=200
        )
    except Exception as e:
        logging.error(f'Error in main function execution: {e}')
        return func.HttpResponse(
            "An error occurred while processing the request.",
            status_code=500
        )
