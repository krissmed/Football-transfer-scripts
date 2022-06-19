# Imports
import json
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup


def make_list():  # Returns a list of all players
    players = []
    # Runs through all pages
    url = (
        f"https://www.fotball.no/lov-og-reglement/overganger/sok-overganger/?transferCategory=Player&genderId=2")
    # Make a GET request to fetch the raw HTML content
    html_content = requests.get(url, headers={
        'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}).text
    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")
    for player in soup.find_all('li', {'class': 'grid__item one-whole'}):
        players.append(player)

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

    df = pd.DataFrame(data=data, columns=["Fotballno_id", "Name", "Full Name", "Position", "Age", "Nationality",
                                          "Second Nationality",
                                          "From club", "From club id", "To club", "To club id", "Tranfer date", "Fee",
                                          "Date joined",
                                          "Contract expiry date", "Loan end date"])
    return df


def extract(player):  # Extracts data from a player
    # Adding name to table
    name = player.find('a', {'class': 'tbl_prs_lnk'}).text
    # Adding transfermarkt id to the table
    fotballno_id = player.find('a', {'class': 'tbl_prs_lnk'})['href'].split('/')[4].replace('?fiksId=', '')

    # Adding position to table
    position = "-"
    # Adding age to table
    age = "-"
    # Adding first nationality
    fir_nat = "-"
    # Adding second nationality
    sec_nat = "-"
    # Adding transfer club from
    try:
        club_from = player.findAll('a', {'class': 'tbl_prs_lnk'})[1].text
        club_from_fotballno_id = player.findAll('a', {'class': 'tbl_prs_lnk'})[1]['href'].split('/')[4].replace('?fiksId=', '') # Fotball.no id of the club
        if "," in club_from:
            club_from = format_team_name(club_from)
    except:
        club_from = player.findAll('span', {'class': 'medium-text'})
        club_from_fotballno_id = "-"

    # Adding club from id

    # Adding transfer club to

    try:
        club_to = player.find_all('a', {'class': 'tbl_prs_lnk'})[-1].text
        club_to_fotballno_id = player.findAll('a', {'class': 'tbl_prs_lnk'})[-1]['href'].split('/')[4].replace('?fiksId=', '')
        if "," in club_to:
            club_to = format_team_name(club_to)
    except:
        club_to = player.find_all('span', {'class': 'medium-text'}[4])
        club_to_fotballno_id = ""
    # Adding transfer date
    print()
    transfer_date = player.find_all('span', {'class': 'medium-text'})[3].text.strip()

    # Adding transfer type/fee
    transfer_type = player.findAll('span', {'class': 'medium-text'})[2].text

    if last_transfer is not False:
        # Checks if the player is already in the list
        if not check_last_transfer(fotballno_id, club_from_fotballno_id, club_to_fotballno_id):
            return False  # If the player is already in the list, return false

    return fotballno_id, name, name, position, age, fir_nat, sec_nat, club_from, club_from_fotballno_id, club_to, club_to_fotballno_id, transfer_date, "-", transfer_date, "-", "-"


def format_team_name(club):
    club_temp = club.split(",")
    new_club = f"{club_temp[1]} {club_temp[0]}"
    return new_club


def export_data(df):  # Export to json or csv
    if not os.path.exists("../Output"):
        os.mkdir("../Output")
    df.to_csv('../Output/fotballno_transfers.csv', index=False)

    df.to_json('../Output/fotballno_transfers.json', orient="index")


# Removes players that are already in the list
def check_last_transfer(player_id, clubFrom_id, clubTo_id):
    if [player_id, clubFrom_id, clubTo_id] == last_transfer:
        return False
    else:
        return True


def get_last_id():
    if os.path.isfile('../Output/fotballno_transfers.json'):  # Checks if the file exists
        f = open('../Output/fotballno_transfers.json')
        data = json.load(f)
        if len(data) > 0:
            return [data[str(0)]['Fotballno_id'], data[str(0)]['From club id'], data[str(0)]['To club id']]
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
