# Imports
from logging import exception
import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import os


def make_list():  # Returns a list of all players
    players = []
    # Runs through all pages
    for i in range(1, 8):
        url = (
            f"https://www.transfermarkt.com/transfers/letztevertragsverlaengerungen/statistik?plus=1&&page={i}")
        # Make a GET request to fetch the raw HTML content
        html_content = requests.get(url, headers={
                                    'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}).text
        # Parse the html content
        soup = BeautifulSoup(html_content, "lxml")
        # Loops through half the players
        for player in soup.find_all('tr', {'class': 'odd'}):
            players.append(player)

        # Calculates the position to make a 1:1 list form transfermarkt
        counter = ((i-1)*25)+1

        # Loops through the other half players
        for player in soup.find_all('tr', {'class': 'even'}):
            players.insert(counter, player)  # Insert in the correct position
            counter += 2

    return players


def extract_data(players):  # Returns a dataframe with all transfer data
    data = []
    counter = 1
    for player in players:  # Loops through all players
        new_data = extract(player)
        if new_data is False:  # If the player is already in the list, break the loop
            break
        print(f"[Added player] {counter}/{len(players)}")
        counter += 1
        data.append(new_data)  # Adds new data to the complete list

    df = pd.DataFrame(data=data, columns=["Player_id", "Name", "Full Name", "Position", "Age", "Nationality", "Second Nationality",
                      "To club", "To club id", "Option", "Date signed", "New contract expiry date"])
    return df


def extract(player):  # Extracts data from the table
    new_data = []
    # Extracting name
    name = player.find('img', {'class': 'bilderrahmen-fixed lazy lazy'})['alt']

    # Extracting transfermarkt player id
    player_id = player.find('a', {'title': name})['href'].split('/')[4]

    # Extracting position
    position = player.find_all('td', {'class': ''})[2].text

    # Extracting age
    age = player.find('td', {'class': 'zentriert'}).text

    # Extracting first nationality
    firNat = player.find_all('img', {'class': 'flaggenrahmen'})[0]['title']

    # Extracting second nationality
    if len(player.find_all('img', {'class': 'flaggenrahmen'})) > 3:
        secNat = player.find_all('img', {'class': 'flaggenrahmen'})[1]['title']
    else:
        secNat = "Null"

    # Extracting new club
    new_club = player.find_all('td', {'class': 'hauptlink'})[
        1].find('a')['title']

    # Extracting new_club id
    if new_club == "Retired" or new_club == "Career break":
        new_club_id = "Null"
    else:
        new_club_id = player.find('a', {'title': new_club})[
            'href'].split('/')[4]

    new_contract_signed = player.find_all('td', {'class': 'zentriert'})[3].text

    new_contract_length = player.find(
        'td', {'class': 'zentriert hauptlink'}).text

    option = player.find_all('td', {'class': 'zentriert'})[2].text

    if last_output is not False:
        # Checks if the player is already in the list
        if check_last_extension(player_id, new_club_id, new_contract_signed, new_contract_length) == False:
            return False  # If the player is already in the list, return false

    full_name = getting_player_details(
        player.find_all('td', {'class': 'hauptlink'})[
            0].find('a')['href'])  # Getting player details form player profile

    # Adding data to list
    new_data.append(player_id)
    new_data.append(name)
    new_data.append(full_name)
    new_data.append(position)
    new_data.append(age)
    new_data.append(firNat)
    new_data.append(secNat)
    new_data.append(new_club)
    new_data.append(new_club_id)
    new_data.append(option)
    new_data.append(new_contract_signed)
    new_data.append(new_contract_length)

    return new_data


# Gets the player details from the player profile
def getting_player_details(player_link):
    url = (
        f"https://www.transfermarkt.com{player_link}")
    html_content = requests.get(url, headers={
                                'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}).text
    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")

    # Extract lists of all player details
    player_data_list = soup.find_all('span', {
                                     'class': 'info-table__content info-table__content--bold'})  # Finds all player data
    player_data_index = soup.find_all('span', {
                                      'class': 'info-table__content info-table__content--regular'})  # Finds all player data index

    counter = 0  # Starts tbe counter at 0

    # Loops through all player details
    for i in player_data_index:
        if i.text == "Name in home country:":  # Checks if the player has a full name listed
            full_name = player_data_list[counter].text
            break
        else:
            full_name = "Null"
        counter += 1

    return full_name


def export_data(df):  # Export to json or csv
    try:
        if not os.path.exists("../Output"):
            os.mkdir("../Output")
        df.to_csv('../Output/Contract_extensions.csv', index=False)

        df.to_json('../Output/Contract_extensions.json', orient="index")
    except Exception as e:
        print(e)

  # Checks whether the player is already listed


def check_last_extension(player_id, new_club_id, new_contract_signed, new_contract_length):
    if [player_id, new_club_id, new_contract_signed, new_contract_length] == last_output:
        return False
    else:
        return True


def get_last_id():
    if os.path.isfile('../Output/Contract_extensions.json'):  # Checks if the file exists
        f = open('../Output/Contract_extensions.json')
        data = json.load(f)
        if len(data) > 0:
            return [data['0']['Player_id'], data['0']['To club id'], data['0']['Date signed'], data['0']['New contract expiry date']]


last_transfer = False

if __name__ == "__main__":
    last_output = get_last_id()
    players = make_list()
    df = extract_data(players)
    if len(df.index) == 0:  # Doesn't write a new file if there is no new data
        print("[ERROR] No new contract extensions")
    else:
        export_data(df)
