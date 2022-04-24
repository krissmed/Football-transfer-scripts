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
        for player in soup.find_all('tr', {'class': 'odd'}):
            players.append(player)

        counter = ((i-1)*25)+1

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
                      "To club", "To club id", "Option", "Date signed", "New contract expiry date"])
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

    # Adding transfer club to
    clubTo = player.find_all('td', {'class': 'hauptlink'})[
        1].find('a')['title']
    # Adding clubTo id
    if clubTo == "Retired" or clubTo == "Career break":
        clubTo_id = "Null"
    else:
        clubTo_id = player.find('a', {'title': clubTo})['href'].split('/')[4]

    new_contract_signed = player.find_all('td', {'class': 'zentriert'})[3].text

    new_contract_length = player.find(
        'td', {'class': 'zentriert hauptlink'}).text

    option = player.find_all('td', {'class': 'zentriert'})[2].text

    if last_output is not False:
        # Checks if the player is already in the list
        if check_last_extension(player_id, clubTo_id, new_contract_signed, new_contract_length) == False:
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
    new_data.append(clubTo)
    new_data.append(clubTo_id)
    new_data.append(option)
    new_data.append(new_contract_signed)
    new_data.append(new_contract_length)

    return new_data


def getting_player_details(player_id):
    # Adding transfermarkt id to the table
    # URL to player profile
    url = (
        f"https://www.transfermarkt.com{player_id}")
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

    return full_name


def export_data(df):  # Export to json or csv
    try:
        df.to_csv('Contract_extensions.csv', index=False)

        df.to_json('Contract_extensions.json', orient="index")
    except Exception as e:
        print(e)


# Removes players that are already in the list
def check_last_extension(player_id, clubFrom_id, new_contract_signed, new_contract_length):
    if [player_id, clubFrom_id, new_contract_signed, new_contract_length] == last_output:
        return False
    else:
        return True


last_transfer = False


def get_last_id():
    if os.path.isfile('Contract_extensions.json'):  # Checks if the file exists
        f = open('Contract_extensions.json')
        data = json.load(f)
        if len(data) > 0:
            return [data['0']['Player_id'], data['0']['To club id'], data['0']['Date signed'], data['0']['New contract expiry date']]


if __name__ == "__main__":
    last_output = get_last_id()
    players = make_list()
    df = extract_data(players)
    if len(df.index) == 0:  # Doesn't write a new file if there is no new data
        print("[ERROR] No new contract extensions")
    else:
        export_data(df)
