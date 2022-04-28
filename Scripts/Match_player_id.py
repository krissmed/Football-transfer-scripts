# Match tranfermarkt id against susie id
# Imports
import csv
import os
import requests
import numpy as np
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
    tfm_id_return = []
    fm_id_return = []
    for player in players:
        tfm_id = player.find(
            'a', {'class': 'small text-dark'})['href'].split("/")
        fm_id = player.find(
            'h5', {'class': 'flex-fill m-0'}).find('a')['href'].split("/")

        tfm_id_return.append(tfm_id[tfm_id.index('profil')+2])
        fm_id_return.append(fm_id[-1])
    return tfm_id_return, fm_id_return


def merge_lists(tfm_id, fm_id, csvfile):
    df = pd.read_csv(f"../Repo/{str(csvfile)}.csv")
    data = []
    for i in range(len(df['Football Manager ID'].tolist())):
        new_line = []
        new_line.append(df['Football Manager ID'][i])
        new_line.append(df['Transfermarkt ID'].tolist()[i])
        data.append(new_line)
    for i in range(len(tfm_id)):
        new_line = []
        new_line.append(fm_id[i])
        new_line.append(tfm_id[i])
        data.append(new_line)

    df = pd.DataFrame(data=data, columns=['Football Manager ID', 'Transfermarkt ID']).drop_duplicates()
    return df


def output_to_csv(df, file):
    df.to_csv(f'../Repo/{str(file)}.csv', index=False)

    df.to_json(f'../Repo/{str(file)}.json', orient="index")


if __name__ == "__main__":
    player_list, staff_list = make_list()
    if len(player_list) > 0:
        tfm_id, fm_id = match_ids(player_list)
        data = merge_lists(tfm_id, fm_id, 'Player')
        output_to_csv(data, 'Player')
    if len(staff_list) > 0:
        tfm_id, fm_id = match_ids(staff_list)
        data = merge_lists(tfm_id, fm_id, 'Staff')
        output_to_csv(data, 'Staff')
