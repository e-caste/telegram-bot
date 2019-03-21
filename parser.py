from bs4 import BeautifulSoup as bs
import requests

# print(soup.prettify())

# print(list(soup.children))

def get_wiki_daily_quote():
    url = "https://en.wikiquote.org/wiki/Main_Page"
    page = requests.get(url)
    soup = bs(page.content, 'html.parser')
    quote = ""

    for a in soup.find_all('i')[1]:
        # print(a.string, end="")
        quote += str(a.string)

    cit = soup.select('div > table > tbody > '
                      'tr > td > table > '
                      'tbody > tr > td > '
                      'table > tbody > tr > td > a')

    return quote + "\n\ncit: " + cit[0].string

# print(quote + "\n\ncit: " + cit[0].string)

# print(get_wiki_daily_quote())