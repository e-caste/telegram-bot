#!/usr/bin/env python3

from selenium import webdriver
from pyvirtualdisplay import Display
from time import sleep
from subprocess import Popen

def main():
    url = 'https://www.facebook.com/pg/cerclemusic/events/?ref=page_internal'
    display = Display(visible=0, size=(1920, 1080))
    display.start()
    driver = webdriver.Firefox()
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
    text_list = []
    if upcoming_events_card.text.count("Get Tickets") == 1:
        full_text = upcoming_events_card.text.split("Share Events\n")[1].split("·")[0] + \
                    upcoming_events_card.text.split("guests")[1].split("Get Tickets")[0]
        text_list.append(full_text)
    else:
        text_list_with_guest_numbers = upcoming_events_card.text.split("Share Events\n")[1].split("Get Tickets")
        for item in text_list_with_guest_numbers:
            text_list.append(item.split("·")[0] + item.split("guests")[1])

    with open('cercle_events.txt', 'r+') as db:
        db_text = db.read()
        for text_event in text_list:
            if text_event not in db_text:
                # notify user via Telegram
                text_result.append(text_event)
                db.seek(0)
                db.write(text_event + db_text)
                db_text = db.read()

    processes_to_kill = [
        "firefox-esr",
        "Xvfb"
    ]
    for process in processes_to_kill:
        Popen(['killall', process])

    if len(link_result) == len(text_result):
        return link_result, text_result
    else:
        return link_result, None

if __name__ == '__main__':
    main()
