from __future__ import division
from pyunpack import Archive
import os
import pandas as pd
import numpy as np
import re
import csv
import subprocess
import getpass
import urllib2
import math
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 \
    Safari/537.36'}
    
scraped_match_info = pd.read_csv('csv\\hltv_match_info.csv', header = None)
    
matches_w_demos = scraped_match_info.loc[pd.isnull(scraped_match_info[2]) == False]
matches_w_demos.loc[:,8] = matches_w_demos.loc[:,0].apply(lambda x: re.compile('(?<=events\/)[0-9]*(?=\/)').search(x).group(0))
matches_w_demos.loc[:,9] = matches_w_demos.loc[:,1].apply(lambda x: re.compile('(?<=matches\/)[0-9]*(?=\/)').search(x).group(0))

zipped_folder = 'E:\\CSGO Demos\\zipped'
unzipped_folder = 'E:\\CSGO Demos\\unzipped'
json_folder = 'E:\\CSGO Demos\\json'

parse_string1 = 'cd C:\\Users\\' + getpass.getuser() + '\\Documents\\GitHub\\dem2json && node dem2json.js '

weapon_data = pd.read_csv('csv\\weapon_info.csv')

def rar_download():
    print('### Rars ###')
    
    
    prev_event = None
    
    for eventid in set(matches_w_demos.loc[:,8]):
        if not os.path.exists(zipped_folder + '\\' + eventid):
                os.makedirs(zipped_folder + '\\' + eventid)
        
        if len(os.listdir(zipped_folder + '\\' + eventid)) < len(matches_w_demos.loc[matches_w_demos[8] == eventid,9]):
            for matchid in set(matches_w_demos.loc[matches_w_demos[8] == eventid,9]):
                if not (matchid + '.rar') in os.listdir(zipped_folder + '\\' + eventid):
                    if not prev_event == matches_w_demos.loc[matches_w_demos[8] == eventid,0].iloc[0]:
                        print(matches_w_demos.loc[matches_w_demos[8] == eventid,0].iloc[0])
                        prev_event = matches_w_demos.loc[matches_w_demos[8] == eventid,0].iloc[0]
                    
                    try:
                        match_row = matches_w_demos.loc[matches_w_demos[9] == matchid,:].iloc[0]
                        demo_url = 'https://www.hltv.org' + match_row[2]
                        req = urllib2.Request(demo_url,headers = header)
                        response = urllib2.urlopen(req)
                        read = response.read()
                        with open(zipped_folder + '\\' + eventid + '\\' + matchid + '.rar', 'wb+') as file_:
                            file_.write(read)
                        file_.close()
                        print('\t' + match_row[1])
                    except:
                        with open(zipped_folder + '\\' + eventid + '\\' + matchid + '.rar', 'wb+') as file_:
                            file_.write('')
                        file_.close()
                        print('\tFAIL - ' + match_row[1])
rar_download()

def rar_to_demo():
    print('### Demos ###')
    
    prev_event = None
    
    for eventid in os.listdir(zipped_folder):
        for matchid in os.listdir(zipped_folder + '\\' + eventid):
            if not os.path.exists(unzipped_folder + '\\' + eventid + '\\' + matchid[:-4]):
                os.makedirs(unzipped_folder + '\\' + eventid + '\\' + matchid[:-4])
                match_row = matches_w_demos.loc[matches_w_demos[9] == matchid[:-4],:].iloc[0]
                if not prev_event == match_row[0]:
                    print(match_row[0])
                    prev_event = match_row[0]
                try:
                    Archive(zipped_folder + '\\' + eventid + '\\' + matchid).extractall(unzipped_folder + '\\' + eventid + '\\'
                        + matchid[:-4])
                    print('\t' + match_row[1])
                except:
                    with open(unzipped_folder + '\\' + eventid + '\\' +  matchid[:-4] + '.dem', 'wb+') as file_:
                        file_.write('')
                    file_.close()
                    print('\tFAIL - ' + match_row[1])
                        
rar_to_demo()

