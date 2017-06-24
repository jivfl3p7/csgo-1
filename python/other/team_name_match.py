import pandas as pd
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def team_name_match():
    hltv_match_teams = pd.read_csv('csv\\hltv_matches.csv', header = None)[[1,4,5,6,7]]
    demo_teams = pd.read_csv('csv\\demo_players.csv', header = None)[[0,3]].drop_duplicates()
    
    team_matchid, teamid_hltv, team_hltv, team_demo, team_match_score = [],[],[],[],[]
    for index, row in hltv_match_teams.iterrows():
        matchid = re.compile('(?<=matches\/)[0-9]{1,}(?=\/)').search(row[1]).group(0)
        demo_team_names = set(demo_teams.loc[demo_teams[0].str.contains(matchid),3])
        if len(demo_team_names) == 2:
            if process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[1] == 100:
                team_matchid.append(matchid)                
                team_hltv.append(row[4])
                teamid_hltv.append(list(hltv_match_teams.loc[hltv_match_teams[4] == row[4],5])[0])
                team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[0])
                team_match_score.append(100)
                team_matchid.append(matchid)
                team_hltv.append(row[6])
                teamid_hltv.append(list(hltv_match_teams.loc[hltv_match_teams[6] == row[6],7])[0])
                team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names - {process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[0]}), scorer = fuzz.partial_ratio)[0])
                team_match_score.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names - {process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[0]}), scorer = fuzz.partial_ratio)[1])
            elif process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[1] == 100:
                team_matchid.append(matchid)
                team_hltv.append(row[6])
                teamid_hltv.append(list(hltv_match_teams.loc[hltv_match_teams[6] == row[6],7])[0])
                team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[0])
                team_match_score.append(100)
                team_matchid.append(matchid)
                team_hltv.append(row[4])
                teamid_hltv.append(list(hltv_match_teams.loc[hltv_match_teams[4] == row[4],5])[0])
                team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names - {process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[0]}), scorer = fuzz.partial_ratio)[0])
                team_match_score.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names - {process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[0]}), scorer = fuzz.partial_ratio)[1])
            elif process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[1] > 85:
                team_matchid.append(matchid)
                team_hltv.append(row[4])
                teamid_hltv.append(list(hltv_match_teams.loc[hltv_match_teams[4] == row[4],5])[0])
                team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[0])
                team_match_score.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[1])
                team_matchid.append(matchid)
                team_hltv.append(row[6])
                teamid_hltv.append(list(hltv_match_teams.loc[hltv_match_teams[6] == row[6],7])[0])
                team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names - {process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[0]}), scorer = fuzz.partial_ratio)[0])
                team_match_score.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names - {process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[0]}), scorer = fuzz.partial_ratio)[1])
            elif process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[1] > 85:
                team_matchid.append(matchid)
                team_hltv.append(row[6])
                teamid_hltv.append(list(hltv_match_teams.loc[hltv_match_teams[6] == row[6],7])[0])
                team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[0])
                team_match_score.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[1])
                team_matchid.append(matchid)
                team_hltv.append(row[4])
                teamid_hltv.append(list(hltv_match_teams.loc[hltv_match_teams[4] == row[4],5])[0])
                team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names - {process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[0]}), scorer = fuzz.partial_ratio)[0])
                team_match_score.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names - {process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[0]}), scorer = fuzz.partial_ratio)[1])
            else:
                if process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[1] > 70:
                    team_matchid.append(matchid)
                    team_hltv.append(row[4])
                    teamid_hltv.append(list(hltv_match_teams.loc[hltv_match_teams[4] == row[4],5])[0])
                    team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[0])
                    team_match_score.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[1])
                if process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[1] > 70:
                    team_matchid.append(matchid)
                    team_hltv.append(row[6])
                    teamid_hltv.append(list(hltv_match_teams.loc[hltv_match_teams[6] == row[6],7])[0])
                    team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[0])
                    team_match_score.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[1])
                    
    team_name_match = pd.DataFrame(
        {'matchid': team_matchid,
         'teamid_hltv': teamid_hltv,
         'team_hltv': team_hltv,
         'team_demo': team_demo,
         'team_match_score': team_match_score
        })
    
    team_name_match = team_name_match.drop_duplicates().sort_values('team_hltv').reset_index(drop = True)
    
    with open('csv\\team_name_index.csv', 'wb') as namecsv:
        team_name_match[['teamid_hltv','team_hltv','team_demo','team_match_score']].drop_duplicates().sort_values('teamid_hltv').reset_index(drop = True).to_csv(namecsv, header = False, index = False)