# Transfermarkt-scripts
[![match_player_id](https://github.com/krissmed/Transfermarkt-scripts/actions/workflows/Update%20FM%20ids.yml/badge.svg)](https://github.com/krissmed/Transfermarkt-scripts/actions/workflows/Update%20FM%20ids.yml)<br>
A collection of scripts used to scrape last transfers and last contract extensions on transfermarkt.com
## Usage
### Prerequisites
```bash
pip install -r requirements.txt
```
### Running
```bash
python Contract_extensions.py
python Latest_transfers.py
```
### Output
Once output is generated, the data is stored in a csv file and a json file under the output folder. 

## Roadmap
- [ ] Match Transfermarkt team ids and Football Manager team ids
- [ ] Sort dataframes before output