def demo_to_json():
    print('### Jsons ###')
    
    prev_event = None
    
    for eventid in os.listdir(unzipped_folder):
        for matchid in os.listdir(unzipped_folder + '\\' + eventid):
            if not os.path.exists(json_folder + '\\' + eventid + '\\' + matchid):
                os.makedirs(json_folder + '\\' + eventid + '\\' + matchid)
            for root, dirs, files in os.walk(unzipped_folder + '\\' + eventid + '\\' + matchid, topdown = False):
                files = (x for x in files if x[-4:] == '.dem')
                for idx, item in enumerate(files):
                    if not os.path.exists(json_folder + '\\' + eventid + "\\" + matchid + "\\" + matchid + "-" + str(idx) + ".json"):
                        match_row = matches_w_demos.loc[matches_w_demos[9] == matchid,:].iloc[0]
                        if not prev_event == match_row[0]:
                                print(match_row[0])
                                prev_event = match_row[0]
                        
                        parse_string2 = "\"" + unzipped_folder + '\\' + eventid + '\\' + matchid + "\\" + item + "\" > "
                        args = (parse_string1 + parse_string2 + "\"" + json_folder + '\\' + eventid + "\\" + matchid + "\\" + matchid
                            + "-" + str(idx) + ".json\"")
                        
                        try:
                            subprocess.check_output(args, shell = True, stderr=subprocess.STDOUT)
                            print('\t' + match_row[1])
                        except Exception as e:
                            with open(json_folder + '\\' + eventid + '\\' +  matchid + '\\' +  matchid + "-" + str(idx) + '.json',
                                      'wb+') as file_:
                                file_.write('')
                            file_.close()
                            
                            error_msg = str(e)
                            with open("csv\\json_fails.csv", 'ab') as jsonfailcsv:
                                jsonfailwriter = csv.writer(jsonfailcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                jsonfailwriter.writerow([eventid,matchid,error_msg])
                            print('\tFAIL - ' + match_row[1])

demo_to_json()

def json_to_csv():
    print('### Csvs ###')
    try:
        exist_csv = list(pd.read_csv('csv\\demo_info.csv', header = None)[2].drop_duplicates())
    except:
        exist_csv = []

    try:
        exist_tname = list(pd.read_csv('csv\\team_name_matches.csv', header = None)[0].drop_duplicates())
    except:
        exist_tname = []

    prev_event = None
    
#    import random
    for eventid in os.listdir(json_folder):
#    for eventid in random.sample(os.listdir(json_folder),30):
        for matchid in os.listdir(json_folder + '\\' + eventid):
            for file_ in os.listdir(json_folder + '\\' + eventid + '\\' + matchid):
                if file_[:-5] not in exist_csv:
                    match_row = matches_w_demos.loc[matches_w_demos[9] == file_[:-7],:].iloc[0]
                    if not prev_event == match_row[0]:
                            print(match_row[0])
                            prev_event = match_row[0]
                    try:
                        try:
                            init_data = pd.read_json(json_folder + '\\' + eventid + '\\' + matchid + '\\' + file_)
                        except:
                            with open('csv\\demo_info.csv', 'ab') as democsv:
                                demowriter = csv.writer(democsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                demowriter.writerow([match_row[1],int(file_[-6:-5]),file_[:-5],None,None,'failed json'])
                            print('\tFAIL - ' + match_row[1])
                            continue
                        
                        # test
#                        match_row = matches_w_demos.loc[matches_w_demos[9] == '2300763',:].iloc[0]
#                        init_data = pd.read_json("E:\\CSGO Demos\\json\\1958\\2300763\\2300763-0.json")
                        
                        # missing round
#                        init_data = pd.read_json("E:\\CSGO Demos\\json\\2538\\2307291\\2307291-1.json") final round adds extra point to scoreline
#                        init_data = pd.read_json("E:\\CSGO Demos\\json\\2538\\2307295\\2307295-0.json") final round adds extra point to scoreline
#                        init_data = pd.read_json("E:\\CSGO Demos\\json\\1986\\2299842\\2299842-1.json") final round adds extra point to scoreline

                        if matchid in ['2309764','2311330','2305232','2311680']:
                            raise ValueError('weird gotv demo')
                        if file_[:-5] in ['2315035-0','2315033-0']:
                            raise ValueError('too many teams in demo')
                            
                        error_msg = None
                        
                        data = pd.merge(init_data, init_data.loc[(init_data['event'] == 'player_connect')
                            & (init_data['steamid'] != 'BOT'),['userid','steamid']].drop_duplicates(), how = 'left', on = 'userid')\
                            .rename(index = str, columns = {'steamid_y':'steamid'}).reset_index(drop = True)
                            
                        clannames = data.loc[(data['clanname'] != '') & (pd.isnull(data['clanname']) == False)
                            & (data['clanname'] != '1'),['clanname']].drop_duplicates()
                        clannames['clanname'] = clannames['clanname'].apply(lambda x: 'Natus Vincere' if re.compile('na.?vi.*', re.I)
                            .search(x) else x)
                        clannames = clannames.drop_duplicates()
                        clannames['lower'] = [re.sub(r'[^\x00-\x7F]+','',x.lower()) for x in clannames['clanname']]
                        
                        hltv_teams = pd.DataFrame(match_row[range(4,8)])
                        hltv_teams.columns = range(hltv_teams.shape[1])
                        hltv_teams['lower'] = [re.sub(r'[^\x00-\x7F]+','',x.lower()) for x in hltv_teams[0]]
                        
                        if len(clannames) == 2:
                            fuzzy_match0 = process.extractOne(clannames['lower'].iloc[0], hltv_teams.loc[:,'lower'].iloc[[0,2]],
                                                              scorer=fuzz.partial_ratio)
                            fuzzy_match1 = process.extractOne(clannames['lower'].iloc[1], hltv_teams.loc[:,'lower'].iloc[[0,2]],
                                                              scorer=fuzz.partial_ratio)
                            if fuzzy_match0[1] > 65:
                                team1_href_row = hltv_teams.loc[hltv_teams['lower'] == fuzzy_match0[0]].index + 1
                                clannames.loc[clannames['lower'] == clannames['lower'].iloc[0],'team_href'] = hltv_teams.loc[team1_href_row,0].iloc[0]
                                team2_href_row = hltv_teams.loc[~hltv_teams.index.isin(team1_href_row) & (hltv_teams.index % 2 != 0),0]
                                clannames.loc[clannames['lower'] == clannames['lower'].iloc[1],'team_href'] = team2_href_row.iloc[0]
                            elif fuzzy_match1[1] > 65:
                                team1_href_row = hltv_teams.loc[hltv_teams['lower'] == fuzzy_match1[0]].index + 1
                                clannames.loc[clannames['lower'] == clannames['lower'].iloc[1],'team_href'] = hltv_teams.loc[team1_href_row,0].iloc[0]
                                team2_href_row = hltv_teams.loc[~hltv_teams.index.isin(team1_href_row) & (hltv_teams.index % 2 != 0),0]
                                clannames.loc[clannames['lower'] == clannames['lower'].iloc[0],'team_href'] = team2_href_row.iloc[0]
                            else:
                                raise ValueError('no high-level team name match')
                        else:
                            for team_name in clannames['lower']:
                                fuzzy_match = process.extractOne(team_name, hltv_teams.loc[:,'lower'].iloc[[0,2]], scorer=fuzz.partial_ratio)
                                team_href_row = hltv_teams.loc[hltv_teams['lower'] == fuzzy_match[0]].index + 1
                                clannames.loc[clannames['lower'] == team_name,'team_href'] = hltv_teams.loc[team_href_row,0].iloc[0]
                                if (fuzzy_match[1] < 65) and (matchid not in exist_tname):
                                    error_msg = 'team name match only ' + str(fuzzy_match[1])
                                    with open('csv\\team_name_matches.csv', 'ab') as teamnamecsv:
                                        teamnamewriter = csv.writer(teamnamecsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                        teamnamewriter.writerow([matchid,team_name,fuzzy_match[0],fuzzy_match[1]])
                                
                        if len(clannames['team_href'].drop_duplicates()) != 2:
                            raise ValueError('number of team names')
                            
                        data = pd.merge(data, clannames[['clanname','team_href']], how = 'left', on = 'clanname')
                        
                        players = data.loc[(data['event'] == 'player_team') & (pd.isnull(data['steamid']) == False),
                                           ['tick','side','steamid','team_href']].sort_values('tick')
                        players['team_href'] = np.where(pd.isnull(players['team_href']), 'Unknown',players['team_href'])
                        players['rank'] = players.groupby('steamid').rank(axis = 0, method = 'first')['tick']
                        players = players.loc[players['rank'] == 1,['steamid','side','team_href']].drop_duplicates()
                        for steamid in players['steamid']:
                            if len(data.loc[(data['steamid'] == steamid) & (data['event'] == 'weapon_fire')]) == 0:
                                players = players.loc[players['steamid'] != steamid]
                        if len(players) != 10:
                            raise ValueError('wrong number of players')
                        if len(players.loc[players['side'] == 3]) != 5:
                            raise ValueError('not enough players per side')
                            
                        if 'Unknown' in list(players['team_href'].drop_duplicates()):
                            try:
                                exist_team = players.loc[players['team_href'] != 'Unknown','team_href'].iloc[0]
                            except:
                                raise ValueError('no team names')
                            miss_team = clannames.loc[clannames['team_href'] != exist_team,'clanname'].iloc[0]
                            players['team_href'] = np.where(players['team_href'] == 'Unknown', miss_team, players['team_href'])
                            
                        data = pd.merge(data, players[['steamid','team_href']], how = 'left', on = 'steamid').rename(index = str,
                            columns = {'team_href':'team_href_old','team_href_y':'team_href'})
                        
                        rounds = data.loc[(data['event'] == 'round_start') | data['winner'].isin([2,3]),
                                          ['round','tick','event','winner','reason','score_ct','score_t']]\
                                          .sort_values(['tick','event'], ascending = [True,True])\
                                          .reset_index(drop = True)
                        rounds = rounds.sort_values(['tick','event'], ascending = [True,True]).reset_index(drop = True)
                                          
                        if rounds.loc[rounds['event'].str.contains('round'),'event'].iloc[0] == 'round_end':
                            rounds.loc[rounds.index.max() + 1] = [-2,0,'round_start',None,None,None,None]
                            rounds = rounds.sort_values('tick', ascending = True).reset_index(drop = True)
                            
                        rounds['winner'] = rounds['winner'].shift(-1)
                        rounds['reason'] = rounds['reason'].shift(-1)
                        rounds['next_event'] = rounds['event'].shift(-1)
                        rounds['round_decision'] = rounds['tick'].shift(-1)
                        rounds['score_ct'] = rounds['score_ct'].shift(-1)
                        rounds['score_t'] = rounds['score_t'].shift(-1)
                        rounds['round_score'] = rounds['score_t'] + rounds['score_ct']
                        rounds = rounds.loc[(rounds['event'] == 'round_start') & (rounds['next_event'] == 'round_end')
                            & (rounds['winner'] != 1),:].reset_index(drop = True).drop('next_event', axis = 1)\
                            .rename(index = str, columns = {'tick':'start'})
                        rounds['end'] = np.where(pd.isnull(rounds['start'].shift(-1)), rounds['round_decision'],
                            rounds['start'].shift(-1) - 1)
                            
                        i = 1
                        for index, row in rounds.iterrows():
                            if row['event'] == 'round_start':
                                rounds.set_value(index, 'round_raw', i)
                                i += 1
                                
                        if len(rounds) == 0:
                            raise ValueError('broken json')
                        elif len(rounds) == 1:
                            raise ValueError('only one round')
                                
                        round_type = pd.merge(data.loc[(data['event'] == 'player_hurt') & (data['weapon'] != '') & (data['health'] == 0),
                                        ['tick','weapon']], weapon_data[['weapon','primary_class']],how = 'left', on = 'weapon')\
                                        [['tick','primary_class']].drop_duplicates()
                        for index, row in rounds.iterrows():
                            round_type.loc[(round_type['tick'] >= row['start']) & (round_type['tick'] != 0)
                                & (round_type['tick'] <= row['round_decision']),'round_raw'] = row['round_raw']
                        round_type = round_type.loc[pd.isnull(round_type['round_raw']) == False]
                        round_type = pd.pivot_table(round_type.groupby(['round_raw','primary_class']).size().reset_index(),
                                                index = 'round_raw', columns = 'primary_class', aggfunc = 'sum').reset_index().fillna(0)
                        round_type.columns = round_type.columns.droplevel(0)
                        round_type['sum'] = round_type.loc[:,round_type.columns != ''].sum(axis = 1)
                        
                        rounds['plant'] = 0
                        if len(data.loc[(data['event'] == 'bomb_exploded'),['tick']]) > 0:
                            bomb_rnds = data.loc[(data['event'] == 'bomb_exploded'),['tick']]
                            for index, row in rounds.iterrows():
                                bomb_rnds.loc[(bomb_rnds['tick'] >= row['start']) & (bomb_rnds['tick'] != 0)
                                    & (bomb_rnds['tick'] <= row['end']),'round_raw'] = row['round_raw']
                        else:
                            bomb_rnds = pd.DataFrame({'round_raw':[]})
                        
                        try:
                            if rounds['round_score'].iloc[0] < 5:
                                knife_round = list(round_type.loc[(round_type['pistol'] + round_type['primary'] == 0),''])
                                if len(knife_round) > 1:
                                    error_msg = '> 1 knife round' + (', ' + error_msg if error_msg else '')
                                rounds['round_score'] = np.where(rounds['round_raw'].isin(knife_round), -1, rounds['round_score'])
                        except Exception as e:
                            if e == 'pistol':
                                raise ValueError('no pistol kills')
                            if e == 'primary':
                                print(e)
                        
                        if file_[:-5] == '2309398-0':
                            rounds = rounds.loc[rounds['round_raw'] > 10].reset_index(drop = True)
                        elif file_[:-5] == '2302683-0':
                            rounds = rounds.loc[rounds['round_raw'] > 13].reset_index(drop = True)
                        else:
                            prev_rnd = 999
                            for rnd in list(round_type.loc[(round_type['primary'] == 0) & (round_type['pistol'] > 0),'',].iloc[::-1]):
                                if (int(rnd) >= prev_rnd - 2) & (prev_rnd not in list(bomb_rnds['round_raw'])):
                                    rounds = rounds.loc[~rounds['round_raw'].isin(range(int(rnd),prev_rnd)),].reset_index(drop = True)
                                prev_rnd = int(rnd)
                            
                        rounds = rounds.loc[rounds['round_raw'].isin(round_type['']) | rounds['round_raw'].isin(bomb_rnds['round_raw'])
                            ,].reset_index(drop = True)
                                        
                        if file_[:-5] in ['2312366-1','2312069-3']:
                            rounds['round_est'] = rounds['round_score']
                        else:
                            for index, row in rounds.iterrows():
                                if row['round_score'] == -1:
                                    rounds.set_value(index, 'round_est', row['round_score'])
                                elif index not in [rounds.index.min(),rounds.index.max()]:
                                    if (row['round_score'] == rounds['round_score'].iloc[int(index) - 1] + 2)\
                                            and (row['round_score'] == rounds['round_score'].iloc[int(index) + 1]):
                                        rounds.set_value(index, 'round_est', rounds['round_score'].iloc[int(index) + 1] - 1)
                                    elif (((row['round_score'] == rounds['round_score'].iloc[int(index) - 1] + 1)
                                                or (row['round_score'] == rounds['round_score'].iloc[int(index) - 1]))
                                            and row['round_score'] == rounds['round_score'].iloc[int(index) + 1]):
                                        rounds.set_value(index, 'round_est', None)
                                    else:
                                        rounds.set_value(index, 'round_est', row['round_score'])
                                elif index == rounds.index.min():
                                    if (row['round_score'] == 1) and (rounds['round_score'].iloc[int(index) + 1] == -1)\
                                            and (rounds['round_score'].iloc[int(index) + 2] == 1):
                                        rounds.set_value(index, 'round_est', None)
                                    elif row['round_score'] == rounds['round_score'].iloc[int(index) + 1]:
                                        rounds.set_value(index, 'round_est', rounds['round_score'].iloc[int(index) + 1] - 1)
                                    elif (row['round_score'] == rounds['round_score'].iloc[int(index) + 1] - 2)\
                                            and (row['round_score'] == rounds['round_score'].iloc[int(index) + 2] - 2):
                                        rounds.set_value(index, 'round_est', row['round_score'])
                                    elif row['round_score'] != rounds['round_score'].iloc[int(index) + 1] - 1:
                                        raise ValueError('round counting error')
                                    else:
                                        rounds.set_value(index, 'round_est', row['round_score'])
                                elif index == rounds.index.max():
                                    if (row['round_score'] <= 30) and ((row['score_ct'] > 16) or (row['score_t'] > 16)):
                                        rounds.set_value(index, 'round_est', rounds['round_est'].iloc[int(index) - 1] + 1)
                                    elif row['round_score'] == rounds['round_est'].iloc[int(index) - 1]:
                                        rounds.set_value(index, 'round_est', rounds['round_score'].iloc[int(index) - 1] + 1)
                                    elif (row['round_score'] == rounds['round_score'].iloc[int(index) - 1] + 2)\
                                            and (row['round_score'] == rounds['round_score'].iloc[int(index) - 2] + 2):
                                        rounds.set_value(index, 'round_est', row['round_score'])
                                    elif row['round_score'] != rounds['round_est'].iloc[int(index) - 1] + 1:
                                        raise ValueError('round counting error')
                                    else:
                                        rounds.set_value(index, 'round_est', row['round_score'])
                        
                        drop_rounds = []
                        for index, row in rounds.iloc[:-1].iterrows():
                            if (row['round_est'] == -1) or (rounds['round_est'].iloc[int(index) - 1] == -1):
                                continue
                            else:
                                if row['round_est'] == 0 or pd.isnull(row['round_est']):
                                    drop_rounds.append(index)
                                elif (index == rounds.index.min()) and (rounds['round_est'].iloc[int(index) + 1] - row['round_est'] > 1):
                                    error_msg = 'missing round' + (', ' + error_msg if error_msg else '')
                                    raise ValueError(error_msg)
                                elif row['round_est'] - rounds['round_est'].iloc[int(index) - 1] > 1:
                                    error_msg = 'missing round' + (', ' + error_msg if error_msg else '')
                                    raise ValueError(error_msg)
                        rounds.drop(rounds.index[[drop_rounds]], inplace = True)
                                    
                        rounds = rounds.drop(['event','round','round_raw','round_score'], 1).rename(index = str,
                            columns = {'round_est':'round'}).reset_index(drop = True)
                            
                        for index, row in rounds.iterrows():
                            if row['round'] == -1:
                                rounds.set_value(index, 'phase', 'knife')
                            elif row['round'] <= 15:
                                rounds.set_value(index, 'phase', 'h1')
                            elif row['round'] <= 30:
                                rounds.set_value(index, 'phase', 'h2')
                            else:
                                rounds.set_value(index, 'phase', 'ot' + str(int(math.ceil((row['round']-30.0)/6)))
                                    + str(np.where(int(math.ceil((row['round']-30.0)/3)) % 2 == 0,'b','a')))
                        
                        first_blood = pd.DataFrame(data.loc[data['event'] == 'player_hurt','tick'].drop_duplicates().sort_values())
                        for index, row in rounds.iterrows():
                            tick = first_blood.loc[(row['start'] <= first_blood['tick'])
                                & (first_blood['tick'] <= row['round_decision']),'tick'].min()
                            rounds.set_value(index,'first_blood',tick)
                            
                        teams = data.loc[(data['event'] == 'item_purchase') | ((data['event'] == 'player_hurt') & (data['health'] == 0)),
                                         ['tick','side','team_href']].drop_duplicates()
                        for index, row in rounds.iterrows():
                            teams.loc[(teams['tick'] >= row['start']) & (teams['tick'] <= row['round_decision']),'round'] = row['round']
                        
                        teams = teams.loc[(pd.isnull(teams['round']) == False) & (teams['team_href'] != '')
                            & (pd.isnull(teams['team_href']) == False), ['round','team_href','side']].drop_duplicates()
                        for index,rnd in enumerate(set(rounds['round'])):
                            rnd_data = teams.loc[teams['round'] == rnd,['team_href','side']]
                            if rnd == -1:
                                if len(rnd_data.loc[rnd_data['side'] == 2]) > 1 or len(rnd_data.loc[rnd_data['side'] == 3]) > 1:
                                    error_msg = 'too many teams per side' + (', ' + error_msg if error_msg else '')
                                    rounds = rounds.loc[rounds['round'] != rnd]
                                if rnd_data['team_href'].nunique() < 1:
                                    error_msg = 'not enough teams per side' + (', ' + error_msg if error_msg else '')
                                    rounds = rounds.loc[rounds['round'] != rnd]
                            elif (rnd == 1) | (index == rounds.index.min()):
                                if len(rnd_data.loc[rnd_data['side'] == 2]) > 1 or len(rnd_data.loc[rnd_data['side'] == 3]) > 1:
                                    error_msg = 'too many teams per side' + (', ' + error_msg if error_msg else '')
                                    raise ValueError(error_msg)
                                if rnd_data['team_href'].nunique() < 1:
                                    error_msg = 'not enough teams per side' + (', ' + error_msg if error_msg else '')
                                    raise ValueError(error_msg)
                            elif len(rnd_data.loc[rnd_data['side'] == 2]) > 1 or len(rnd_data.loc[rnd_data['side'] == 3]) > 1:
                                error_msg = 'too many teams per side' + (', ' + error_msg if error_msg else '')
                                rounds = rounds.loc[rounds['round'] < rnd]
                                
                        rounds = pd.merge(rounds, teams.loc[teams['side'] == 3,['round','team_href']], how = 'left', on = 'round')\
                            .rename(index = str, columns = {'team_href':'ct_href'}).reset_index(drop = True)
                        rounds = pd.merge(rounds, teams.loc[teams['side'] == 2,['round','team_href']], how = 'left', on = 'round')\
                            .rename(index = str, columns = {'team_href':'t_href'}).reset_index(drop = True)
                            
                        for index, row in rounds.loc[pd.isnull(rounds['ct_href']) | pd.isnull(rounds['t_href'])].iterrows():
                            if pd.isnull(row['ct_href']):
                                if row['phase'] == rounds['phase'].iloc[int(index) + 1]:
                                    rounds.set_value(index,'ct_href',rounds['ct_href'].iloc[int(index) + 1])
                                else:
                                    rounds.set_value(index,'ct_href',rounds['t_href'].iloc[int(index) + 1])
                            if pd.isnull(row['t_href']):
                                if row['phase'] == rounds['phase'].iloc[int(index) + 1]:
                                    rounds.set_value(index,'t_href',rounds['t_href'].iloc[int(index) + 1])
                                else:
                                    rounds.set_value(index,'t_href',rounds['ct_href'].iloc[int(index) + 1])
                                    
                        for index, row in rounds.iterrows():
                            try:
                                rounds.set_value(index, 'ct_href', re.sub(r'[^\x00-\x7F]+','',str(row['ct_href'].encode('utf-8'))))
                            except:
                                rounds.set_value(index, 'ct_href', re.sub(r'[^\x00-\x7F]+','',str(row['ct_href'])))
                            try:
                                rounds.set_value(index, 't_href', re.sub(r'[^\x00-\x7F]+','',str(row['t_href'].encode('utf-8'))))
                            except:
                                rounds.set_value(index, 't_href', re.sub(r'[^\x00-\x7F]+','',str(row['t_href'])))
                            
                        for phs in set(rounds['phase']):
                            ct_teams = rounds.loc[rounds['phase'] == phs,'ct_href'].drop_duplicates()
                            t_teams = rounds.loc[rounds['phase'] == phs,'t_href'].drop_duplicates()
                            if max(len(ct_teams),len(t_teams)) > 1:
                                error_msg = 'team change within phase' + (', ' + error_msg if error_msg else '')
                                rounds = rounds.loc[rounds['phase'] != phs]
                                if len(rounds) == 0:
                                    raise ValueError('no rounds')
                        
                        item_change = data.loc[(data['event'].isin(['defuser_purchase','armor_purchase']))
                            | ((data['weapon'] != 'c4') & data['event'].isin(['item_purchase','item_pickup','item_drop']))
                            | (data['health'] == 0) | ((data['event'] == 'weapon_fire') & (data['weapon'].isin(
                                ['decoy','flashbang','molotov','smokegrenade','hegrenade','incgrenade','inferno','molotov_projectile'])))
                            & (data['tick'] >= rounds.loc[rounds['round'] != -1,'start'].min())
                            & (data['tick'] <= rounds['end'].max()),
                            ['tick','event','steamid','side','health','weapon','boughtHelmet','attacker']]
                        item_change = pd.merge(item_change, weapon_data, how = 'left', on = 'weapon')
                        item_change = item_change.loc[(item_change['health'] == 0)
                            | (~item_change['secondary_class'].isin(['knife','starter','taser'])),]
                        for index, row in rounds.iterrows():
                            item_change.loc[(item_change['tick'] >= row['start'])
                                & (item_change['tick'] <= row['end']),'round'] = row['round']
                            item_change.loc[(item_change['tick'] >= row['start'])
                                & (item_change['tick'] <= row['end']),'phase'] = row['phase']                        
                        item_change = item_change.loc[(pd.isnull(item_change['round']) == False) & (item_change['round'] != -1)]
                        item_change = item_change.sort_values(['steamid','tick','event']).reset_index(drop = True)
                        for index, row in item_change.iterrows():
                            try:
                                nextid = item_change.loc[index + 1,'steamid']
                                nextphase = item_change.loc[index + 1,'phase']
                                if (row['steamid'] == nextid) and (row['phase'] == nextphase):
                                    item_change.set_value(index,'phase_change',0)
                                else:
                                    item_change.set_value(index,'phase_change',1)
                            except:
                                item_change.set_value(index,'phase_change',1)
                        
                        item_change['life_seq'] = item_change.loc[(item_change['phase_change'] == 1)
                            | (item_change['event'] == 'player_hurt')].groupby('steamid').cumcount()
                        item_change['life_seq'] = item_change.groupby('steamid')['life_seq'].bfill().ffill()
                        item_change = item_change.sort_values(['tick','event']).reset_index(drop = True)
                        item_change['econ'] = 0

                        for steamid in list(item_change['steamid'].drop_duplicates()):
                            for life_seq in range(0,int(max(item_change['life_seq'])) + 1):
                                d,a,h,pr,pr_value,pi,pi_value,g_he,g_t,g_inc,g_fla,g_smo,g_dec = [0] * 13
                                for index,row in item_change.loc[(item_change['steamid'] == steamid)
                                                                & (item_change['life_seq'] == life_seq)].iterrows():
                                    change = 0
                                    if row['event'] == 'player_hurt':
                                        item_change.set_value(index, 'econ', -1*(pr_value + pi_value + a*650 + h*350 + g_inc*500
                                                                                 + g_smo*300 + g_he*300 + g_fla*200 + g_dec*50))
                                        if d == 1:
                                            item_change.set_value(index, 'defuse', -1)
                                        break
                                    elif row['event'] == 'defuser_purchase':
                                        if d != 1:
                                            d = 1
                                            item_change.set_value(index, 'defuse', 1)
                                    elif row['event'] == 'armor_purchase':
                                        if a != 1:
                                            if row['boughtHelmet'] == 0:
                                                a = 1
                                                change = 650
                                            else:
                                                a = 1
                                                h = 1
                                                change = 1000
                                        elif h != 1:
                                            h = 1
                                            change = 350
                                    elif row['event'] in ['item_purchase','item_pickup']:
                                        if row['secondary_class'] in ['t1_rifle','t2_rifle','other']:
                                            if pr != 1:
                                                pr = 1
                                                pr_value = row['value']
                                                change = pr_value
                                            else:
                                                change = row['value'] - pr_value
                                        elif row['secondary_class'] == 'upgraded':
                                            if pi != 1:
                                                pi = 1
                                                pi_value = row['value']
                                                change = pi_value
                                            else:
                                                change = row['value'] - pi_value
                                        elif row['weapon'] == 'hegrenade':
                                            if g_he != 1 and g_t < 4:
                                                g_he = 1
                                                g_t += 1
                                                change = row['value']
                                        elif row['weapon'] == 'flashbang':
                                            if g_fla < 2 and g_t < 4:
                                                g_fla += 1
                                                g_t += 1
                                                change = row['value']
                                        elif row['weapon'] == 'smokegrenade':
                                            if g_smo != 1 and g_t < 4:
                                                g_smo = 1
                                                g_t += 1
                                                change = row['value']
                                        elif row['weapon'] == 'decoy':
                                            if g_dec != 1 and g_t < 4:
                                                g_dec = 1
                                                g_t += 1
                                                change = row['value']
                                        elif row['weapon'] in ['inferno','molotov_projectile','molotov','incgrenade']:
                                            if g_inc != 1 and g_t < 4:
                                                g_inc = 1
                                                g_t += 1
                                                change = row['value']
                                        else:
                                            raise ValueError('missing item name: ' + row['weapon'])
                                    elif row['event'] == 'item_drop':
                                        if row['secondary_class'] in ['t1_rifle','t2_rifle','other']:
                                            pr = 0
                                            pr_value = 0
                                            change = -1*row['value']
                                        elif row['secondary_class'] == 'upgraded':
                                            pi = 0
                                            pi_value = 0
                                            change = -1*row['value']
                                    elif row['event'] == 'weapon_fire':
                                        g_t -= 1
                                        change = -row['value']
                                        if row['weapon'] == 'hegrenade':
                                            g_he = 0
                                        elif row['weapon'] == 'flashbang':
                                            g_fla -= 1
                                        elif row['weapon'] == 'smokegrenade':
                                            g_smo = 0
                                        elif row['weapon'] == 'decoy':
                                            g_dec = 0
                                        elif row['weapon'] in ['inferno','molotov_projectile','molotov','incgrenade']:
                                            g_inc = 0
                                        else:
                                            raise ValueError('missing item name: ' + row['weapon'])
                                    item_change.set_value(index, 'econ', change)
                                    
                        item_change['defuse'] = item_change[['phase','defuse']].groupby('phase').cumsum()
                        item_change['defuse'] = item_change[['phase','defuse']].groupby('phase')['defuse'].ffill().fillna(0)
                        item_change['t_econ'] = item_change.loc[item_change['side'] == 2,['phase','econ']].groupby('phase').cumsum()
                        item_change['t_econ'] = item_change[['phase','t_econ']].groupby('phase')['t_econ'].ffill().fillna(0)
                        item_change['ct_econ'] = item_change.loc[item_change['side'] == 3,['phase','econ']].groupby('phase').cumsum()
                        item_change['ct_econ'] = item_change[['phase','ct_econ']].groupby('phase')['ct_econ'].ffill().fillna(0)
                        
                        for index, row in rounds.loc[rounds['round'] > 0].iterrows():
                            defuse = item_change.loc[(row['start'] <= item_change['tick'])
                                & (item_change['tick'] < row['first_blood']),'defuse'].max()
                            ct_econ = item_change.loc[(row['start'] <= item_change['tick'])
                                & (item_change['tick'] < row['first_blood']),'ct_econ'].max()
                            t_econ = item_change.loc[(row['start'] <= item_change['tick'])
                                & (item_change['tick'] < row['first_blood']),'t_econ'].max()
                            rounds.set_value(index, 'ct_econ_adv', ct_econ - t_econ)
                            rounds.set_value(index, 'defuse', defuse)
                            
                            
                        userid_side = pd.merge(init_data.loc[(init_data['event'] == 'player_connect') & (init_data['steamid'] != 'BOT'),
                                                             ['userid','steamid']].drop_duplicates(), 
                                                 item_change[['phase','steamid','side']].drop_duplicates(), how = 'left', on = 'steamid')\
                                             .drop_duplicates()
                                             
                        round_reward = pd.concat([item_change.loc[item_change['event'] == 'player_hurt'],
                                                  data.loc[data['event'] == 'bomb_planted',['tick','event','steamid']]])
                        round_reward = pd.merge(round_reward, userid_side, how = 'left', left_on = ['phase','attacker'],
                                                right_on = ['phase','userid'])
                        
						
#						 1 = Bomb explosion
#						 2 = No CTs remain (post-plant)
#						 7 = Bomb defused
#						 8 = No Ts remain
#						 9 = No CTs remain (pre-plant)
#						 12 = Time expired
                        for index, row in rounds.loc[rounds['round'] > 0].iterrows():
                            t_value,ct_value = [0,0]
                            temp_df = round_reward.loc[(round_reward['tick'] >= row['start'])
                                & (round_reward['tick'] <= row['end']),]
                            for index2, row2 in temp_df.iterrows():
                                if row2['event'] == 'bomb_planted':
                                    t_value += 300
                                elif row2['event'] == 'bomb_defused':
                                    ct_value += 300
                                elif row2['side_x'] == 2:
                                    if row2['side_y'] == 3:
                                        t_value += row2['kill']
                                    else:
                                        t_value -= 300
                                elif row2['side_x'] == 3:
                                    if row2['side_y'] == 2:
                                        ct_value += row2['kill']
                                    else:
                                        ct_value -= 300
                                else:
                                    raise ValueError('round reward error')
                            if row['reason'] == 12:
                                time_deaths = temp_df.loc[(temp_df['side_x'] == 2) & (temp_df['event'] == 'player_hurt')
                                    & (temp_df['tick'] > row['round_decision'])]
                                ct_value += 5*3250
                                t_value += (5 - len(time_deaths))*1400
                                rounds.set_value(index,'plant',0)
                            elif row['reason'] == 9:
                                t_value += 5*3250
                                ct_value += 5*1400
                                rounds.set_value(index,'plant',0)
                            elif row['reason'] <= 2:
                                t_value += 5*3500
                                ct_value += 5*1400
                                rounds.set_value(index,'plant',1)
                            elif row['reason'] == 8:
                                ct_value += 5*3250
                                t_value += 5*1400
                                rounds.set_value(index,'plant',0)
                            elif row['reason'] == 7:
                                ct_value += 5*3500
                                t_value += 5*(1400+800)
                                rounds.set_value(index,'plant',1)
                            else:
                                raise ValueError('round reward error')
                            rounds.set_value(index,'ct_reward_diff',ct_value - t_value)                            
                        
                        rounds['match_href'] = match_row[1]
                        rounds['map_num'] = int(file_[-6:-5])
                        
                        missing_econ_rds = rounds.loc[pd.isnull(rounds['ct_econ_adv']) & (rounds['round'] != -1)]
                        
                        if len(missing_econ_rds) > 0:
                            rounds = rounds.loc[(rounds['round'] < min(list(missing_econ_rds['round'])))
                                | ~rounds['phase'].isin(set(missing_econ_rds['phase']))]
                            error_msg = 'round with no econ value' + (', ' + error_msg if error_msg else '')
                            
                        with open('csv\\demo_rounds.csv', 'ab') as democsv:
                            rounds[['match_href','map_num','phase','round','t_href','ct_href','ct_econ_adv','ct_reward_diff','defuse',
                                    'plant','winner']].to_csv(democsv, header = False, index = False)
                           
                        mapname = data.loc[data['event']=='info','mapName'].iloc[0]
                        maphash = str(int(data.loc[data['event']=='info','mapHash'].iloc[0]))
                        
                        with open('csv\\demo_info.csv', 'ab') as democsv:
                            demowriter = csv.writer(democsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                            demowriter.writerow([match_row[1],int(file_[-6:-5]),file_[:-5],mapname,maphash,error_msg])
                            
                        print('\t' + match_row[1])
                    
                    except Exception as e:
                            error_msg = str(e)
                            with open('csv\\demo_info.csv', 'ab') as democsv:
                                demowriter = csv.writer(democsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                demowriter.writerow([match_row[1],int(file_[-6:-5]),file_[:-5],None,None,error_msg])
                            print('\tFAIL - ' + match_row[1])
                                
json_to_csv()