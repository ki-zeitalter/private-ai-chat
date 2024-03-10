import bs4
import requests


def scrape(url: str):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = bs4.BeautifulSoup(response.text, 'lxml')

    return soup.body.get_text(' ', strip=True)
