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
    for i in range(1, 11):
        url = (f"https://www.transfermarkt.com/transfers/neuestetransfers/statistik?land_id=0&wettbewerb_id=alle&minMarktwert=0&maxMarktwert=200000000&plus={i}")
        # Make a GET request to fetch the raw HTML content
        html_content = requests.get(url, headers={
                                    'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}).text
        # Parse the html content
        soup = BeautifulSoup(html_content, "lxml")
        for player in soup.find_all('tr', {'class': 'odd'}):
            players.append(player)
        counter = 1

        for player in soup.find_all('tr', {'class': 'even'}):
            players.insert(counter, player)
            counter += 2

    return players


def extract_data(players):  # Returns a dataframe of all players
    data = []
    counter = 1
    for player in players:
        new_data = extract(player)
        if new_data is False:
            break
        print(f"[Added player] {counter}/{len(players)}")
        counter += 1
        data.append(new_data)

    df = pd.DataFrame(data=data, columns=["Player_id", "Name", "Full Name", "Position", "Age", "Nationality", "Second Nationality",
                      "From club", "From club id", "To club", "To club id", "Tranfer date", "Fee", "Date joined", "Contract expiry date"])
    return df


def extract(player):  # Extracts data from a player
    new_data = []
    # Adding name to table
    name = player.find('img', {'class': 'bilderrahmen-fixed lazy lazy'})['alt']

    # Adding transfermarkt id to the table
    player_id = player.find('a', {'title': name})['href'].split('/')[4]

    # Adding position to table
    position = player.find_all('td', {'class': ''})[2].text

    # Adding age to table
    age = player.find('td', {'class': 'zentriert'}).text

    # Adding first nationality
    firNat = player.find_all('img', {'class': 'flaggenrahmen'})[0]['title']

    # Adding second nationality
    if len(player.find_all('img', {'class': 'flaggenrahmen'})) > 3:
        secNat = player.find_all('img', {'class': 'flaggenrahmen'})[1]['title']
    else:
        secNat = "Null"

    # Adding transfer club from
    clubFrom = player.find('img', {'class': 'tiny_wappen'})['alt']

    # Adding club from id
    if clubFrom == "Retired" or clubFrom == "Career break":
        clubFrom_id = "Null"
    else:
        clubFrom_id = player.find('a', {'title': clubFrom})[
        'href'].split('/')[4]

    # Adding transfer club to
    clubTo = player.find_all('img', {'class': 'tiny_wappen'})[1]['alt']

    # Adding clubTo id
    if clubTo == "Retired" or clubTo == "Career break":
        clubTo_id = "Null"
    else:
        clubTo_id = player.find('a', {'title': clubTo})['href'].split('/')[4]

    # Adding transfer date
    transferDate = player.find_all('td', {'class': 'zentriert'})[2].text

    # Adding transfer type/fee
    transferType = player.find_all('td', {'class': 'rechts hauptlink'})[0].text

    if last_transfer is not False:
        # Checks if the player is already in the list
        if check_last_transfer(player_id, clubFrom_id, clubTo_id) == False:
            return False  # If the player is already in the list, return false¨

    date_joined, contract_length, full_name = getting_player_details(
        player, name)  # Getting player details form player profile

    # Adding data to list
    new_data.append(player_id)
    new_data.append(name)
    new_data.append(full_name)
    new_data.append(position)
    new_data.append(age)
    new_data.append(firNat)
    new_data.append(secNat)
    new_data.append(clubFrom)
    new_data.append(clubFrom_id)
    new_data.append(clubTo)
    new_data.append(clubTo_id)
    new_data.append(transferDate)
    new_data.append(transferType)
    new_data.append(date_joined.strip())
    new_data.append(contract_length.strip())

    return new_data


def getting_player_details(player, name):
    # Adding transfermarkt id to the table
    # URL to player profile
    url = (
        f"http://www.transfermarkt.com{player.find('a', {'title' : name})['href']}")
    html_content = requests.get(url, headers={
                                'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}).text
    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")
    player_data_list = soup.find_all('span', {
                                     'class': 'info-table__content info-table__content--bold'})  # Finds all player data
    player_data_index = soup.find_all('span', {
                                      'class': 'info-table__content info-table__content--regular'})  # Finds all player data index
    counter = 0  # Starts tbe counter at 0

    for i in player_data_index:
        if i.text == "Name in home country:":
            full_name = player_data_list[counter].text
            break
        else:
            full_name = "Null"
        counter += 1

    counter = 0  # Reset the counter to 0

    for i in player_data_index:  # Finds the joined date
        if i.text == "Joined:":  # If the index is "Joined:"
            # The date joined is the next "Joined:"
            date_joined = player_data_list[counter].text
            break  # Stop looking for the joined date
        counter += 1

    counter = 0  # Reset the counter to 0

    for i in player_data_index:  # Finds the contract expiry date
        if i.text == "Contract expires:":
            # The contract length is the next "Contract expires:"
            contract_length = player_data_list[counter].text
            break  # Stop looking for the contract length
        counter += 1

    return date_joined, contract_length, full_name


def export_data(df):  # Export to json or csv
    try:
        df.to_csv('Latest_transfers.csv', index=False)

        df.to_json('Latest_transfers.json', orient="index")
    except Exception as e:
        print(e)


# Removes players that are already in the list
def check_last_transfer(player_id, clubFrom_id, clubTo_id):
    if [player_id, clubFrom_id, clubTo_id] == last_transfer:
        return False
    else:
        return True


last_transfer = False


def get_last_id():
    if os.path.isfile('Latest_transfers.json'):  # Checks if the file exists
        f = open('Latest_transfers.json')
        data = json.load(f)
        if len(data) > 0:
            return [data[str(0)]['Player_id'], data[str(0)]['From club id'], data[str(0)]['To club id']]


if __name__ == "__main__":
    last_transfer = get_last_id()
    players = make_list()
    df = extract_data(players)
    export_data(df)
