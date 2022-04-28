# Match tranfermarkt id against susie id
# Imports
import csv
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re


def remove_duplicates():
    with open('../Repo/transfer_market_fm_ids.csv', 'r') as in_file, open('../Repo/ouput.csv', 'w') as out_file:

        seen = set()  # set for fast O(1) amortized lookup

        for line in in_file:
            if line in seen:
                continue  # skip duplicate

            seen.add(line)
            out_file.write(line)


def check_for_duplicate(tfm_id, data):
    for row in data:
        if tfm_id == row[1]:
            return True
    return False


def make_list():
    players = []
    staff = []
    # Runs through all pages
    page = 1
    pattern_player = re.compile('^.*transfermarkt.*/profil/spieler.*$')
    pattern_staff = re.compile('^.*transfermarkt.*/profil/trainer.*$')
    while True:
        print(f'Running on page {page}')
        url = (
            f"https://sortitoutsi.net/football-manager-data-update/submissions?status=enabled&page={page}")
        # Make a GET request to fetch the raw HTML content
        html_content = requests.get(url, headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}).text
        # Parse the html content
        soup = BeautifulSoup(html_content, "lxml")
        # Loops through half the players
        if len(soup.find_all('div', {'class': 'data-update-submission-box'})) == 0:
            print("breaking")
            break
        for person in soup.find_all('div', {'class': 'data-update-submission-box'}):
            if pattern_player.match(person.find('a', {'class': 'small text-dark'})['href']):
                players.append(person)
            if pattern_staff.match(person.find('a', {'class': 'small text-dark'})['href']):
                staff.append(person)
        page += 1
    print(len(players))
    print(len(staff))
    return players, staff


def extract(players):
    for player in players:
        pass


def remove_broken(data):
    with open('../Repo/transfer_market_fm_ids.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[0] == "0":
                print("Remove")
            else:
                data.append(row)


def match_ids(players):
    data = []
    for player in players:
        new_line = []
        tfm_id = player.find(
            'a', {'class': 'small text-dark'})['href'].split("/")
        fm_id = player.find(
            'h5', {'class': 'flex-fill m-0'}).find('a')['href'].split("/")

        new_line.append(tfm_id[tfm_id.index('profil')+2])
        new_line.append(fm_id[-1])
        data.append(new_line)
    print(data)
    return data


def export_data(df):  # Export to json or csv
    try:
        if not os.path.exists("../Index"):
            os.mkdir("../Index")
        df.to_csv('../Output/player_index.csv', index=False)
    except Exception as e:
        print(e)


def open_playerindex():
    df = pd.read_csv("../Repo/player.csv")
    fm_id_current = df['Football_Manager_id'].tolist()
    tfm_id_current = df['Transfermarkt_id'].tolist()
    return fm_id_current, tfm_id_current


def sort_complete_csv():
    # After output, the csv should be sorted to make it easier to naivgate. Preferably by fm_id
    pass


def merge_lists(list, csvfile):
    data = []
    df = pd.read_csv(f"../Repo/{csvfile}.csv")
    fm_id_current = df['Football_Manager_id'].tolist()
    tfm_id_current = df['Transfermarkt_id'].tolist()

    for i in range(len(list)):
        if list[i][0] in fm_id_current:
            tfm_id_current.append(list[i][0])
            fm_id_current.append(list[i][1])
            print(f"[Entry added] {list[i]}")
        else:
            continue
    for i in range(len(fm_id_current)):
        new_entry = [tfm_id_current, fm_id_current]
        data.append(new_entry)
    return data


def output_to_csv(data, file):
    df = pd.DataFrame(data=data, columns=[
                      "Transfermarkt_id", "Football_Manager_id"])
    df.drop_duplicates(subset='Football_Manager_id')
    df['Transfermarkt_id'] = df['Transfermarkt_id'].astype(str).astype(int)
    df['Football_Manager_id'] = df['Football_Manager_id'].astype(str).astype(int)
    print(df.dtypes)

    df = df.sort_values(by=['Football_Manager_id'])
    print(df)

    df.to_csv(f'../Repo/{file}.csv', index=False)

    df.to_json(f'../Repo/{file}.json', orient="index")


if __name__ == "__main__":
    player_list, staff_list = make_list()
    if len(player_list) > 0:
        players = match_ids(player_list)
        data = merge_lists(players, 'Player')
        output_to_csv(players, 'Player')
    if len(staff_list) > 0:
        staff = match_ids(staff_list)
        data = merge_lists(staff, 'Staff')
        output_to_csv(staff, 'Staff')
