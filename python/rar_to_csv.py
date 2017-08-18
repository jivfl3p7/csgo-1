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

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 \
    Safari/537.36'}
    
scraped_match_info = pd.read_csv('csv\\hltv_match_info.csv', header = None)
    
matches_w_demos = scraped_match_info.loc[pd.isnull(scraped_match_info[2]) == False]
matches_w_demos.loc[:,8] = matches_w_demos.loc[:,0].apply(lambda x: re.compile('(?<=events\/)[0-9]*(?=\/)').search(x).group(0))
matches_w_demos.loc[:,9] = matches_w_demos.loc[:,1].apply(lambda x: re.compile('(?<=matches\/)[0-9]*(?=\/)').search(x).group(0))

def rar_download():
    print('### Rars ###')
    
    zipped_folder = r'E:\\CSGO Demos\\zipped'
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
    
    zipped_folder = r'E:\\CSGO Demos\\zipped'
    unzipped_folder = r'E:\\CSGO Demos\\unzipped'
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
                    Archive(zipped_folder + '\\' + eventid + '\\' + matchid).extractall(unzipped_folder + '\\' + eventid + '\\' + matchid[:-4])
                    print('\t' + match_row[1])
                except:
                    with open(unzipped_folder + '\\' + eventid + '\\' +  matchid[:-4] + '.dem', 'wb+') as file_:
                        file_.write('')
                    file_.close()
                    print('\tFAIL - ' + match_row[1])
                        
rar_to_demo()

