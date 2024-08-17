import logging
import requests
from bs4 import BeautifulSoup
import azure.functions as func

def fetch_cnn_headlines():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }

    base_url = 'https://www.cnn.com/politics'
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the main sections with the specified classes
    containers = soup.find_all('div', class_=[
        'container__field-links container_lead-plus-headlines__field-links',
        'container_list-headlines__cards-wrapper'
    ])
    
    # Extract all <a> tags within the found containers
    html_elements = []
    for container in containers:
        links = container.find_all('a', href=True)
        for link in links:
            url = 'https://www.cnn.com' + link['href']
            text = link.get_text(strip=True)
            if text and text not in ["CNN", "Getty Images"]:  # Exclude "CNN" and "Getty Images"
                # Create an HTML element for each headline with double spacing
                html_element = f'<a href="{url}">{text}</a><br><br>'
                html_elements.append(html_element)

    # Combine all HTML elements into one string
    final_html = ''.join(html_elements)
    return final_html

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Fetch the CNN headlines
    html_content = fetch_cnn_headlines()

    # Return the HTML content as the response
    return func.HttpResponse(html_content, mimetype="text/html")
