import logging
import requests
from bs4 import BeautifulSoup
import re
import azure.functions as func

def fetch_antiwar_articles():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }

    base_url = 'https://antiwar.com/'
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the <table> tags with the specified attributes
    table_tags = soup.find_all('table', width="486", border="0", cellspacing="0", cellpadding="0", bgcolor="#F3F5F6")

    articles_data = []
    for table in table_tags:
        # Find all <a> tags within the <table> tags
        links = table.find_all('a', href=True)
        for link in links:
            url = link['href']
            text = link.get_text(strip=True)
            # Normalize whitespace
            text = re.sub(r'\s+', ' ', text)
            if text and len(text) > 20:  # Filter to avoid irrelevant links
                # Create HTML element
                html_element = f'<a href="{url}">{text}</a>'
                articles_data.append(html_element)

    return articles_data

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Fetch the articles
    articles_data = fetch_antiwar_articles()

    # Join the HTML elements into a single string with double spacing (2 <br> tags)
    response_content = "<br><br>\n".join(articles_data)

    return func.HttpResponse(response_content, mimetype="text/html")
