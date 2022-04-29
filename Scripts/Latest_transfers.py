# Imports
import json
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup


def make_list():  # Returns a list of all players
    players = []
    # Runs through all pages
    for i in range(1, 11):
        url = (
            f"https://www.transfermarkt.com/transfers/neuestetransfers/statistik/plus/?plus=1&galerie=0&wettbewerb_id="
            f"alle&land_id=&minMarktwert=0&maxMarktwert=200.000.000&yt0=Show&&page={i}")
        # Make a GET request to fetch the raw HTML content
        html_content = requests.get(url, headers={
                                    'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                                                  '(KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}).text
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

    df = pd.DataFrame(data=data, columns=["Player_id", "Fm_id", "Name", "Full Name", "Position", "Age", "Nationality",
                                          "Second Nationality",
                      "From club", "From club id", "To club", "To club id", "Tranfer date", "Fee", "Date joined",
                                          "Contract expiry date"])
    print(data)
    return df


def extract(player):  # Extracts data from a player
    # Adding name to table
    name = player.find('img', {'class': 'bilderrahmen-fixed lazy lazy'})['alt']

    # Adding transfermarkt id to the table
    tfm_player_id = player.find('a', {'title': name})['href'].split('/')[4]

    fm_player_id = get_fm_id(tfm_player_id, 'player')


    # Adding position to table
    position = player.find_all('td', {'class': ''})[2].text

    # Adding age to table
    age = player.find('td', {'class': 'zentriert'}).text

    # Adding first nationality
    fir_nat = player.find_all('img', {'class': 'flaggenrahmen'})[0]['title']

    # Adding second nationality
    if len(player.find_all('img', {'class': 'flaggenrahmen'})) > 3:
        sec_nat = player.find_all('img', {'class': 'flaggenrahmen'})[1]['title']
    else:
        sec_nat = "Null"

    # Adding transfer club from
    club_from = player.find('img', {'class': 'tiny_wappen'})['alt']

    # Adding club from id
    if club_from == "Retired" or club_from == "Career break":
        club_from_tfm_id = "Null"
    else:
        club_from_tfm_id = player.find('a', {'title': club_from})[
            'href'].split('/')[4]

    # club_from_fm_id = get_fm_id(club_from_tfm_id, 'team')

    # Adding transfer club to
    club_to = player.find_all('img', {'class': 'tiny_wappen'})[1]['alt']

    # Adding club_to id

    if club_to == "Retired" or club_to == "Career break":
        club_to_tfm_id = "Null"
    else:
        club_to_tfm_id = player.find('a', {'title': club_to})['href'].split('/')[4]

    # club_to_fm_id = get_fm_id(club_to_tfm_id, 'team')


    # Adding transfer date
    transfer_date = player.find_all('td', {'class': 'zentriert'})[2].text

    # Adding transfer type/fee
    transfer_type = player.find_all('td', {'class': 'rechts hauptlink'})[0].text

    if last_transfer is not False:
        # Checks if the player is already in the list
        if not check_last_transfer(tfm_player_id, club_from_tfm_id, club_to_tfm_id):
            return False  # If the player is already in the list, return false¨

    date_joined, contract_length, full_name = getting_player_details(
        player, name)  # Getting player details form player profile

    return [tfm_player_id, fm_player_id, name, full_name, position, age, fir_nat, sec_nat, club_from, club_from_tfm_id,
            club_to, club_to_tfm_id, transfer_date, transfer_type, date_joined.strip(), contract_length.strip()]

def get_fm_id(id, file):
    df = pd.read_csv(f"../Repo/{file}.csv")
    tfm_id = df['Transfermarkt ID'].tolist()
    fm_id = df['Football Manager ID'].tolist()
    for i in range(len(tfm_id)):
        if id == tfm_id[i]:
            return fm_id[i]

    return False


def getting_player_details(player, name):
    # Adding transfermarkt id to the table
    # URL to player profile
    url = (
        f"http://www.transfermarkt.com{player.find('a', {'title' : name})['href']}")
    html_content = requests.get(url, headers={
                                'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}).text
    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")
    player_data = soup.find('div', {
                                     'class': 'info-table info-table--right-space'}).find_all('span')  # Finds all player data

    counter = 0  # Reset the counter to 0
    full_name = "Null"
    date_joined = "Null"
    contract_length = "Null"

    for i in player_data:
        if i.text == "Name in home country:":
            full_name = player_data[counter+1].text
        elif i.text == "Joined:":
            date_joined = player_data[counter+1].text
        elif i.text == "Contract expires:":
            contract_length = player_data[counter+1].text
        counter += 1

    return date_joined, contract_length, full_name


def export_data(df):  # Export to json or csv
    if not os.path.exists("../Output"):
        os.mkdir("../Output")
    df.to_csv('../Output/Latest_transfers.csv', index=False)

    df.to_json('../Output/Latest_transfers.json', orient="index")


# Removes players that are already in the list
def check_last_transfer(player_id, clubFrom_id, clubTo_id):
    if [player_id, clubFrom_id, clubTo_id] == last_transfer:
        return False
    else:
        return True

def internal_transfer(player):
    # If team id are connected in tfm_team_ids.csv --> Do not output
    # Check for internal transfer Man U U23 --> Man U Reserves
    pass


def get_last_id():
    if os.path.isfile('../Output/Latest_transfers.json'):  # Checks if the file exists
        f = open('../Output/Latest_transfers.json')
        data = json.load(f)
        if len(data) > 0:
            return [data[str(0)]['Player_id'], data[str(0)]['From club id'], data[str(0)]['To club id']]
        else:
            return False
    else:
        return False


if __name__ == "__main__":
    last_transfer = get_last_id()
    players = make_list()
    df = extract_data(players)
    if len(df.index) == 0:  # Doesn't write a new file if there is no new data
        print("[ERROR] No new transfers")
    else:
        export_data(df)