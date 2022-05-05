# Get background from player/staff profiles. Possibly AI upscale to full HD as well. mac range = 1009050
# Imports
import re

import requests
from bs4 import BeautifulSoup
import selenium
from selenium.webdriver.common.keys import Keys


def change_to_gallery(id):
    driver = webdriver.Firefox()
    driver.get("http://www.python.org")
    assert "Python" in driver.title
    elem = driver.find_element_by_name("q")


def make_list():
    players = []

    url = f"https://www.transfermarkt.com/oyvind-knutsen/profil/spieler/250981"
    html_content = requests.get(url, headers={
        'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}).text
    soup = BeautifulSoup(html_content, "lxml")

    print(soup.find_all('div', {'id': 'svelte-performance-data'}))

def getinput():
    regex = r"[0-9]"
    while True:
        id = input("Write FM UID: ")
        if re.match(id, regex):
            return id

if __name__ == "__main__":
    # id = getinput()
    change_to_gallery(1)
    make_list() # Add id