#Imports
import requests
import pandas as pd
from bs4 import BeautifulSoup

def extract_data(soup):
    data = []
    players = []
    #Extracting player information
    #The table uses either class odd or even on the player lines
    players.append(soup.find_all('tr', {'class' : 'odd'}))
    players.append(soup.find_all('tr', {'class' : 'even'}))
    print(players)


    for player in players:
        new_data = extract(player)
        data.append(new_data)

    #Creating a new table and adding data
    df = pd.DataFrame(data=data, columns=["Name", "Player_id", "Position", "Age", "Nationality", "Transfer from", "Transfer to", "Transfer date", "Transfer type"])
    return df

def extract(players):
    new_data = []
    # Adding name to table
    name = players.find('img', {'class' : 'bilderrahmen-fixed lazy lazy'})['alt']
    new_data.append(name)

    # Adding transfermarkt id to the table
    player_id = players.find('a', {'title' : name})['href'].split('/')[4]
    new_data.append(player_id)

    # Adding position to table 
    position = players.find_all('td', {'class' : ''})[2].text
    new_data.append(position)

    # Adding age to table
    age = players.find('td', {'class' : 'zentriert'}).text
    new_data.append(age)

    # Adding nationality
    firNat = players.find('img', {'class' : 'flaggenrahmen'})['title']
    new_data.append(firNat)

    # Adding transfer club from
    clubFrom = players.find('img', {'class' : 'tiny_wappen'})['alt']
    new_data.append(clubFrom)

    # Adding transfer club to
    clubTo = players.find_all('img', {'class' : 'tiny_wappen'})[1]['alt']
    new_data.append(clubTo)

    # Adding transfer date
    transferDate = players.find_all('td', {'class' : 'zentriert'})[2].text
    new_data.append(transferDate)

    # Adding transfer type/fee
    transferType = players.find_all('td' , {'class' : 'rechts hauptlink'})[0].text
    new_data.append(transferType)
    print(new_data) 
    return new_data



def export_data(df):
    #Export to json/csv
    try:
        df.to_csv('Latest Transfer.csv', index = False)

        df.to_json('Latest transfers.json',orient="index")
    except:
        print("Error exporting data")


def main():
    #Extracting half the data to a list
    url=(f"https://www.transfermarkt.com/transfers/neuestetransfers/statistik?ajax=yw1&land_id=0&maxMarktwert=200000000&minMarktwert=0&plus=1&wettbewerb_id=alle&page=1")
    # Make a GET request to fetch the raw HTML content
    html_content = requests.get(url, headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}).text 
    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")
    df = extract_data(soup)
    export_data(df)

if __name__ == "__main__":
    main()