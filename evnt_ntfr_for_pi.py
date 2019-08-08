#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display
from time import sleep
from subprocess import Popen

def main():
    link_result = []
    text_result = []

    urls = [
        'https://www.facebook.com/pg/cerclemusic/events/?ref=page_internal',
        'https://www.facebook.com/pg/thedreamersrec/events/?ref=page_internal',
        'https://www.facebook.com/pg/SupermarketTorino/events/?ref=page_internal'
    ]

    links = [
        'cercle_events_links.txt',
        'thedreamers_events_links.txt',
        'supermarket_events_links.txt'
    ]

    texts = [
        'cercle_events.txt',
        'thedreamers_events.txt',
        'supermarket_events.txt'
    ]

    # make list of dicts
    urls_filenames = []
    for url, link, text in zip(urls, links, texts):
        urls_filenames.append({
            'url': url,
            'links_file': link,
            'text_file': text
        })

    for url_filenames in urls_filenames:
        display = Display(visible=0, size=(1920, 1080))
        display.start()
        driver = webdriver.Firefox()
        driver.get(url_filenames['url'])
        link_result_tmp = []
        text_result_tmp = []
        retry_times = 30

        for _ in range(retry_times):
            try:
                WebDriverWait(driver, timeout=120).until(
                    expected_conditions.presence_of_element_located(
                        (By.XPATH, "//div[@id='upcoming_events_card']//a")
                    )
                )
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
        else:
            links_to_events = []
            links_to_events.append(events.get_attribute('href').split("?")[0])

        # UPDATE EVENT LINKS FILE
        with open(url_filenames['links_file'], 'r+') as db:
            db_links = db.read()
            for link in links_to_events:
                if link not in db_links:
                    link_result_tmp.append(link)
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

        with open(url_filenames['text_file'], 'r+') as db:
            db_text = db.read()
            for text_event in text_list:
                if text_event not in db_text:
                    text_result_tmp.append(text_event)
                    db.seek(0)
                    db.write(text_event + db_text)
                    db_text = db.read()

        link_result.append(link_result_tmp)
        text_result.append(text_result_tmp)

        driver.close()

        processes_to_kill = [
            "firefox-esr",
            "Xvfb",
            "geckodriver"
        ]
        for process in processes_to_kill:
            Popen(['killall', process])

    return_text = True
    for links_tmp, text_tmp in zip(link_result, text_result):
        if len(links_tmp) != len(text_tmp):
            return_text = False
            break

    # return list of lists (one for each event type)
    if return_text:
        return link_result, text_result
    else:
        return link_result, None

if __name__ == '__main__':
    main()
