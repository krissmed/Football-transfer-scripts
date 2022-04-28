# Match tranfermarkt id against susie id
# Imports
import csv
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re


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


def merge_lists(list, csvfile):
    data = []
    df = pd.read_csv(f"../Repo/{str(csvfile)}.csv")
    fm_id_current = df['Football Manager ID'].tolist()
    tfm_id_current = df['Transfermarkt ID'].tolist()

    for i in range(len(list)):
        if list[i][0] not in fm_id_current:
            tfm_id_current.append(list[i][0])
            fm_id_current.append(list[i][1])
            print(f"[Entry added] {list[i]}")
        else:
            continue
    for i in range(len(fm_id_current)):
        new_entry = [fm_id_current, tfm_id_current]
        data.append(new_entry)
    return data


def output_to_csv(data, file):
    df = pd.DataFrame(data=data, columns=[
                      "Football Manager ID", "Transfermarkt ID"])
    df.drop_duplicates(subset='Football Manager ID')
    df['Transfermarkt ID'] = df['Transfermarkt ID'].astype(str).astype(int)
    df['Football Manager ID'] = df['Football Manager ID'].astype(str).astype(int)
    print(df.dtypes)

    df = df.sort_values(by=['Football Manager ID'])
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
