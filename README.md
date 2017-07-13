# csgo analytics
This project is designed to rate professional Counter Strike: Global Offensive (CSGO) teams using data from [HLTV.org](http://www.hltv.org/). The goal of this project is to develop ratings that are both descriptive and predictive of team performances.

The professional CSGO scene has teams compete in both online and LAN (in-person) events but for this project we will just focus on results from international LAN events with at least one team from the [HLTV.org World Rankings](https://www.hltv.org/ranking/teams/2017/july/10) competeting.

Below is the process that is executed by the `csgo.bat` batch file:


### 1. scraping (python)
* `hltv_scrape_teamrank.py` - *Gather historical HLTV.org World Rankings*
* `hltv_scrape_event.py` - *Log basic info from international LAN events that contain at least one ranked team*
* `hltv_scrape_match.py` - *For events from step 2, gather match info (teams, vetos, maps, results, etc.)*
* `hltv_scrape_demo.py` - *Scrape match demos for possible future use*
Info from the first three scripts below are scraped into csv files.

### 2. demo parsing (python)
Note: parsing data from the HLTV demos requires an external tool and the data from these demos is not currently being utilized for the rankings.
* `rar_to_demo.py` - *Convert zipped demo files to `.dem` files*
* `demo_to_json.py` - *Use external parsing tool to log match events (e.g. gun buy, player death, bomb plant) into json files*
* `json_to_csv.py` - *Convert events from json into usable match data and stored in csv files*
* `team_name_match.py` - *Utilize fuzzy matching functions in python to match HLTV team names to demo team names*

### 3. database creation (postgresql)
If it does not exist, create a local db called `esports`. Next, the schema `csgo` is created where all of the csv files above are loaded into.

### 4. calculate team ratings (R)
* `steph.R` - *Utilize the Stephenson Rating System in the [PlayerRatings package](https://cran.r-project.org/web/packages/PlayerRatings/PlayerRatings.pdf) to calculate team ratings by map and output into local postgresql db*
