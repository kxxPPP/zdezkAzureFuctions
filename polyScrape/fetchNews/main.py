import asyncio
from playwright.async_api import async_playwright
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def fetch_polymarket_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        base_url = 'https://polymarket.com/'

        try:
            await page.goto(base_url)
            await page.wait_for_selector('div.c-dhzjXW.c-dhzjXW-ieRtncW-css', timeout=5000)
        except Exception as e:
            logging.error(f"Page navigation or loading failed: {e}")
            await browser.close()
            return []

        parent_sections = await page.query_selector_all('div.c-dhzjXW.c-dhzjXW-ieRtncW-css')

        if not parent_sections:
            logging.warning("Parent sections not found")
            await browser.close()
            return []

        async def extract_market_data(market):
            # Gather all the necessary elements in parallel
            title_element, subject_elements, percentage_elements, bet_section = await asyncio.gather(
                market.query_selector('p.c-dqzIym.c-dqzIym-fxyRaa-color-normal.c-dqzIym-cTvRMP-spacing-normal.c-dqzIym-dxJWYY-weight-bold.c-dqzIym-gKzrVx-lines-2.c-dqzIym-ihMZKul-css'),
                market.query_selector_all('p.c-dqzIym.c-dqzIym-fxyRaa-color-normal.c-dqzIym-cTvRMP-spacing-normal.c-dqzIym-jalaKP-weight-normal.c-dqzIym-iLHpdH-lines-1.c-dqzIym-ieWzmqD-css'),
                market.query_selector_all('p.c-dqzIym.c-dqzIym-fxyRaa-color-normal.c-dqzIym-cTvRMP-spacing-normal.c-dqzIym-iIobgq-weight-medium.c-dqzIym-icjKTkb-css'),
                market.query_selector('div.c-dhzjXW.c-dhzjXW-ibFYNkb-css')
            )

            title = await title_element.inner_text() if title_element else "Title not found"
            subjects = [await se.inner_text() for se in subject_elements]

            if not percentage_elements and not subjects and bet_section:
                bet_elements = await bet_section.query_selector_all('span.c-PJLV')
                subjects = [await be.inner_text() for be in bet_elements if await be.inner_text() != "Bet"]
                subjects = [subject.replace("Bet ", "") for subject in subjects]

                percentage_elements = await market.query_selector_all('p.c-dqzIym.c-dqzIym-fxyRaa-color-normal.c-dqzIym-cTvRMP-spacing-normal.c-dqzIym-iIobgq-weight-medium.c-dqzIym-hzzdKO-size-md.c-dqzIym-igjdJOs-css')
                if percentage_elements:
                    yes_percentage_text = await percentage_elements[0].inner_text()
                    yes_percentage = int(yes_percentage_text.replace('%', '').strip())
                    no_percentage = 100 - yes_percentage
                    percentages = [f"{yes_percentage}%", f"{no_percentage}%"]
                else:
                    percentages = []
            else:
                percentages = [await pe.inner_text() for pe in percentage_elements]

            return {
                "title": title,
                "subjects": subjects,
                "percentages": percentages
            }

        # Collect market data tasks
        market_section_tasks = []
        for parent_section in parent_sections:
            market_section = await parent_section.query_selector('div.c-bQzyIt.c-ecfoyU')
            if market_section:
                logging.info("Market section found")
                markets = await market_section.query_selector_all('div.c-dhzjXW.c-dhzjXW-idNOCmT-css')
                market_section_tasks.extend([extract_market_data(market) for market in markets])

        market_data = await asyncio.gather(*market_section_tasks)

        logging.info(f"Total markets found: {len(market_data)}")

        await browser.close()
        return market_data

async def generate_html_table(market_data):
    html_content = "<table border='1'>\n"
    html_content += "<thead><tr><th>Title</th><th>Outcomes</th><th>Percentages</th></tr></thead>\n"
    html_content += "<tbody>\n"

    for market in market_data:
        title = market['title']
        outcomes = "".join(f"<div>{outcome}</div>" for outcome in market['subjects'])
        percentages = "".join(f"<div>{percentage}</div>" for percentage in market['percentages'])
        html_content += f"<tr><td>{title}</td><td>{outcomes}</td><td>{percentages}</td></tr>\n"

    html_content += "</tbody>\n</table>\n"
    return html_content

# Run the function and get HTML output
async def main():
    market_data = await fetch_polymarket_data()
    if market_data:
        html_table = await generate_html_table(market_data)
        # Output the HTML table (you can save it to a file or return it from a function)
        print(html_table)

# To run the async function
asyncio.run(main())
