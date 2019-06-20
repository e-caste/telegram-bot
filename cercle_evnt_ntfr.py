#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep

def main():
    url = 'https://www.facebook.com/pg/cerclemusic/events/?ref=page_internal'
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    link_result = []
    text_result = []

    while True:
        try:
            upcoming_events_card = driver.find_element_by_id('upcoming_events_card')
            events = upcoming_events_card.find_element_by_xpath('descendant::a')
            break
        except Exception as e:
            print(e)
            sleep(2)

    if isinstance(events, list):
        links_to_events = []
        for event in events:
            links_to_events.append(event.get_attribute('href').split("?")[0])
            # print(event.get_attribute('href'))
    else:
        links_to_events = []
        links_to_events.append(events.get_attribute('href').split("?")[0])
        # print(link_to_event)

    # UPDATE EVENT LINKS FILE
    with open('cercle_events_links.txt', 'r+') as db:
        db_links = db.read()
        for link in links_to_events:
            if link not in db_links:
                # notify user via Telegram
                link_result.append(link)
                db.seek(0)
                db.write(link + "\n" + db_links)
                db_links = db.read()


    # ALSO UPDATE EVENT DETAILS FILE
    if upcoming_events_card.text.count("Get Tickets") == 1:
        full_text = upcoming_events_card.text.split("Share Events\n")[1].split("Get Tickets")[0]
        text_list = []
        text_list.append(full_text)
    else:
        text_list = upcoming_events_card.text.split("Share Events\n")[1].split("Get Tickets")
        full_text = ""
        for item in text_list:
            full_text += item
            full_text += "\n\n"
        del full_text[:-2]

    # print(full_text)

    with open('cercle_events.txt', 'r+') as db:
        db_text = db.read()
        for text_event in text_list:
            if text_event not in db_text:
                # notify user via Telegram
                text_result.append(text_event)
                db.seek(0)
                db.write(text_event + db_text)
                db_text = db.read()


    return link_result, text_result

if __name__ == '__main__':
    main()








# import requests
# from bs4 import BeautifulSoup
# import re
#
#
# def main():
#     url = 'https://www.facebook.com/pg/cerclemusic/events/?ref=page_internal'
#     events_fb_page = requests.get(url)
#     # soup = BeautifulSoup(events_fb_page.text, 'html.parser')
#     soup = BeautifulSoup(events_fb_page.text, 'html5lib')
#
#     # upcoming_events_card = soup.find_all()
#     upcoming_events_card = soup.find_all(id="upcoming_events_card")
#     # events = soup.find_all('a', attrs={'data-hovercard'})
#     # events = soup.find_all(href=re.compile("/events/"))
#     events = []
#     for event in upcoming_events_card: # .find_all(href=re.compile("/events/"))
#         print(event)
#
#     # if events is not None:
#     #     for event in events.find_all('a'):
#     #         print(event)
#     #     exit(0)
#     # else:
#     #     exit(1)
#
# # upcoming_events_card = soup.find('div', {'id': 'upcoming_events_card'})
# # upcoming_events = upcoming_events_card.find_all('a')
#
#
# if __name__ == '__main__':
#     main()
