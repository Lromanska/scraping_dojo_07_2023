from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import json
import os
import time

tags_prefix_len = 6


def find(browser, by, element):
    try:
        return browser.find_element(by, element)
    except NoSuchElementException:
        print(f"{element} not found")
        return None


def find_next_url(root):
    nav = find(root, By.XPATH, "//nav")
    if not nav:
        return None

    pager = find(nav, By.CLASS_NAME, 'pager')
    if not pager:
        return None

    next_btn = find(pager, By.CLASS_NAME, "next")
    if not next_btn:
        return None

    a = next_btn.find_element(By.TAG_NAME, "a")
    final_url = a.get_attribute("href")
    return final_url


def scrape_quotes(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('window-size=1920x1080')
    all_quotes = []
    with webdriver.Chrome(options=chrome_options) as driver:
        while url:
            print(f"Scraping url: {url}")
            driver.get(url)
            time.sleep(10)
            res = driver.page_source
            print(res)
            soup = BeautifulSoup(res, "html.parser")

            quotes = soup.find_all(class_="quote")

            for quote in quotes:
                parsed_quote = {
                    "text": quote.find(class_="text").get_text().replace("\u201c", "").replace("\u201d", ""),
                    "by": quote.find(class_="author").get_text(),
                    "tags": quote.find(class_="tags").get_text()[tags_prefix_len:].split()
                }
                print(parsed_quote)
                all_quotes.append(parsed_quote)

            url = find_next_url(driver)
    return all_quotes


def save_quotes_as_json(quotes, output_file):
    with open(output_file, 'w') as outfile:
        json.dump(quotes, outfile)


if __name__ == '__main__':
    load_dotenv()
    output_file = os.getenv("OUTPUT_FILE")
    url = os.getenv("INPUT_URL")

    all_quotes = scrape_quotes(url)

    save_quotes_as_json(all_quotes, output_file)


