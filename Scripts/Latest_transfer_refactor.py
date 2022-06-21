# Imports
import json
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup


def create_bs4_object(url):
    html_content = requests.get(url, headers={
        'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}).text
    soup = BeautifulSoup(html_content, "lxml")
    return soup


def get_competition_urls():
    print('[PROCESSING] Building list of all competitions')
    competition_urls = ['https://www.transfermarkt.com/wettbewerbe/europa/wettbewerbe', 'https://www.transfermarkt.com/wettbewerbe/asien', 'https://www.transfermarkt.com/wettbewerbe/amerika', 'https://www.transfermarkt.com/wettbewerbe/afrika']
    transfer_urls = []
    for url in competition_urls:
        page_number = 1
        active = True
        while active:
            soup = create_bs4_object(url + f'?page={page_number}')
            remaining_rows_odd, remaining_rows_even, active = check_for_valid_url(soup)
            insertion_point = (page_number * 25) + 1  # Output the list as it is on the website
            if active is False:
                for row in remaining_rows_odd:
                    transfer_urls.append(add_to_urllist(row.find_all('a')[1]))

                for row in remaining_rows_even:
                    transfer_urls.append(add_to_urllist(row.find_all('a')[1]))
                break
            for player in soup.find_all('tr', {'class': 'odd'}):
                transfer_urls.append(add_to_urllist(player.find_all('a')[1]))

            for player in soup.find_all('tr', {'class': 'even'}):
                transfer_urls.insert(insertion_point, add_to_urllist(player.find_all('a')[1]))
                insertion_point += 2  # Calculate the next insertion point
            page_number += 1
    print(f'[PROCESSING] Found {len(transfer_urls)} competitions')
    return transfer_urls


def add_to_urllist(player_object):
    link = f"https://www.transfermarkt.com{player_object['href']}/plus/1"
    link = link.replace("startseite", "letztetransfers")
    return link


def check_for_valid_url(soup):
    for row in soup.find_all('td', {'class': 'extrarow bg_blau_20 hauptlink'}):
        if row.text == "Domestic Cup":
            remaining_rows_odd = row.find_all_previous('tr', {'class': 'odd'})
            remaining_rows_even = row.find_all_previous('tr', {'class': 'even'})
            return remaining_rows_odd, remaining_rows_even, False
    return [], [], True


def make_list_of_players(comp_urls):
    counter = 0
    player_list = []
    for url in comp_urls:
        print(f"[PROCESSING] Building list of all transferred players {counter}/{len(comp_urls)}")
        soup = create_bs4_object(url)
        for player in soup.find_all('tr', {'class': 'odd'}):
            check_last_transfer(url, player)
            player_list.append(player)
            print(f"[PROCESSING] Added player to list (Total: {len(player_list)})")
        for player in soup.find_all('tr', {'class': 'even'}):
            player_list.append(player)
            print(f"[PROCESSING] Added player to list (Total: {len(player_list)})")
        counter += 1
    print(f'[PROCESSING] Found {len(player_list)} players')


def check_last_transfer(url, player):
    if LAST_TRANSFER == player:
        return False



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
    df = pd.DataFrame(data=data, columns=["Player_id", "Name", "Full Name", "Position", "Age", "Nationality",
                                          "Second Nationality",
                      "From club", "From club id", "To club", "To club id", "Tranfer date", "Fee", "Date joined",
                                          "Contract expiry date"])
    print(data)x
    return df


# def extract(player):
#     name = player.find('img', {'class': 'bilderrahmen-fixed'})['alt']
#     print(name)
#     tfm_player_id = player.find('a', {'title': name})['href'].split('/')[4]
#
#     return [tfm_player_id, name, full_name, position, age, fir_nat, sec_nat, club_from, club_from_tfm_id,
#             club_to, club_to_tfm_id, transfer_date, transfer_type, date_joined.strip(), contract_length.strip()]


def get_last_transfer(player_id, clubFrom_id, clubTo_id):
    global last_transfer



def debug(string):
    return f"[DEBUG] {string}"


if __name__ == "__main__":
    #last_transfer = get_last_id()
    comp_urls = get_competition_urls()
    player_list = make_list_of_players(comp_urls)
    df = extract_data(player_list)
