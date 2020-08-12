from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
from time import sleep

DOMAIN = "https://mangalivre.net" 

URL = DOMAIN + "/manga/boku-no-hero-academia/1319" 

browser = webdriver.Chrome(ChromeDriverManager().install())

def scroll_to_end():
    previous_height = browser.execute_script("return document.body.scrollHeight")
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(2)
    current_height = browser.execute_script("return document.body.scrollHeight")
    if previous_height != current_height:
        scroll_to_end()

def get_chapter_list():
    browser.get(URL)
    scroll_to_end()
    elem = browser.find_element_by_xpath("//div/ul[@class='full-chapters-list list-of-chapters']")
    return elem.get_attribute('outerHTML')


def parse_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    a_tags = soup.find_all('a', href=True)
    links = [a['href'] for a in a_tags if a['href'].startswith('/ler')]
    return links


html_content = get_chapter_list()
links = parse_html(html_content)

print(links)

browser.close()