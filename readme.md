# Transfermarkt-scripts

[![Verify transfers script](https://github.com/krissmed/Transfermarkt-scripts/actions/workflows/Get_transfers.yml/badge.svg)](https://github.com/krissmed/Transfermarkt-scripts/actions/workflows/Get_transfers.yml)
[![Update FM ids](https://github.com/krissmed/Transfermarkt-scripts/actions/workflows/Update%20FM%20ids.yml/badge.svg)](https://github.com/krissmed/Transfermarkt-scripts/actions/workflows/Update%20FM%20ids.yml)
[![Verify contract script](https://github.com/krissmed/Transfermarkt-scripts/actions/workflows/Get_extensions.yml/badge.svg)](https://github.com/krissmed/Transfermarkt-scripts/actions/workflows/Get_extensions.yml)

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
- [ ] Add loan return date to output (for latest_transfers)
- [ ] Add future transfer script
- [ ] Add managerial changes script
- [ ] Add background extractor from transfermarkt
