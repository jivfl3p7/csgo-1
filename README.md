# csgo analytics
This project is designed to rate professional Counter Strike: Global Offensive (CSGO) teams using data from [HLTV.org](http://www.hltv.org/). The goal of this project is to develop ratings that are both descriptive and predictive of team performances.

The professional CSGO scene has teams compete in both online and LAN (in-person) events but for this project we will just focus on results from international LAN events with at least one team from the [HLTV.org World Rankings](https://www.hltv.org/ranking/teams/2017/july/10) competeting.

Below is the process that is executed by the `csgo.bat` batch file:


### 1. scraping `python\hltv_scrape.py`
- *Scrape historical HLTV.org World Rankings*
- *Scrape match data from events where at least one participating team is in the most recent world ranking (relative to the start of the event)*


### ~~2. demo parsing `python\rar_to_csv.py`~~
~~Note: parsing data from the HLTV demos requires an external tool~~
- ~~*Convert zipped demo files to `.dem` files*~~
- ~~*Use external parsing tool to log match events (e.g. gun buy, player death, bomb plant) into json files*~~
- ~~*Convert events from json into usable match data and store in csv files*~~

### ~~3. match demo to hltv `python\team_name_match.py`~~
- ~~*Utilize fuzzy matching functions in python to match HLTV team names to demo team names*~~

### 4. database creation `sql\...`
If it does not exist, create a local db called `esports`. Next, the schema `csgo` is created where all of the csv files above are loaded into.

### 5. calculate team ratings `r\step_explore.py` (WIP)
- *Utilize the Stephenson Rating System in the [PlayerRatings package](https://cran.r-project.org/web/packages/PlayerRatings/PlayerRatings.pdf) to calculate team ratings by map and output results into local postgresql db*
