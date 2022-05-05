# Imports
import json
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup
def extract_information():
    url = (
            f"https://www.transfermarkt.com/najeeb-yakubu/profil/spieler/543493")
    # Make a GET request to fetch the raw HTML content
    html_content = requests.get(url, headers={
                                    'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}).text
    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")

    first_name, last_name = extract_name(soup)
    full_name, age, date_of_birth, foot, nationality, loaned_club, current_club, contract_length = extract_personal_information(soup)
    main_position, other_positions = extract_position(soup)
    career_history(soup)

def extract_name(soup):
    first_name = soup.find('h1', {'class': 'data-header__headline-wrapper'}).text
    last_name = soup.find('h1', {'class': 'data-header__headline-wrapper'}).find('strong').text
    return first_name, last_name

def extract_nationalities():
    counter = 0  # Reset the counter to 0

def extract_personal_information(soup):
    player_data = soup.find('div', {'class': 'info-table info-table--right-space'}).find_all('span')  # Finds all player data
    counter = 0  # Reset the counter to 0
    full_name = "Null"
    date_of_birth = "Null"
    age = "Null"
    foot = "Null"
    current_club = "Null"
    loaned_club = "Null"
    nationality = []
    date_joined = "Null"
    contract_length = "Null"

    for i in player_data:
        if i.text == "Name in home country:":
            full_name = player_data[counter+1].text
        elif i.text == "Joined:":
            date_joined = player_data[counter+1].text
        elif i.text == "Contract expires:":
            contract_length = player_data[counter+1].text
        elif i.text == "Date of birth:":
            date_of_birth = player_data[counter+1].text
        elif i.text == "Age:":
            age = player_data[counter+1].text
        elif i.text == "Foot:":
            foot = player_data[counter+1].text
        elif i.text == "Current club:":
            current_club = player_data[counter+1].text
        elif i.text == "Loaned from:":
            loaned_club = player_data[counter+1].text
        elif i.text == "Citizenship":
            nationality.append(player_data[counter+1].text)
        counter += 1

    return full_name, age, date_of_birth, foot, nationality, loaned_club, current_club, contract_length


def career_history(soup): # Extract all information from the player's career history
    pass


def international_history(soup): # Extracts all information from the player's international history
    pass


def extract_position(soup):
    player_data = soup.find('div', {'class': 'detail-position__box'}).find_all('div', {'class': 'detail-position__position'})
    main_position = player_data[0].text
    other_positions = []
    for player in range(1, len(player_data)):
        other_positions.append(player_data[player].text)
    return main_position, other_positions

if __name__ == "__main__":
    extract_information()