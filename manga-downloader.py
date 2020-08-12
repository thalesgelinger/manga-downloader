from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from time import sleep
from PIL import Image
import json
import requests
import os
import img2pdf

DOMAIN = "https://mangalivre.net" 

URL = DOMAIN + "/manga/solo-leveling/7702" 

options = Options()
options.headless = True
browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)

def scroll_to_end():
    previous_height = browser.execute_script("return document.body.scrollHeight")
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(2)
    current_height = browser.execute_script("return document.body.scrollHeight")
    if previous_height != current_height:
        scroll_to_end()

def get_chapter_list():
    print("Getting chapters list...")
    browser.get(URL)
    scroll_to_end()
    elem = browser.find_element_by_xpath("//div/ul[@class='full-chapters-list list-of-chapters']")
    return elem.get_attribute('outerHTML')


def parse_links(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    a_tags = soup.find_all('a', href=True)
    links = [a['href'] for a in a_tags if a['href'].startswith('/ler')]
    return [ DOMAIN + link for link in links]


def read_chapters(links):
    print("Reading chapters")

    pages = []

    links.sort()
    

    for link in links:
        splitted_link = link.split('/')
        title = splitted_link[4]
        chapter = splitted_link[7]
        

        if os.path.isdir(f"mangas/{title}/{chapter}"):
            print(f"Already downloaded {title} {chapter}")
            continue

        browser.get(link)
        current_page = browser.execute_script("return document.querySelector('div.page-navigation > span > em:nth-child(1)').innerText")
        total_pages = browser.execute_script("return document.querySelector('div.page-navigation > span > em:nth-child(2)').innerText")
        
        print(f"Downloading from {link}")

        for i in range(int(current_page), int(total_pages) + 1):
            img_html = browser.find_element_by_xpath("//div[@class='manga-image']/img").get_attribute('outerHTML')
            img_soup = BeautifulSoup(img_html, "html.parser").find('img')
            pages.append(img_soup["src"])
            browser.find_element_by_xpath("//div[@class='page-next']").click()
            sleep(3)
        download_pages(title, chapter, pages)
        convert_to_pdf(title, chapter)

def download_pages(title, chapter, pages):

    print(f"Dowloading {title} {chapter}")

    if not os.path.isdir(f"mangas/{title}/{chapter}"):
        os.makedirs(f"mangas/{title}/{chapter}")

    for page in pages:
        img = requests.get(page)
        page_name = page.split('/')[-1]
        with open(f"mangas/{title}/{chapter}/{page_name}", 'wb') as f:
            f.write(img.content, )
    return title, chapter

def convert_to_pdf(title, chapter):

    print(f"Converting {title} {chapter} to PDF")

    if not os.path.isdir(f"mangas/{title}/PDFs"):
        os.makedirs(f"mangas/{title}/PDFs")

    images = []

    img_list = os.listdir(f"mangas/{title}/{chapter}")

    img_list.sort(key=lambda item:item.split('.')[:1])

    for img in img_list:
        img_open = Image.open(f"mangas/{title}/{chapter}/{img}")
        img_open = img_open.convert('RGB')
        images.append(img_open)     

    images[0].save(f"mangas/{title}/PDFs/{chapter}.pdf",save_all=True, append_images=images[1:])

html_content = get_chapter_list()
links = parse_links(html_content)
read_chapters(links)

print("Done!")

browser.close()