# -*- coding: utf-8 -*-
"""
Created on Sat Jun 10 21:03:49 2017

@author: wesso
"""

import pandas as pd
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def team_name_match():
    hltv_match_teams = pd.read_csv('csv\\hltv_matches.csv', header = None)[[1,4,5,6,7]]
    demo_teams = pd.read_csv('csv\\match_pistol_results.csv', header = None)[[0,2]]
    
    team_matchid, team_hltv, team_demo, team_match_score = [],[],[],[]
    for index, row in hltv_match_teams.iterrows():
        matchid = re.compile('(?<=matches\/)[0-9]{1,}(?=\/)').search(row[1]).group(0)
        demo_team_names = set(demo_teams.loc[demo_teams[0].str.contains(matchid),2])
        if len(demo_team_names) == 2:
            if process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[1] == 100:
                team_matchid.append(matchid)
                team_hltv.append(row[4])
                team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[0])
                team_match_score.append(100)
                team_matchid.append(matchid)
                team_hltv.append(row[6])
                team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names - {process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[0]}), scorer = fuzz.partial_ratio)[0])
                team_match_score.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names - {process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[0]}), scorer = fuzz.partial_ratio)[1])
            elif process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[1] == 100:
                team_matchid.append(matchid)
                team_hltv.append(row[6])
                team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[0])
                team_match_score.append(100)
                team_matchid.append(matchid)
                team_hltv.append(row[4])
                team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names - {process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[0]}), scorer = fuzz.partial_ratio)[0])
                team_match_score.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names - {process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[0]}), scorer = fuzz.partial_ratio)[1])
            elif process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[1] > 90:
                team_matchid.append(matchid)
                team_hltv.append(row[4])
                team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[0])
                team_match_score.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[1])
                team_matchid.append(matchid)
                team_hltv.append(row[6])
                team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names - {process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[0]}), scorer = fuzz.partial_ratio)[0])
                team_match_score.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names - {process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[0]}), scorer = fuzz.partial_ratio)[1])
            elif process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[1] > 90:
                team_matchid.append(matchid)
                team_hltv.append(row[6])
                team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[0])
                team_match_score.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[1])
                team_matchid.append(matchid)
                team_hltv.append(row[4])
                team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names - {process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[0]}), scorer = fuzz.partial_ratio)[0])
                team_match_score.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names - {process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[0]}), scorer = fuzz.partial_ratio)[1])
            else:
                if process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[1] > 70:
                    team_matchid.append(matchid)
                    team_hltv.append(row[4])
                    team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[0])
                    team_match_score.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[4]), list(demo_team_names), scorer = fuzz.partial_ratio)[1])
                if process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[1] > 70:
                    team_matchid.append(matchid)
                    team_hltv.append(row[6])
                    team_demo.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[0])
                    team_match_score.append(process.extractOne(re.sub(r'[^\x00-\x7F]+','',row[6]), list(demo_team_names), scorer = fuzz.partial_ratio)[1])
                    
    team_name_match = pd.DataFrame(
        {'matchid': team_matchid,
         'team_hltv': team_hltv,
         'team_demo': team_demo,
         'team_match_score': team_match_score
        })
    
    team_name_match = team_name_match.drop_duplicates().sort_values('team_hltv').reset_index(drop = True)
    
    with open('csv\\team_name_match.csv', 'wb') as namecsv:
        team_name_match[['team_hltv','team_demo','team_match_score']].drop_duplicates().sort_values('team_hltv').reset_index(drop = True).to_csv(namecsv, header = False, index = False)