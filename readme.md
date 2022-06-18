# Transfermarkt-scripts

[![Verify transfers script](https://github.com/krissmed/Transfermarkt-scripts/actions/workflows/Get_transfers.yml/badge.svg)](https://github.com/krissmed/Transfermarkt-scripts/actions/workflows/Get_transfers.yml)
[![Update FM ids](https://github.com/krissmed/Transfermarkt-scripts/actions/workflows/Update%20FM%20ids.yml/badge.svg)](https://github.com/krissmed/Transfermarkt-scripts/actions/workflows/Update%20FM%20ids.yml)
[![Verify contract script](https://github.com/krissmed/Transfermarkt-scripts/actions/workflows/Get_extensions.yml/badge.svg)](https://github.com/krissmed/Transfermarkt-scripts/actions/workflows/Get_extensions.yml)
[![Verify Fotball.no](https://github.com/krissmed/Transfermarkt-scripts/actions/workflows/Fotball.no.yml/badge.svg)](https://github.com/krissmed/Transfermarkt-scripts/actions/workflows/Fotball.no.yml)

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
- [ ] Add future transfer script (https://www.transfermarkt.com/bundesliga/transfers/wettbewerb/L1/plus/?saison_id=2022&s_w=&leihe=3&intern=0)
- [ ] Add staff changes script (https://www.transfermarkt.com/bundesliga/trainerwechsel/wettbewerb/L1)
- [ ] Add background extractor from transfermarkt (Links only)
- [ ] Refactor to pull from each league individually
- [ ] Refactor to stop pulling list when transfer is already listed