def demo_to_json():
    print('### Jsons ###')
    unzipped_folder = 'E:\\CSGO Demos\\unzipped'
    json_folder = 'E:\\CSGO Demos\\json'
    parse_string1 = 'cd C:\\Users\\' + getpass.getuser() + '\\Documents\\Github\\dem2json && node dem2json.js '
    
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
                        args = (parse_string1 + parse_string2 + "\"" + json_folder + '\\' + eventid + "\\" + matchid + "\\" + matchid + "-" 
                            + str(idx) + ".json\"")
                        try:
                            subprocess.check_output(args, shell = True, stderr=subprocess.STDOUT)
                            print('\t' + match_row[1])
                        except Exception as e:
                            with open(json_folder + '\\' + eventid + '\\' +  matchid + '\\' +  matchid + "-" + str(idx) + '.json', 'wb+') as file_:
                                file_.write('')
                            file_.close()
                            
                            error_msg = str(e)
                            with open("csv\\json_fails.csv", 'ab') as jsonfailcsv:
                                jsonfailwriter = csv.writer(jsonfailcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                jsonfailwriter.writerow([eventid,matchid,error_msg])
                            print('\tFAIL - ' + match_row[1])

demo_to_json()

def json_to_csv():
    print('### json to csv ###')
    try:
        exist_csv = list(pd.read_csv('csv\\demo_info.csv', header = None)[0].drop_duplicates())
        try:
            exist_fail = list(pd.read_csv('csv\\csv_fails.csv', header = None)[1])
            exist_csv = exist_csv + exist_fail
        except:
            pass
    except:
        exist_csv = []
        
    weapon_data = pd.read_csv('csv\\weapon_info.csv')
    json_folder = 'E:\\CSGO Demos\\json'
    prev_eventid = None
    
    for eventid in os.listdir(json_folder)[11:18]:
        for matchid in os.listdir(json_folder + '\\' + eventid):
            for file_ in os.listdir(json_folder + '\\' + eventid + '\\' + matchid):
                if file_[:-5] not in exist_csv:
                    if prev_eventid != eventid:
                        print(eventid)
                        prev_eventid = eventid
                    try:
                        data = pd.read_json(json_folder + '\\' + eventid + '\\' + matchid + '\\' + file_)
                        # "C:\\Users\\wessonmo\\Desktop\\faze-vs-astralis-map1-mirage.json"
                        # "C:\\Users\\wessonmo\\Desktop\\faze-vs-astralis-map2-nuke.json"
                        # "C:\\Users\\wessonmo\\Desktop\\faze-vs-astralis-map3-inferno.json"
                        # "C:\\Users\\wessonmo\\Desktop\\1_flipsid3-natus-vincere_de_nuke.json"
                        
                        # score testing jsons
#                        data = pd.read_json("E:\\CSGO Demos\\json\\1617\\2298924\\2298924-0.json") right after half
#                        data = pd.read_json("E:\\CSGO Demos\\json\\1617\\2298948\\2298948-0.json") pre-half
#                        data = pd.read_json("E:\\CSGO Demos\\json\\1617\\2298949\\2298949-0.json") later in second half
#                        data = pd.read_json("E:\\CSGO Demos\\json\\1617\\2298960\\2298960-1.json") right after half
#                        data = pd.read_json("E:\\CSGO Demos\\json\\1617\\2298961\\2298961-0.json")
#                        data = pd.read_json("E:\\CSGO Demos\\json\\1617\\2298961\\2298961-1.json")
#                        data = pd.read_json("E:\\CSGO Demos\\json\\1617\\2298963\\2298963-0.json")
#                        data = pd.read_json("E:\\CSGO Demos\\json\\1617\\2298973\\2298973-1.json")
#                        data = pd.read_json("E:\\CSGO Demos\\json\\1617\\2298974\\2298974-0.json")
#                        data = pd.read_json("E:\\CSGO Demos\\json\\1617\\2298987\\2298987-0.json")
#                        data = pd.read_json("E:\\CSGO Demos\\json\\1617\\2298987\\2298987-2.json")
#                        data = pd.read_json("E:\\CSGO Demos\\json\\2013\\2300570\\2300570-0.json") final round?
                        
                        #wrong number of pistol rounds
#                        data = pd.read_json("E:\\CSGO Demos\\json\\2036\\2301160\\2301160-0.json")
#                        data = pd.read_json("C:\\Users\\wessonmo\\Desktop\\2301160-0.json")
                        
                        #match split into two demos
#                        data = pd.read_json("E:\\CSGO Demos\\json\\2013\\2300635\\2300635-1.json")
#                        data = pd.read_json("E:\\CSGO Demos\\json\\2013\\2300635\\2300635-2.json")
                        
                        #
                     
                        data = pd.merge(data, data.loc[(data['event'] == 'player_connect') &
                            (data['steamid'] != 'BOT'),['userid','steamid']], how = 'left', on = 'userid').rename(index = str,
                            columns = {'steamid_y':'steamid'}).reset_index(drop = True)
                        
                        match_info = pd.DataFrame(data[data['event']=='info'])
                        match_info.insert(0,'mapid',file_[:-5])
                        match_info['mapHash'] = match_info['mapHash'].astype(int).astype(str)
                        match_info = match_info[['mapid','mapName','mapHash']]
                        match_info = match_info.drop_duplicates()
#                        with open('csv\\demo_info.csv', 'ab') as infocsv:
#                            match_info.to_csv(infocsv, header = False, index = False)
                        
#                        data.loc[data['event'].isin(['round_start','round_end']),['tick','round','event','score_ct','score_t']]
                        
                        
                        team_switches = data.loc[data['event'] == 'player_team',['tick','event']].groupby('tick').count().reset_index()
                        team_switches = team_switches.loc[team_switches['event'] == 10]
                        team_switches['event'] = 'team_switch'
                        
                        rounds = data.loc[data['event'].isin(['round_start','round_end']),
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
                        rounds['round_est'] = rounds['score_t'] + rounds['score_ct']
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
                            
                        knife_round = pd.merge(data.loc[(data['event'] == 'player_hurt') & (data['weapon'] != ''),['tick','weapon']],
                                       weapon_data[['weapon','primary_class']],how = 'left', on = 'weapon')[['tick','primary_class']]\
                                       .drop_duplicates()
                        for index, row in knife_round[knife_round['tick'] <= rounds.loc[rounds['round_raw'] < 5,'end'].max()].iterrows():
                            for index2, row2 in rounds[rounds['round_raw'] < 5].iterrows():
                                if row2['start'] <= row['tick'] <= row2['round_decision']:
                                    knife_round.set_value(index,'round_raw',row2['round_raw'])
                                    break
                                else:
                                    pass
                        knife_round = knife_round.loc[(pd.isnull(knife_round['round_raw']) == False) & (knife_round['tick'] != 0)]
                        knife_round = pd.pivot_table(knife_round.groupby(['round_raw','primary_class']).size().reset_index(),
                                                index = 'round_raw', columns = 'primary_class', aggfunc = 'sum').reset_index().fillna(0)
                        knife_round.columns = knife_round.columns.droplevel(0)
                        knife_round = knife_round.loc[(knife_round['knife'] >= 10)
                            & (knife_round['knife']/(knife_round['pistol'] + knife_round['knife'] + knife_round['primary']) >= 0.8)
                            ,'']
                        
                        if len(knife_round) > 1:
                            raise ValueError('> 1 knife round')
                        elif len(knife_round) == 1:
                            rounds['round_est'] = np.where(rounds['round_raw'] == knife_round.iloc[0], -1, rounds['round_est'])
                        
                        for index, row in rounds.iloc[::-1].iterrows(): 
                            try:
                                if row['round_est'] == -1:
                                    pass
                                elif row['round_est'] - rounds['round_est'].iloc[int(index) - 1] > 1:
                                    raise ValueError('missing round')
                                elif row['round_est'] == rounds['round_est'].iloc[int(index) + 1]:
                                    rounds.drop(rounds.index[index], inplace = True)
                            except:
                                pass
                        
                        rounds['phase'] = np.where(rounds['round_est'] == -1, 'ot', np.where(rounds['round']))
                        rounds = rounds.drop(['event','round','round_raw'], 1).rename(index = str, columns = {'round_est':'round'})\
                            .reset_index(drop = True)
                            
                        for index, row in rounds.iterrows():
                            if row['round'] == 0:
                                rounds.set_value(index, 'phase', 'knife')
                            elif row['round'] <= 15:
                                rounds.set_value(index, 'phase', 'h1')
                            else:
                                rounds.set_value(index, 'phase', 'h2')
                        
                            
                            
                        
                        
#                        try:
#                            for index,row in round_type.iterrows():
#                                if (row['knife']/(row['pistol'] + row['knife'] + row['primary']) >= 0.8):
#                                    round_type.set_value(index,'round_type','knife')
#                                elif row['primary'] == 0:
#                                    round_type.set_value(index,'round_type','pistol')
#                                else :
#                                    round_type.set_value(index,'round_type','mixed')
#                        except:
#                            for index,row in round_type.iterrows():
#                                if row['primary'] == 0:
#                                    round_type.set_value(index,'round_type','pistol')
#                                else :
#                                    round_type.set_value(index,'round_type','mixed')
#                        
#                        if len(round_type.loc[round_type['round_type'] == 'pistol']) != 2:
#                            if round_type.loc[round_type.index.max(),'round_type'] == 'pistol':
#                                round_type = round_type.loc[round_type.index < round_type.index.max()]
#                            else:
#                                raise ValueError('wrong number of pistol rounds')
#                        
#                        rounds = pd.merge(rounds, round_type[['','round_type']], how = 'left', left_on = 'round_raw', right_on = '')\
#                            .drop('', axis = 1)                        
#                        
#                        
#                        
#                        
#                        
#                            
#                            
#                        rounds = pd.concat([rounds,team_switches]).sort_values(['tick','event'], ascending = [True,False])\
#                            .reset_index(drop = True).rename(index = str, columns = {'tick':'start'})
#                        rounds['cumcount'] = rounds.loc[::-1].groupby('round').cumcount()
#                        rounds = rounds.loc[(rounds['event'] == 'team_switch') | (rounds['round'] == 0) | (rounds['cumcount'] == 0),:]\
#                            .drop('cumcount', axis = 1)
#                        
#                        i,prev_ct,prev_t = 1,None,None
#                        for index, row in rounds.iterrows():
#                            if (row['score_ct'] == prev_ct) and (row['score_t'] == prev_t)\
#                                and (row['score_ct'] + row['score_t'] > 0):
#                                print(json_folder + '\\' + eventid + '\\' + matchid + '\\' + file_)
#                                raise ValueError('multiple rounds with same score')
##                                return
#                            prev_ct,prev_t = row['score_ct'],row['score_t']
#                            if row['event'] == 'round_start':
#                                rounds.set_value(index, 'round_raw', i)
#                                i += 1
#                        
##                        round_type = pd.merge(data.loc[(data['event'].isin(['player_hurt','item_pickup','item_purchase','item_drop']))
##                            & (data['weapon'] != ''),['tick','weapon']],weapon_data[['weapon','primary_class']],how = 'left',
##                                on = 'weapon')[['tick','primary_class']].drop_duplicates()
#                        
#                                
#                        
#                        round_type = pd.pivot_table(round_type.groupby(['round_raw','primary_class']).size().reset_index(),
#                                                index = 'round_raw', columns = 'primary_class', aggfunc = 'sum').reset_index().fillna(0)
#                        round_type.columns = round_type.columns.droplevel(0)
#                        try:
#                            round_type = round_type.loc[(round_type['knife'] >= 10) | (round_type['pistol'] + round_type['primary'] >= 5)]
#                        except:
#                            round_type = round_type.loc[round_type['pistol'] + round_type['primary'] >= 5]
#                        
#                        try:
#                            for index,row in round_type.iterrows():
#                                if (row['knife']/(row['pistol'] + row['knife'] + row['primary']) >= 0.8):
#                                    round_type.set_value(index,'round_type','knife')
#                                elif row['primary'] == 0:
#                                    round_type.set_value(index,'round_type','pistol')
#                                else :
#                                    round_type.set_value(index,'round_type','mixed')
#                        except:
#                            for index,row in round_type.iterrows():
#                                if row['primary'] == 0:
#                                    round_type.set_value(index,'round_type','pistol')
#                                else :
#                                    round_type.set_value(index,'round_type','mixed')
#                        
#                        if len(round_type.loc[round_type['round_type'] == 'pistol']) != 2:
#                            if round_type.loc[round_type.index.max(),'round_type'] == 'pistol':
#                                round_type = round_type.loc[round_type.index < round_type.index.max()]
#                            else:
#                                raise ValueError('wrong number of pistol rounds')
                        
#                        rounds = pd.merge(rounds, round_type[['','round_type']], how = 'left', left_on = 'round_raw', right_on = '')\
#                            .drop('', axis = 1)
    
#                        rnd_counter = None
#                        pstl_counter = 0
#                        for index, row in rounds.iterrows():
#                            if row['round_type'] == 'knife':
#                                rounds.set_value(index, 'round', 0)
#                            if row['round_type'] == 'pistol':
#                                rounds.set_value(index, 'round', (pstl_counter)*15 + 1)                                
#                                rnd_counter = (pstl_counter)*15 + 2
#                                pstl_counter += 1
#                            if row['round_type'] == 'mixed' and rnd_counter != None:
#                                if pstl_counter == 1 and rnd_counter > 15:
#                                    raise ValueError('too many rounds between pistols')
#                                else:
#                                    rounds.set_value(index, 'round', rnd_counter)
#                                    rnd_counter += 1
#                            if row['event'] == 'team_switch':
#                                if pstl_counter != 2:
#                                    rnd_counter = None
                        
                        rounds = rounds.loc[rounds['round'] <= 30].reset_index(drop = True)
                        for index, row in rounds.iterrows():
                            if row['round'] == 0:
                                rounds.set_value(index, 'phase', 'knife')
                            elif row['round'] <= 15:
                                rounds.set_value(index, 'phase', 'h1')
                            else:
                                rounds.set_value(index, 'phase', 'h2')
                                    
                        for index, row in rounds.iterrows():
                            if (row['round'] in [0,15,30]) or (pd.isnull(row['end']) == True):
                                rounds.set_value(index, 'end', row['round_decision'])
                        
                        rounds = rounds[['phase','round','start','round_decision','end','winner','reason']]
                        
                        first_blood = pd.DataFrame(data.loc[data['event'] == 'player_hurt','tick'])
                        for index, row in first_blood.iterrows():
                            for index2, row2 in rounds.loc[rounds['round'] > 0].iterrows():
                                if row2['start'] <= row['tick'] <= row2['end']:
                                    first_blood.set_value(index,'round',row2['round'])
                                    break
                                else:
                                    pass
                            
                        first_blood = first_blood.groupby('round').min().reset_index()
                        rounds = pd.merge(rounds, first_blood, how = 'left', on = 'round').rename(index = str,
                            columns = {'tick':'first_blood'}).reset_index(drop = True)
                        
                        teams = data.loc[(data['event'] == 'item_purchase') | ((data['event'] == 'player_hurt') & (data['health'] == 0)),
                                         ['tick','side','clanname']]
                        for index, row in teams.iterrows():
                            for index2, row2 in rounds.iterrows():
                                if row2['start'] <= row['tick'] <= row2['round_decision']:
                                    teams.set_value(index, 'round', row2['round'])
                                    break
                        
                        teams = teams.loc[pd.isnull(teams['round']) == False, ['round','clanname','side']].drop_duplicates()
                        
                        rounds = pd.merge(rounds, teams.loc[teams['side'] == 3,['round','clanname']], how = 'left', on = 'round')\
                            .rename(index = str, columns = {'clanname':'ct_team'}).reset_index(drop = True)
                        rounds = pd.merge(rounds, teams.loc[teams['side'] == 2,['round','clanname']], how = 'left', on = 'round')\
                            .rename(index = str, columns = {'clanname':'t_team'}).reset_index(drop = True)
                        
                        item_change = data.loc[(data['event'].isin(['defuser_purchase','armor_purchase']))
                            | ((data['weapon'] != 'c4') & data['event'].isin(['item_purchase','item_pickup','item_drop']))
                            | (data['health'] == 0) | ((data['event'] == 'weapon_fire') & (data['weapon'].isin(
                                ['decoy','flashbang','molotov','smokegrenade','hegrenade','incgrenade']))),
                            ['tick','event','steamid','side','health','weapon','boughtHelmet']]
                        item_change['min_tick'] = rounds.loc[rounds['round'] >= 1,['start','end']].min(axis=1).min()
                        item_change['max_tick'] = rounds.loc[rounds['round'] >= 1,['start','end']].max(axis=1).max()
                        item_change = item_change.loc[(item_change['min_tick'] <= item_change['tick'])
                            & (item_change['tick'] <= item_change['max_tick']),
                            ['tick','event','steamid','side','health','weapon','boughtHelmet']]
                        item_change = pd.merge(item_change, weapon_data, how = 'left', on = 'weapon')
                        for index, row in item_change.iterrows():
                            for index2, row2 in rounds.iterrows():
                                if row2['start'] <= row['tick'] <= row2['end']:
                                    item_change.set_value(index,'round',row2['round'])
                                    item_change.set_value(index,'phase',row2['phase'])
                                    break
                                else:
                                    pass
                        
                        item_change = item_change.loc[pd.isnull(item_change['round']) == False]
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
                                g = 0
                                pr = 0
                                pi = 0
                                a = 0
                                h = 0
                                for index,row in item_change.loc[(item_change['steamid'] == steamid)
                                                                & (item_change['life_seq'] == life_seq)].iterrows():
                                    change = 0
                                    if row['event'] == 'defuser_purchase':
                                        change = 400
                                    if row['event'] == 'armor_purchase':
                                        if row['boughtHelmet'] == 0:
                                            if a != 650:
                                                a = 650
                                                change = a
                                            else:
                                                change = 0
                                        else:
                                            if a != 650:
                                                a = 650
                                                h = 350
                                                change = a + h
                                            elif h != 350:
                                                h = 350
                                                change = h
                                            else:
                                                change = 0
                                    if row['event'] == 'weapon_fire':
                                        g += -1*row['value']
                                        change = -1*row['value']
                                    if row['event'] in ['item_purchase','item_pickup']:
                                        if row['secondary_class'] in ['t1_rifle','t2_rifle','other']:
                                            pr = row['value']
                                            change = row['value']
                                        if row['secondary_class'] == 'upgraded':
                                            pi = row['value']
                                            change = row['value']
                                        if row['weapon'] in ['hegrenade','inferno','flashbang','molotov_projectile','smokegrenade',
                                                'molotov','incgrenade','inferno','decoy']:
                                            g += row['value']
                                            change = row['value']
                                    if row['event'] == 'item_drop':
                                        if row['secondary_class'] in ['t1_rifle','t2_rifle','other']:
                                            pr = -1*row['value']
                                            change = -1*row['value']
                                        if row['secondary_class'] == 'upgraded':
                                            pi = -1*row['value']
                                            change = -1*row['value']
                                    if row['event'] == 'player_hurt':
                                        item_change.set_value(index, 'econ', -1*(g + pr + pi + a + h))
                                    else:
                                        item_change.set_value(index, 'econ', change)
                                    
                        item_change['t_econ'] = item_change.loc[item_change['side'] == 2,['phase','econ']].groupby('phase').cumsum()
                        item_change['t_econ'] = item_change[['phase','t_econ']].groupby('phase')['t_econ'].ffill().fillna(0)
                        item_change['ct_econ'] = item_change.loc[item_change['side'] == 3,['phase','econ']].groupby('phase').cumsum()
                        item_change['ct_econ'] = item_change[['phase','ct_econ']].groupby('phase')['ct_econ'].ffill().fillna(0)
    #                    item_change.loc[item_change['steamid'] == 'STEAM_1:0:78128774',['steamid','event','weapon','econ','t_econ']]
    #                    item_change.to_csv('C:\\Users\\wessonmo\\Desktop\\item_change.csv')
                        
                        for index, row in rounds.loc[rounds['round'] > 0].iterrows():
                            ct_econ = item_change.loc[(row['start'] <= item_change['tick'])
                                & (item_change['tick'] < row['first_blood']),'ct_econ'].max()
                            t_econ = item_change.loc[(row['start'] <= item_change['tick'])
                                & (item_change['tick'] < row['first_blood']),'t_econ'].max()
                            rounds.set_value(index, 'ct_econ_adv', ct_econ - t_econ)
                            
                        try:
                            i
#                            with open('csv\\demo_knife.csv', 'ab') as knifecsv:
#                                rounds.loc[rounds['round'] == 0,['mapid','t_team','ct_team','winner']]\
#                                    .to_csv(knifecsv, header = False, index = False)
                        except:
                            pass
                        
#                        with open('csv\\demo_pistol.csv', 'ab') as pistolcsv:
#                                rounds.loc[rounds['round'].isin([1,16]),['mapid','round','t_team','ct_team','winner']]\
#                                    .to_csv(pistolcsv, header = False, index = False)
#                                
#                        with open('csv\\demo_primary.csv', 'ab') as primarycsv:
#                            rounds.loc[~rounds['round'].isin([0,1,16]),['mapid','round','t_team','ct_team','ct_econ_adv','winner']]\
#                                .to_csv(primarycsv, header = False, index = False)
                            
                        
                        players = data.loc[(data['event'].isin(['player_hurt','item_purchase','item_pickup','armor_purchase','item_drop']))
                            & (((data['round'] >= 3) & (data['round'] <= 5)) | ((data['round'] > 16) & (data['round'] <= 20))),
                            ['tick','steamid','clanname']]
                        for index, row in players.iterrows():
                            for index2, row2 in rounds.iterrows():
                                if row2['start'] <= row['tick'] <= row2['end']:
                                    players.set_value(index,'round',row2['round'])
                                    break
                                else:
                                    pass
                                
                        players = pd.merge(players.loc[pd.isnull(players['round']) == False,['clanname','steamid']].drop_duplicates(),
                                       data.loc[data['event'] == 'player_connect',['steamid','name']], how = 'left', on = 'steamid')\
                                       .rename(index = str, columns = {'clanname':'team'})
                        for index, row in players.iterrows():
                            players.set_value(index, 'name', re.sub(r'[^\x00-\x7F]+','',str(row['name'].encode('utf-8'))))
                            players.set_value(index, 'team', re.sub(r'[^\x00-\x7F]+','',str(row['team'].encode('utf-8'))))
                        players.insert(0, 'mapid', file_[:-5])
                        
#                        with open('csv\\demo_players.csv', 'ab') as playercsv:
#                            players[['mapid','steamid','name','team']].to_csv(playercsv, header = False, index = False)
                            
                        print(file_[:-5])
                    
                    except Exception as e:
                            error_msg = str(e)
                            with open('csv\\csv_fails.csv', 'ab') as csvfailcsv:
                                csvfailwriter = csv.writer(csvfailcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                csvfailwriter.writerow([eventid,file_[:-5],error_msg])
                                
#json_to_csv()