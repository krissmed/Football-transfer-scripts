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
    competition_urls = ['https://www.transfermarkt.com/wettbewerbe/europa/wettbewerbe',
                        'https://www.transfermarkt.com/wettbewerbe/asien',
                        'https://www.transfermarkt.com/wettbewerbe/amerika',
                        'https://www.transfermarkt.com/wettbewerbe/afrika'
                        ]
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


def check_if_transfer(soup):
    is_transfer = False
    for subnav in soup.find_all("a", {"class": "tm-subnav-item megamenu_drop"}):
        if subnav.text == "Transfers":
            is_transfer = True
    return is_transfer


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
    first_transfers = []
    for url in comp_urls:
        print(f"[PROCESSING] Building list of all transferred players {counter}/{len(comp_urls)}")
        soup = create_bs4_object(url)
        if check_if_transfer(soup) is False or soup.find('tr', {'class': 'odd'}) is None:
            continue
        print(f"[Processing] Running on url: {url}")
        new_first_transfer = extract(soup.find('tr', {'class': 'odd'}), url)
        new_first_transfer.insert(0, url)
        first_transfers.append(new_first_transfer)
        counter += 1
    print(f'[PROCESSING] Found {len(player_list)} players')
    return first_transfers, player_list


def extract(player, url):
    name = player.find('img', {'class': 'bilderrahmen-fixed'})['alt']

    tfm_player_id = player.find('a', {'title': name})['href'].split('/')[4]

    club_to = player.find_all('img', {'class': 'tiny_wappen'})[1]['alt']

    if club_to == "Retired" or club_to == "Career break":
        club_to_tfm_id = "Null"
    else:
        club_to_tfm_id = player.find('a', {'title': club_to})['href'].split('/')[4]

    club_from = player.find('img', {'class': 'tiny_wappen'})['alt']

    if club_from == "Retired" or club_from == "Career break":
        club_from_tfm_id = "Null"
    else:
        club_from_tfm_id = player.find('a', {'title': club_from})[
            'href'].split('/')[4]

    transfer_date = player.find_all('td', {'class': 'zentriert'})[2].text

    age = player.find_all('td', {'class': 'zentriert'})[1].text

    fir_nat = player.find_all('img', {'class': 'flaggenrahmen'})[0]['title']

    if len(player.find_all('img', {'class': 'flaggenrahmen'})) > 3:
        sec_nat = player.find_all('img', {'class': 'flaggenrahmen'})[1]['title']
    else:
        sec_nat = "Null"

    transfer_type = player.find_all('td', {'class': 'rechts hauptlink'})[0].text

    position, date_joined, contract_length, full_name = getting_player_details(
        player, name)

    return[tfm_player_id, name, full_name, position, age, fir_nat, sec_nat, club_from, club_from_tfm_id, club_to,
           club_to_tfm_id, transfer_date, transfer_type, date_joined.strip(), contract_length.strip()]


def getting_player_details(player, name):
    soup = create_bs4_object("https://www.transfermarkt.com"+player.find('a', {"title": name})['href'])
    player_data = soup.find('div', {'class': ['info-table info-table--right-space',
                                              'info-table info-table--right-space min-height-audio']}).find_all('span')

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
        elif i.text == "Position:":
            position = player_data[counter + 1].text
        counter += 1

    return position.strip(), date_joined.strip(), contract_length, full_name


def export_data(df):  # Export to json or csv
    if not os.path.exists("../Output"):
        os.mkdir("../Output")
    df.to_csv('../Output/latest_transfers.csv', index=False)

    df.to_json('../Output/latest_transfers.json', orient="records")


if __name__ == "__main__":
    comp_urls = get_competition_urls()
    first_transfer, player_list = make_list_of_players(comp_urls)
    print(first_transfer)
    df = pd.DataFrame(data=first_transfer,
                      columns=["Url", "Player_id", "Name", "Full Name", "Position", "Age", "Nationality",
                               "Second Nationality", "From club", "From club id", "To club", "To club id",
                               "Tranfer date", "Fee", "Date joined", "Contract expiry date"])
    export_data(df)

# Todo
# H??ndter edge-case hvor det ikke er noen transfers