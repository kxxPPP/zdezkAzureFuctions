import logging
import requests
from bs4 import BeautifulSoup
import azure.functions as func

def fetch_blog_headlines():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }

    base_url = 'https://www.christophe-barraud.com/blog/'
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the div with the class 'articles-list'
    articles_list = soup.find('div', class_='articles-list')
    
    # Find all <a> tags within the articles_list div
    links = articles_list.find_all('a', href=True)
    
    # Collect the headlines and URLs, excluding "Morning Briefs" category
    headlines_data = []
    for link in links:
        url = link['href']
        text = link.get_text(strip=True)
        if text and 'category/morning-briefs' not in url:  # Excludes Morning Briefs category
            headlines_data.append((text, url))

    return headlines_data

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    headlines_data = fetch_blog_headlines()

    # Create an HTML response string
    response_html = "<html><body>"
    for headline, url in headlines_data:
        response_html += f'<p><a href="{url}">{headline}</a></p>'
    response_html += "</body></html>"

    return func.HttpResponse(response_html, mimetype="text/html")
