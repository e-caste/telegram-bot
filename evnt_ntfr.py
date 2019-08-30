#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from time import sleep
from subprocess import Popen
from sys import stderr, platform
import os
from robbamia import *

if platform.startswith('darwin'):
    DEBUG = True
else:
    DEBUG = False

if DEBUG:
    from selenium.webdriver.firefox.options import Options
else:
    from pyvirtualdisplay import Display


def main():
    # print("Current wd: " + os.getcwd())
    os.chdir(raspi_wd)
    # print("Current wd: " + os.getcwd())
    link_result = []
    text_result = []

    urls = [
        'SupermarketTorino',
        'cerclemusic',
        'thedreamersrec'
    ]

    prefixes = [
        'supermarket',
        'cercle',
        'thedreamers'
    ]

    if len(urls) != len(prefixes):
        print("Check urls and prefixes.", file=stderr)
        return

    # make list of dicts
    urls_filenames = []
    for url, prefix in zip(urls, prefixes):
        urls_filenames.append({
            'url': 'https://www.facebook.com/pg/' + url + '/events/?ref=page_internal',
            'links_file': prefix + '_events_links.txt',
            'text_file': prefix + '_events.txt'
        })

    for url_filenames in urls_filenames:
        if DEBUG:
            options = Options()
            options.add_argument('--headless')
            driver = webdriver.Firefox(options=options)
        else:
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
                        # (By.XPATH, "//div[@id='upcoming_events_card']//a")
                        (By.XPATH, "//div[@id='upcoming_events_card']")
                    )
                )
                upcoming_events_card = driver.find_element_by_id('upcoming_events_card')
                events = upcoming_events_card.find_elements_by_xpath('descendant::a')
                break
            except Exception as e:
                # print(e)  # printing 30 times is too verbose
                sleep(0.5)

        try:
            links_to_events = []
            if isinstance(events, list):
                for event in events:
                    link = event.get_attribute('href').split("?")[0]
                    # a facebook event link is only made of digits, discard any link with letters
                    if not any(c.isalpha() for c in link[:-1].split("/")[-1]):
                        links_to_events.append(link)
            else:
                link = events.get_attribute('href').split("?")[0]
                # a facebook event link is only made of digits, discard any link with letters
                if not any(c.isalpha() for c in link[:-1].split("/")[-1]):
                    links_to_events.append(link)

        # no new events were found at a url, try with next one
        except UnboundLocalError as ule:
            print("No new events found at " + url_filenames['url'], file=stderr)
            print("Continuing...", file=stderr)
            continue

        # UPDATE EVENT LINKS FILE
        with open(url_filenames['links_file'], 'r') as db:
            db_links = db.read()
        with open(url_filenames['links_file'], 'a') as db:
            for link in links_to_events:
                if link not in db_links:
                    link_result_tmp.append(link)
                    db.write(link + "\n")
                    print("Found new event at " + url_filenames['url'])


        # ALSO UPDATE EVENT DETAILS FILE
        # TODO: add separation of events by recognizing dates with a regex
        text_list = []
        if upcoming_events_card.text.count("Get Tickets") == 1:
            full_text = upcoming_events_card.text.split("Share Events\n")[1].split("·")[0] + \
                        upcoming_events_card.text.split("guests")[1].split("Get Tickets")[0]
            text_list.append(full_text)
        else:
            try:
                text_list_with_guest_numbers = upcoming_events_card.text.split("Share Events\n")[1].split("Get Tickets")
                for item in text_list_with_guest_numbers:
                    text_list.append(item.split("·")[0] + item.split("guests")[1])
            except IndexError as ie:
                # print(ie, file=stderr)
                print("Only sending links because there is no Get Tickets button...", file=stderr)

        with open(url_filenames['text_file'], 'r') as db:
            db_text = db.read()
        with open(url_filenames['text_file'], 'a') as db:
            for text_event in text_list:
                if text_event not in db_text:
                    text_result_tmp.append(text_event)
                    db.write(text_event + "\n")

        link_result.append(link_result_tmp)
        text_result.append(text_result_tmp)

        driver.close()
        if not DEBUG:
            display.stop()

        processes_to_kill = [
            "firefox-esr",
            "Xvfb",
            "geckodriver"
        ]
        if not DEBUG:
            for process in processes_to_kill:
                Popen(['killall', process])

        if not DEBUG:
            sleep(10) # after each event url

    return_text = True
    for links_tmp, text_tmp in zip(link_result, text_result):
        if len(links_tmp) != len(text_tmp):
            return_text = False
            break

    if DEBUG:
        print(link_result)
        print(text_result)
    # return list of lists (one for each event type)
    else:
        if return_text:
            return link_result, text_result, prefixes
        else:
            return link_result, None, prefixes

if __name__ == '__main__':
    main()
