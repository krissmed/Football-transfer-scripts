#Imports
from logging import exception
import requests
import pandas as pd
from bs4 import BeautifulSoup


def make_list(): # Returns a list of all players
    players = []
    # Runs through all pages
    for i in range(1, 11):
        url=(f"https://www.transfermarkt.com/transfers/neuestetransfers/statistik?ajax=yw1&land_id=0&maxMarktwert=200000000&minMarktwert=0&plus=1&wettbewerb_id=alle&page=1")
        # Make a GET request to fetch the raw HTML content
        html_content = requests.get(url, headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}).text 
        # Parse the html content
        soup = BeautifulSoup(html_content, "lxml")
        for player in soup.find_all('tr', {'class' : 'odd'}):
            players.append(player)

        for player in soup.find_all('tr', {'class' : 'even'}):
            players.append(player)
                
    return players


def extract_data(players): # Returns a dataframe of all players
    data = []
    counter = 1
    for player in players:
        new_data = extract(player)
        print(f"[Added player] {Counter}/{len(players)}")
        counter += 1
        data.append(new_data)

    df = pd.DataFrame(data=data, columns=["Name", "Player_id", "Position", "Age", "Nationality", "Transfer from", "Transfer to", "Transfer date", "Transfer fee", "Contract Expiry Date", "Date Joined"])
    return df


def extract(player): # Extracts data from a player
    new_data = []
    # Adding name to table
    name = player.find('img', {'class' : 'bilderrahmen-fixed lazy lazy'})['alt']
    new_data.append(name)

    # Adding transfermarkt id to the table
    player_id = player.find('a', {'title' : name})['href'].split('/')[4]
    new_data.append(player_id)

    # Adding position to table 
    position = player.find_all('td', {'class' : ''})[2].text
    new_data.append(position)

    # Adding age to table
    age = player.find('td', {'class' : 'zentriert'}).text
    new_data.append(age)

    # Adding nationality
    firNat = player.find('img', {'class' : 'flaggenrahmen'})['title']
    new_data.append(firNat)

    # Adding transfer club from
    clubFrom = player.find('img', {'class' : 'tiny_wappen'})['alt']
    new_data.append(clubFrom)

    # Adding transfer club to
    clubTo = player.find_all('img', {'class' : 'tiny_wappen'})[1]['alt']
    new_data.append(clubTo)

    # Adding transfer date
    transferDate = player.find_all('td', {'class' : 'zentriert'})[2].text
    new_data.append(transferDate)

    # Adding transfer type/fee
    transferType = player.find_all('td' , {'class' : 'rechts hauptlink'})[0].text
    new_data.append(transferType)

    # Adding contract length
    date_joined, contract_length = Contract_length(player, name)
    new_data.append(date_joined.strip())
    new_data.append(contract_length.strip())


    return new_data


def Contract_length(player, name):
    # Adding transfermarkt id to the table
    url = (f"http://www.transfermarkt.com{player.find('a', {'title' : name})['href']}")
    html_content = requests.get(url, headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}).text 
    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")
    player_data_list = soup.find_all('span', {'class': 'info-table__content info-table__content--bold'})
    player_data_index = soup.find_all('span', {'class': 'info-table__content info-table__content--regular'})

    counter = 0

    for i in player_data_index: # Finds the joined date
        if i.text == "Joined:":
            date_joined = player_data_list[counter].text
            break
        counter += 1

    counter = 0 # Reset the counter
    for i in player_data_index: # Finds the contract expiry date
        if i.text == "Contract expires:":
            contract_length = player_data_list[counter].text
            break
        counter += 1

    return date_joined, contract_length


def export_data(df): #Export to json or csv
    try:
        df.to_csv('Output.csv', index = False)

        df.to_json('Output.json',orient="index")
    except Exception as e:
        print(e)


def main():
    players = make_list()
    df = extract_data(players)
    export_data(df)


if __name__ == "__main__":
    main()