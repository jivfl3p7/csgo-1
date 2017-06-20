# -*- coding: utf-8 -*-
"""
Created on Thu May 18 13:08:21 2017

@author: wesso
"""

from __future__ import division
import os
import pandas as pd
import re
import csv

def json_to_csv():
    try:
        exist_csv = list(pd.read_csv('csv\\match_info.csv', header = None)[0].drop_duplicates())
        try:
            exist_fail = list(pd.read_csv('csv\\csv_fails.csv', header = None)[1])
            exist_csv = exist_csv + exist_fail
        except:
            pass
    except:
        exist_csv = []
        
    weapon_data = pd.read_csv("C:\\Users\\wesso\\Documents\\Github\\dem2json\\csgo weapon value.csv")
    json_folder = "E:\\CSGO Demos\\json"
    
    for eventid in os.listdir(json_folder):#reversed()
        print(eventid)
        for matchid in os.listdir(json_folder + '\\' + eventid):
            for file_ in os.listdir(json_folder + '\\' + eventid + '\\' + matchid):
                if file_[:-5] not in exist_csv:
                    try:
                        data = pd.read_json(json_folder + '\\' + eventid + '\\' + matchid + '\\' + file_)
                        data = pd.merge(data, data.loc[(data['event'] == 'player_connect') & (data['steamid'] != 'BOT'),['userid','steamid']], how = 'left', on = 'userid').rename(index = str, columns = {'steamid_y':'steamid'}).reset_index(drop = True)
                        
                        match_info = pd.DataFrame(data[data['event']=='info'])
                        match_info.insert(0,'mapid',file_[:-5])
                        match_info['mapHash'] = match_info['mapHash'].astype(str)
                        match_info = match_info[['mapid','mapName','mapHash','tickRate']]
                        match_info = match_info.drop_duplicates()
                        
                        player_teams = pd.DataFrame(columns = ['steamid','team'])
                        team_connect_tick = data.loc[((pd.isnull(data['team']) == True) | (data['round'] == 15)) & (data['team'] != '') & (data['event'] == 'player_team'),['tick','round','steamid','team']].drop_duplicates()
                        team_connect_tick['cumcount'] = team_connect_tick.groupby('tick').cumcount()
                        
                        if team_connect_tick['cumcount'].max() != 9:
                            raise ValueError('issue with player teams')
                        
                        i = 0
                        for index, row in data.loc[((pd.isnull(data['team']) == True) | (data['tick'] == list(team_connect_tick.loc[team_connect_tick['cumcount'] == 9,'tick'])[0])) & (data['team'] != '') & (data['event'] == 'player_team'),['round','steamid','team']].iterrows():
                            if row['steamid'] not in list(player_teams.steamid.drop_duplicates()):
                                if row['round'] == 15:
                                    try:
                                        player_teams.loc[i] = [row['steamid'], list(set(data.loc[(pd.isnull(data['team']) == False) & (data['team'] != '') & (data['round'] == 15),'team'].drop_duplicates()) - set([row['team'].encode('utf-8')]))[0]]
                                        i += 1
                                    except:
                                        raise ValueError('not enough team names')
                                else:
                                    player_teams.loc[i] = [row['steamid'], row['team']]
                                    i += 1
                                    
                        if [10,15] != list(pd.merge(player_teams,data.loc[(data['round'] < 14) & (data['round'] > 2) & (data['event'] == 'item_purchase'),['steamid','side']].drop_duplicates(), how = 'left', on = 'steamid').groupby('team').sum().reset_index().side.sort_values()):
                            raise ValueError('issue with player teams')
                            
                        players = pd.merge(player_teams,data.loc[(data['event'] == 'player_connect') & (data['tick'] < 1000),['steamid','name']], how = 'left', on = 'steamid')
                        players = players[['steamid','name','team']].drop_duplicates()
                        for index, row in players.iterrows():
                            players.set_value(index, 'name', re.sub(r'[^\x00-\x7F]+','',str(row['name'].encode('utf-8'))))
                            players.set_value(index, 'team', re.sub(r'[^\x00-\x7F]+','',str(row['team'].encode('utf-8'))))
                        players.insert(0, 'mapid', file_[:-5])
                        
                        team_switches = data.loc[data['event'] == 'player_team',['tick','event']].groupby('tick').count().reset_index()
                        team_switches = team_switches.loc[team_switches['event'] == 10]
                        team_switches['event'] = 'team_switch'
                        
                        rounds = data.loc[data['event'].isin(['round_start','round_end']),['round','tick','event','winner','reason']]
                                          
                        if list(rounds.loc[rounds['event'].str.contains('round'),'event'])[0] == 'round_end':
                            rounds.loc[rounds.index.max() + 1] = [-2,0,'round_start',None,None]
                            rounds = rounds.sort_values(['tick','event'], ascending = [True,False]).reset_index(drop = True)
                            
                        rounds['winner'] = rounds['winner'].shift(-1)
                        rounds['reason'] = rounds['reason'].shift(-1)
                        rounds['next_event'] = rounds['event'].shift(-1)
                        rounds['round_decision'] = rounds['tick'].shift(-1)
                        rounds = rounds.loc[(rounds['event'] == 'round_start') & (rounds['next_event'] == 'round_end'),['round','tick','event','round_decision','winner','reason']].reset_index(drop = True)
                        rounds['end'] = rounds['tick'].shift(-1) - 1
                        rounds = pd.concat([rounds,team_switches]).sort_values(['tick','event'], ascending = [True,False]).reset_index(drop = True)[['round','tick','round_decision','end','event','winner','reason']].rename(index = str, columns = {'tick':'start'})
                        rounds['cumcount'] = rounds.loc[::-1].groupby('round').cumcount()
                        rounds = rounds.loc[(rounds['event'] == 'team_switch') | (rounds['round'] == 0) | (rounds['cumcount'] == 0),['round','start','round_decision','end','event','winner','reason']]
                        
                        i = 1
                        for index, row in rounds.iterrows():
                            if row['event'] == 'round_start':
                                rounds.set_value(index, 'round_raw', i)
                                i += 1
                        
                        round_type = pd.merge(data.loc[(data['event'].isin(['player_hurt','item_pickup','item_purchase','item_drop'])) & (data['weapon'] != ''),['tick','weapon']],weapon_data[['weapon','primary_class']],how = 'left', on = 'weapon')[['tick','primary_class']]
                        for index, row in round_type.iterrows():
                            for index2, row2 in rounds[rounds['event'] == 'round_start'].iterrows():
                                if row2['start'] <= row['tick'] <= row2['round_decision']:
                                    round_type.set_value(index,'round_raw',row2['round_raw'])
                                    break
                                else:
                                    pass
                        round_type = round_type.loc[pd.isnull(round_type['round_raw']) == False]
                        round_type = pd.pivot_table(round_type.groupby(['round_raw','primary_class']).size().reset_index(), index = 'round_raw', columns = 'primary_class', aggfunc = 'sum').reset_index().fillna(0)
                        round_type.columns = round_type.columns.droplevel(0)
                        try:
                            round_type = round_type.loc[(round_type['knife'] >= 10) | (round_type['pistol'] + round_type['primary'] >= 5)]
                        except:
                            round_type = round_type.loc[round_type['pistol'] + round_type['primary'] >= 5]
                        
                        for index,row in round_type.iterrows():
                            if (row['pistol'] == 0) & (row['primary'] == 0):
                                round_type.set_value(index,'round_type','knife')
                            elif row['primary'] == 0:
                                round_type.set_value(index,'round_type','pistol')
                            else :
                                round_type.set_value(index,'round_type','mixed')
                        
                        if len(round_type.loc[round_type['round_type'] == 'pistol']) != 2:
                            if round_type.loc[round_type.index.max(),'round_type'] == 'pistol':
                                round_type = round_type.loc[round_type.index < round_type.index.max()]
                            else:
                                raise ValueError('wrong number of pistol rounds')
                        
                        rounds = pd.merge(rounds, round_type[['','round_type']], how = 'left', left_on = 'round_raw', right_on = '')[['round_raw','event','start','round_type','round_decision','end','winner','reason']]
    
                        rnd_counter = None
                        pstl_counter = 0
                        for index, row in rounds.iterrows():
                            if row['round_type'] == 'knife':
                                rounds.set_value(index, 'round', 0)
                            if row['round_type'] == 'pistol':
                                rounds.set_value(index, 'round', (pstl_counter)*15 + 1)                                
                                rnd_counter = (pstl_counter)*15 + 2
                                pstl_counter += 1
                            if row['round_type'] == 'mixed' and rnd_counter != None:
                                if pstl_counter == 1 and rnd_counter > 15:
                                    raise ValueError('too many rounds between pistols')
                                else:
                                    rounds.set_value(index, 'round', rnd_counter)
                                    rnd_counter += 1
                            if row['event'] == 'team_switch':
                                if pstl_counter != 2:
                                    rnd_counter = None
                        
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
    
                        team_side = data.loc[((data['round'] == 0) & (data['health'] == 0)) | (data['event'] == 'item_purchase'),['tick','steamid','side']].drop_duplicates()
                        for index, row in team_side.iterrows():
                            for index2, row2 in rounds.iterrows():
                                if row2['start'] <= row['tick'] < row2['round_decision']:
                                    team_side.set_value(index,'round',row2['round'])
                                    break
                                else:
                                    pass
                        
                        team_side = pd.merge(team_side, players, how = 'left', on = 'steamid')[['round','side','team']].drop_duplicates()
                        team_side = team_side.loc[(pd.isnull(team_side['round']) == False) & (pd.isnull(team_side['team']) == False)].sort_values(['round','side'])
                        t_teams = team_side.loc[team_side['side'] == 2,['round','team']]
                        ct_teams = team_side.loc[team_side['side'] == 3,['round','team']]
                        
                        rounds = pd.merge(pd.merge(rounds, t_teams, how = 'left', on = 'round'),ct_teams, how = 'left', on = 'round').rename(index = str, columns = {'team_x':'t_team', 'team_y':'ct_team'})
                        
                        for index, row in rounds.iterrows():
                            if row['t_team'] == row['ct_team']:
                                raise ValueError('team side issue')
                            elif pd.isnull(row['t_team']) == True:
                                rounds.set_value(index, 't_team', list(set(rounds.loc[pd.isnull(rounds['t_team']) == False,'t_team']) - set([row['ct_team']]))[0])
                            elif pd.isnull(row['ct_team']) == True:
                                rounds.set_value(index, 'ct_team', list(set(rounds.loc[pd.isnull(rounds['ct_team']) == False,'ct_team']) - set([row['t_team']]))[0])
                        
                        
                        if len(rounds.loc[(pd.isnull(rounds['round']) == False) & ((pd.isnull(rounds['t_team']) == True) | (pd.isnull(rounds['ct_team']) == True))]) > 0:
                            for index, row in rounds.loc[(pd.isnull(rounds['round']) == False) & ((pd.isnull(rounds['t_team']) == True) | (pd.isnull(rounds['ct_team']) == True))].iterrows():
                                if pd.isnull(row['t_team']) == True:
                                    rounds.set_value(index, 't_team', list(rounds.loc[(rounds['phase'] == row['phase']) & (pd.isnull(rounds['t_team']) == False),'t_team'].drop_duplicates())[0].encode('utf-8'))
                                if pd.isnull(row['ct_team']) == True:
                                    rounds.set_value(index, 'ct_team', list(rounds.loc[(rounds['phase'] == row['phase']) & (pd.isnull(rounds['ct_team']) == False),'ct_team'].drop_duplicates())[0].encode('utf-8'))
                                
                        first_blood = pd.DataFrame(data.loc[data['event'] == 'player_hurt','tick'])
                        for index, row in first_blood.iterrows():
                            for index2, row2 in rounds.loc[rounds['round'] > 0].iterrows():
                                if row2['start'] <= row['tick'] <= row2['end']:
                                    first_blood.set_value(index,'round',row2['round'])
                                    break
                                else:
                                    pass
                            
                        first_blood = first_blood.groupby('round').min().reset_index()
                        rounds = pd.merge(rounds, first_blood, how = 'left', on = 'round').rename(index = str, columns = {'tick':'first_blood'}).reset_index(drop = True)
                      
                        item_change = data.loc[(data['event'] == 'armor_purchase') | ((data['weapon'] != 'c4') & data['event'].isin(['item_purchase','item_pickup','item_drop'])) | (data['health'] == 0) | ((data['event'] == 'weapon_fire') & (data['weapon'].isin(['decoy','flashbang','molotov','smokegrenade','hegrenade','incgrenade']))),['tick','event','steamid','side','health','weapon','boughtHelmet']]
                        item_change['min_tick'] = rounds.loc[rounds['round'] >= 1,['start','end']].min(axis=1).min()
                        item_change['max_tick'] = rounds.loc[rounds['round'] >= 1,['start','end']].max(axis=1).max()
                        item_change = item_change.loc[(item_change['min_tick'] <= item_change['tick']) & (item_change['tick'] <= item_change['max_tick']),['tick','event','steamid','side','health','weapon','boughtHelmet']]
                        item_change = pd.merge(item_change, weapon_data, how = 'left', on = 'weapon')
                        for index, row in item_change.iterrows():
                            for index2, row2 in rounds.iterrows():
                                if row2['start'] <= row['tick'] <= row2['end']:
                                    item_change.set_value(index,'round',row2['round'])
                                    item_change.set_value(index,'phase',row2['phase'])
                                    break
                                else:
                                    pass
                        
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
                        
                        item_change['life_seq'] = item_change.loc[(item_change['phase_change'] == 1) | (item_change['event'] == 'player_hurt')].groupby('steamid').cumcount()
                        item_change['life_seq'] = item_change.groupby('steamid')['life_seq'].bfill().ffill()
                        item_change = item_change.sort_values(['tick','event']).reset_index(drop = True)
                        
                        primary_change = item_change.loc[(item_change['event'] == 'player_hurt') | (item_change['primary_class'] == 'primary'),['tick','round','phase','life_seq','event','steamid','side','secondary_class']]
                        for steamid in list(primary_change['steamid'].drop_duplicates()):
                            for life_seq in range(0,int(max(primary_change['life_seq'])) + 1):
                                i = 1
                                modifier = 0
                                weapon_type = None
                                for index,row in primary_change.loc[(primary_change['steamid'] == steamid) & (primary_change['life_seq'] == life_seq)].iterrows():
                                    if (i == 1) and (row['event'] == 'player_hurt'):
                                        break
                                    elif row['event'] in ['item_purchase','item_pickup','item_drop']:
                                        if row['event'] == 'item_drop':
                                            modifier = -1
                                        else:
                                            modifier = 1
                                        if row['secondary_class'] == 't1_rifle':
                                            primary_change.set_value(index, 'player_t1_rifle', 1*modifier)
                                            weapon_type = 't1_rifle'
                                            i += 1
                                        elif row['secondary_class'] == 't2_rifle':
                                            primary_change.set_value(index, 'player_t2_rifle', 1*modifier)
                                            weapon_type = 't2_rifle'
                                            i += 1
                                        else:
                                            primary_change.set_value(index, 'player_other', 1*modifier)
                                            weapon_type = 'other'
                                            i += 1
                                    else:
                                        if modifier == -1:
                                            break
                                        elif weapon_type == 't1_rifle':
                                            primary_change.set_value(index, 'player_t1_rifle', -1)
                                        elif weapon_type == 't2_rifle':
                                            primary_change.set_value(index, 'player_t2_rifle', -1)
                                        else:
                                            primary_change.set_value(index, 'player_other', -1)
                        
                        primary_change = primary_change.fillna(0)
                        primary_change['t_t1_rifle'] = primary_change.loc[primary_change['side'] == 2].groupby('phase')['player_t1_rifle'].cumsum()
                        primary_change['t_t1_rifle'] = primary_change['t_t1_rifle'].ffill().fillna(0)
                        try:
                            primary_change['t_t2_rifle'] = primary_change.loc[primary_change['side'] == 2].groupby('phase')['player_t2_rifle'].cumsum()
                            primary_change['t_t2_rifle'] = primary_change['t_t2_rifle'].ffill().fillna(0)
                        except:
                            primary_change['t_t2_rifle'] = 0
                        try:
                            primary_change['t_other_primary'] = primary_change.loc[primary_change['side'] == 2].groupby('phase')['player_other'].cumsum()
                            primary_change['t_other_primary'] = primary_change['t_other_primary'].ffill().fillna(0)
                        except:
                            primary_change['t_other_primary'] = 0
                        primary_change['ct_t1_rifle'] = primary_change.loc[primary_change['side'] == 3].groupby('phase')['player_t1_rifle'].cumsum()
                        primary_change['ct_t1_rifle'] = primary_change['ct_t1_rifle'].ffill().fillna(0)
                        try:
                            primary_change['ct_t2_rifle'] = primary_change.loc[primary_change['side'] == 3].groupby('phase')['player_t2_rifle'].cumsum()
                            primary_change['ct_t2_rifle'] = primary_change['ct_t2_rifle'].ffill().fillna(0)
                        except:
                            primary_change['ct_t2_rifle'] = 0
                        try:
                            primary_change['ct_other_primary'] = primary_change.loc[primary_change['side'] == 3].groupby('phase')['player_other'].cumsum()
                            primary_change['ct_other_primary'] = primary_change['ct_other_primary'].ffill().fillna(0)
                        except:
                            primary_change['ct_other_primary'] = 0
                        
                        primary_change = primary_change[['tick','round','phase','t_t1_rifle','t_t2_rifle','t_other_primary','ct_t1_rifle','ct_t2_rifle','ct_other_primary']]
                                
                        i = 1
                        for index, row in rounds.loc[~rounds['round'].isin([0,1,16])].iterrows():
                            if len(primary_change.loc[(row['start'] <= primary_change['tick']) & (primary_change['tick'] < row['first_blood'])]) == 0:
                                primary_change.loc[max(primary_change.index) + i] = [row['first_blood'] - 1,None,None,None,None,None,None,None,None]
                                i += 1
                            else:
                                pass
                        
                        primary_change = primary_change.sort_values('tick').reset_index(drop = True)
                        primary_change['phase'] = primary_change['phase'].bfill()
                        primary_change['t_t1_rifle'] = primary_change.groupby('phase')['t_t1_rifle'].ffill()
                        primary_change['t_t2_rifle'] = primary_change.groupby('phase')['t_t2_rifle'].ffill()
                        primary_change['t_other_primary'] = primary_change.groupby('phase')['t_other_primary'].ffill()
                        primary_change['ct_t1_rifle'] = primary_change.groupby('phase')['ct_t1_rifle'].ffill()
                        primary_change['ct_t2_rifle'] = primary_change.groupby('phase')['ct_t2_rifle'].ffill()
                        primary_change['ct_other_primary'] = primary_change.groupby('phase')['ct_other_primary'].ffill()
                        primary_change = primary_change[['tick','round','t_t1_rifle','t_t2_rifle','t_other_primary','ct_t1_rifle','ct_t2_rifle','ct_other_primary']]
                        
                        pistol_change = item_change.loc[(item_change['event'] == 'player_hurt') | (item_change['secondary_class'] == 'upgraded'),['tick','round','phase','life_seq','event','steamid','side']]
                        for steamid in list(pistol_change['steamid'].drop_duplicates()):
                            for life_seq in range(0,int(max(pistol_change['life_seq'])) + 1):
                                i = 1
                                modifier = 0
                                for index,row in pistol_change.loc[(pistol_change['steamid'] == steamid) & (pistol_change['life_seq'] == life_seq)].iterrows():
                                    if (i == 1) and (row['event'] == 'player_hurt'):
                                        pistol_change.set_value(index, 'player_upg_pistol', 0)
                                    elif row['event'] in ['item_purchase','item_pickup','item_drop']:
                                        if row['event'] == 'item_drop':
                                            modifier = -1
                                            pistol_change.set_value(index, 'player_upg_pistol', 1*modifier)
                                            i += 1
                                        else:
                                            modifier = 1
                                            pistol_change.set_value(index, 'player_upg_pistol', 1*modifier)
                                            i += 1
                                    else:
                                        if modifier == -1:
                                            pistol_change.set_value(index, 'player_upg_pistol', 0)
                                        else:
                                            pistol_change.set_value(index, 'player_upg_pistol', -1)
                        
                        pistol_change['t_upg_pistol'] = pistol_change.loc[pistol_change['side'] == 2].groupby('phase')['player_upg_pistol'].cumsum()
                        pistol_change['t_upg_pistol'] = pistol_change['t_upg_pistol'].ffill().fillna(0)
                        pistol_change['ct_upg_pistol'] = pistol_change.loc[pistol_change['side'] == 3].groupby('phase')['player_upg_pistol'].cumsum()
                        pistol_change['ct_upg_pistol'] = pistol_change['ct_upg_pistol'].ffill().fillna(0)
                        pistol_change = pistol_change[['tick','round','phase','t_upg_pistol','ct_upg_pistol']]
                        
                        i = 1
                        for index, row in rounds.loc[rounds['round'] != 0].iterrows():
                            if len(pistol_change.loc[(row['start'] <= pistol_change['tick']) & (pistol_change['tick'] < row['first_blood'])]) == 0:
                                pistol_change.loc[max(pistol_change.index) + i] = [row['first_blood'] - 1,None,None,None,None]
                                i += 1
                            else:
                                pass
                        
                        pistol_change = pistol_change.sort_values('tick').reset_index(drop = True)
                        pistol_change['phase'] = pistol_change['phase'].bfill()
                        pistol_change['t_upg_pistol'] = pistol_change.groupby('phase')['t_upg_pistol'].ffill()
                        pistol_change['ct_upg_pistol'] = pistol_change.groupby('phase')['ct_upg_pistol'].ffill()
                        pistol_change = pistol_change[['tick','round','t_upg_pistol','ct_upg_pistol']]
                        
                        
                        
                        
                        grenade_change = item_change.loc[(item_change['event'] == 'player_hurt') | ((pd.isnull(item_change['primary_class']) == True) & (item_change['event'] != 'armor_purchase')),['tick','round','phase','life_seq','event','steamid','side']]
                        for steamid in list(grenade_change['steamid'].drop_duplicates()):
                            for life_seq in range(0,int(max(grenade_change['life_seq'])) + 1):
                                i = 1
                                g_count = 0
                                for index,row in grenade_change.loc[(grenade_change['steamid'] == steamid) & (grenade_change['life_seq'] == life_seq)].iterrows():
                                    if (i == 1) and (row['event'] == 'player_hurt'):
                                        grenade_change.set_value(index, 'player_grenade', 0)
                                    elif row['event'] in ['item_purchase','item_pickup','weapon_fire']:
                                        if row['event'] == 'weapon_fire':
                                            grenade_change.set_value(index, 'player_grenade', -1)
                                            g_count -= 1
                                            i += 1
                                        else:
                                            if g_count < 4:
                                                grenade_change.set_value(index, 'player_grenade', 1)
                                                g_count += 1
                                            else:
                                                grenade_change.set_value(index, 'player_grenade', 0)
                                            i += 1
                                    else:
                                        grenade_change.set_value(index, 'player_grenade', -1*g_count)
                        
                        grenade_change['t_grenade'] = grenade_change.loc[grenade_change['side'] == 2].groupby('phase')['player_grenade'].cumsum()
                        grenade_change['t_grenade'] = grenade_change['t_grenade'].ffill().fillna(0)
                        grenade_change['ct_grenade'] = grenade_change.loc[grenade_change['side'] == 3].groupby('phase')['player_grenade'].cumsum()
                        grenade_change['ct_grenade'] = grenade_change['ct_grenade'].ffill().fillna(0)
                        grenade_change = grenade_change[['tick','round','phase','t_grenade','ct_grenade']]
                        
                        i = 1
                        for index, row in rounds.loc[rounds['round'] != 0].iterrows():
                            if len(grenade_change.loc[(row['start'] <= grenade_change['tick']) & (grenade_change['tick'] < row['first_blood'])]) == 0:
                                grenade_change.loc[max(grenade_change.index) + i] = [row['first_blood'] - 1,None,None,None,None]
                                i += 1
                            else:
                                pass
                        
                        grenade_change = grenade_change.sort_values('tick').reset_index(drop = True)
                        grenade_change['phase'] = grenade_change['phase'].bfill()
                        grenade_change['t_grenade'] = grenade_change.groupby('phase')['t_grenade'].ffill()
                        grenade_change['ct_grenade'] = grenade_change.groupby('phase')['ct_grenade'].ffill()
                        grenade_change = grenade_change[['tick','round','t_grenade','ct_grenade']]
                        
                        
                        armor_change = item_change.loc[(item_change['event'] == 'player_hurt') | (item_change['event'] == 'armor_purchase'),['tick','round','phase','life_seq','event','steamid','side']]
                        for steamid in list(armor_change['steamid'].drop_duplicates()):
                            for life_seq in range(0,int(max(armor_change['life_seq'])) + 1):
                                i = 1
                                armor_count = 0
                                for index,row in armor_change.loc[(armor_change['steamid'] == steamid) & (armor_change['life_seq'] == life_seq)].iterrows():
                                    if (i == 1) and (row['event'] == 'player_hurt'):
                                        armor_change.set_value(index, 'player_armor', 0)
                                        armor_change.set_value(index, 'armor_count', armor_count)
                                    elif row['event'] == 'armor_purchase':
                                        if armor_count == 0:
                                            armor_change.set_value(index, 'player_armor', 1)
                                            armor_change.set_value(index, 'armor_count', armor_count)
                                            armor_count = 1
                                            i += 1
                                        else:
                                            armor_change.set_value(index, 'player_armor', 0)
                                            armor_change.set_value(index, 'armor_count', armor_count)
                                            i += 1
                                    else:
                                        if armor_count == 1:
                                            armor_change.set_value(index, 'player_armor', -1)
                                            armor_change.set_value(index, 'armor_count', armor_count)
                                            i += 1
                                        else:
                                            armor_change.set_value(index, 'player_armor', 0)
                                            armor_change.set_value(index, 'armor_count', armor_count)
                                            i += 1
                        
                        armor_change['t_armor'] = armor_change.loc[armor_change['side'] == 2].groupby('phase')['player_armor'].cumsum()
                        armor_change['t_armor'] = armor_change['t_armor'].ffill().fillna(0)
                        armor_change['ct_armor'] = armor_change.loc[armor_change['side'] == 3].groupby('phase')['player_armor'].cumsum()
                        armor_change['ct_armor'] = armor_change['ct_armor'].ffill().fillna(0)
                        armor_change = armor_change[['tick','round','phase','t_armor','ct_armor']]
                        
                        i = 1
                        for index, row in rounds.loc[rounds['round'] != 0].iterrows():
                            if len(armor_change.loc[(row['start'] <= armor_change['tick']) & (armor_change['tick'] < row['first_blood'])]) == 0:
                                armor_change.loc[max(armor_change.index) + i] = [row['first_blood'] - 1,None,None,None,None]
                                i += 1
                            else:
                                pass
                        
                        armor_change = armor_change.sort_values('tick').reset_index(drop = True)
                        armor_change['phase'] = armor_change['phase'].bfill()
                        armor_change['t_armor'] = armor_change.groupby('phase')['t_armor'].ffill()
                        armor_change['ct_armor'] = armor_change.groupby('phase')['ct_armor'].ffill()
                        armor_change = armor_change[['tick','round','t_armor','ct_armor']]
                    
                        econ_kill = data.loc[data['health'] == 0,['tick','steamid','event','side','attacker','weapon']].rename(index = str, columns = {'steamid':'player'})
                        econ_kill = pd.merge(econ_kill,data.loc[(pd.isnull(data['steamid']) == False) & (data['event'] == 'player_connect'),['userid','steamid']].drop_duplicates(),how = 'left', left_on = 'attacker', right_on = 'userid')[['tick','player','event','side','steamid','weapon']].rename(index = str, columns = {'steamid':'attacker'})
                        econ_kill = pd.merge(econ_kill, players[['steamid','team']], how = 'left', left_on = 'player', right_on = 'steamid').rename(index = str, columns = {'team':'player_team'})
                        econ_kill = pd.merge(econ_kill, players[['steamid','team']], how = 'left', left_on = 'attacker', right_on = 'steamid').rename(index = str, columns = {'team':'attacker_team'})
                        econ_kill = pd.merge(econ_kill,weapon_data[['weapon','kill']], how = 'left', on = 'weapon')
                        for index, row in econ_kill.iterrows():
                            if row['side'] == 2:
                                if row['player_team'] == row['attacker_team']:
                                    econ_kill.set_value(index,'t_econ_change', -3300)
                                    econ_kill.set_value(index,'ct_econ_change', 0)
                                else:
                                    econ_kill.set_value(index,'t_econ_change', 0)
                                    econ_kill.set_value(index,'ct_econ_change', row['kill'])
                            else:
                                if row['player_team'] == row['attacker_team']:
                                    econ_kill.set_value(index,'ct_econ_change', -3300)
                                    econ_kill.set_value(index,'t_econ_change', 0)
                                else:
                                    econ_kill.set_value(index,'ct_econ_change', 0)
                                    econ_kill.set_value(index,'t_econ_change', row['kill'])
                        econ_kill = econ_kill[['tick','event','side','t_econ_change','ct_econ_change']]
        
                        econ_outcome = rounds[['round','end']].rename(index = str, columns = {'end': 'tick'})
                        econ_outcome['event'] = 'true_round_end'
        
                        econ_bomb = data.loc[data['event'].isin(['bomb_planted','bomb_defused']),['tick','event']]
                        if len(econ_bomb) > 0:
                            for index, row in econ_bomb.iterrows():
                                if row['event'] == 'bomb_planted':
                                    econ_bomb.set_value(index,'ct_econ_change', 0)
                                    econ_bomb.set_value(index,'t_econ_change', 300)
                                else:
                                    econ_bomb.set_value(index,'t_econ_change', 0)
                                    econ_bomb.set_value(index,'ct_econ_change', 300)
                            econ_bomb = econ_bomb[['tick','event','t_econ_change','ct_econ_change']]
                            
                            econ = pd.concat([econ_kill,econ_bomb,econ_outcome]).sort_values('tick').reset_index(drop = True)
                        else:
                            econ = pd.concat([econ_kill,econ_outcome]).sort_values('tick').reset_index(drop = True)
                        for index, row in econ.iterrows():
                            for index2, row2 in rounds.iterrows():
                                if row2['start'] <= row['tick'] <= row2['end']:
                                    econ.set_value(index,'round',row2['round'])
                                    econ.set_value(index,'reason',row2['reason'])
                                    econ.set_value(index,'round_decision',row2['round_decision'])
                                    break
                        econ = econ.loc[pd.isnull(econ['round']) == False]
                        econ[['round']] = econ[['round']].bfill()
                        econ = econ[['tick','round','round_decision','event','side','reason','t_econ_change','ct_econ_change']]
                        
                        prev_rnd = None
                        for index, row in econ.iterrows():
                            if prev_rnd == None or row['round'] != prev_rnd:
                                pre_end_deaths = 0
                            if row['event'] == 'player_hurt' and row['side'] == 2 and row['reason'] == 12 and row['tick'] <= row['round_decision']:
                                pre_end_deaths += 1
                            elif row['event'] == 'true_round_end':
                                if row['reason'] == 12:
                                    econ.set_value(index,'t_econ_change',1400*(pre_end_deaths))
                                    econ.set_value(index,'ct_econ_change',3250*5)
                                elif row['reason'] == 7:
                                    econ.set_value(index,'t_econ_change',2200*5)
                                    econ.set_value(index,'ct_econ_change',3500*5)
                                elif row['reason'] == 8:
                                    econ.set_value(index,'t_econ_change',1400*5)
                                    econ.set_value(index,'ct_econ_change',3250*5)
                                elif row['reason'] == 1:
                                    econ.set_value(index,'t_econ_change',3500*5)
                                    econ.set_value(index,'ct_econ_change',1400*5)
                                else:
                                    econ.set_value(index,'t_econ_change',3250*5)
                                    econ.set_value(index,'ct_econ_change',1400*5)
                            prev_rnd = row['round']
                                
                        econ['t_econ'] = econ.groupby('round')['t_econ_change'].cumsum()
                        econ['ct_econ'] = econ.groupby('round')['ct_econ_change'].cumsum()
                        econ['ct_econ_result'] = econ['ct_econ'] - econ['t_econ']
                        econ = econ.loc[econ['event'] == 'true_round_end',['round','ct_econ_result']]
                    
                        rounds = pd.merge(rounds, econ, how = 'left', on = 'round')
                        
                        for index, row in rounds.loc[rounds['round'] > 0].iterrows():
                            primary_start = primary_change.loc[(row['start'] <= primary_change['tick']) & (primary_change['tick'] < row['first_blood'])].max()
                            rounds.set_value(index,'t_t1_rifle',primary_start['t_t1_rifle'])
                            rounds.set_value(index,'t_t2_rifle',primary_start['t_t2_rifle'])
                            rounds.set_value(index,'t_other_primary',primary_start['t_other_primary'])
                            rounds.set_value(index,'ct_t1_rifle',primary_start['ct_t1_rifle'])
                            rounds.set_value(index,'ct_t2_rifle',primary_start['ct_t2_rifle'])
                            rounds.set_value(index,'ct_other_primary',primary_start['ct_other_primary'])
                            primary_end_tick = primary_change.loc[primary_change['round'] == row['round'],'tick'].max()
                            primary_end = primary_change.loc[primary_change['tick'] == primary_end_tick].max()
                            rounds.set_value(index,'t_t1_rifle_end',primary_end['t_t1_rifle'])
                            rounds.set_value(index,'t_t2_rifle_end',primary_end['t_t2_rifle'])
                            rounds.set_value(index,'t_other_primary_end',primary_end['t_other_primary'])
                            rounds.set_value(index,'ct_t1_rifle_end',primary_end['ct_t1_rifle'])
                            rounds.set_value(index,'ct_t2_rifle_end',primary_end['ct_t2_rifle'])
                            rounds.set_value(index,'ct_other_primary_end',primary_end['ct_other_primary'])
                            
                            pistol_start = pistol_change.loc[(row['start'] <= pistol_change['tick']) & (pistol_change['tick'] < row['first_blood'])].max()
                            rounds.set_value(index,'t_upg_pistol',pistol_start['t_upg_pistol'])
                            rounds.set_value(index,'ct_upg_pistol',pistol_start['ct_upg_pistol'])
                            pistol_end_tick = pistol_change.loc[pistol_change['round'] == row['round'],'tick'].max()
                            pistol_end = pistol_change.loc[pistol_change['tick'] == pistol_end_tick].max()
                            rounds.set_value(index,'t_upg_pistol_end',pistol_end['t_upg_pistol'])
                            rounds.set_value(index,'ct_upg_pistol_end',pistol_end['ct_upg_pistol'])
                            
                            grenade_start = grenade_change.loc[(row['start'] <= grenade_change['tick']) & (grenade_change['tick'] < row['first_blood'])].max()
                            rounds.set_value(index,'t_grenade',grenade_start['t_grenade'])
                            rounds.set_value(index,'ct_grenade',grenade_start['ct_grenade'])
                            grenade_end_tick = grenade_change.loc[grenade_change['round'] == row['round'],'tick'].max()
                            grenade_end = grenade_change.loc[grenade_change['tick'] == grenade_end_tick].max()
                            rounds.set_value(index,'t_grenade_end',grenade_end['t_grenade'])
                            rounds.set_value(index,'ct_grenade_end',grenade_end['ct_grenade'])
                            
                            armor_start = armor_change.loc[(row['start'] <= armor_change['tick']) & (armor_change['tick'] < row['first_blood'])].max()
                            rounds.set_value(index,'t_armor',armor_start['t_armor'])
                            rounds.set_value(index,'ct_armor',armor_start['ct_armor'])
                            armor_end_tick = armor_change.loc[armor_change['round'] == row['round'],'tick'].max()
                            armor_end = armor_change.loc[armor_change['tick'] == armor_end_tick].max()
                            rounds.set_value(index,'t_armor_end',armor_end['t_armor'])
                            rounds.set_value(index,'ct_armor_end',armor_end['ct_armor'])
                            
                            
                        
                        rounds.update(rounds.loc[rounds['round'] != 0,['t_t1_rifle','t_t2_rifle','t_other_primary','ct_t1_rifle','ct_t2_rifle','ct_other_primary','t_upg_pistol','ct_upg_pistol','t_grenade','ct_grenade','t_armor','ct_armor','t_t1_rifle_end','t_t2_rifle_end','t_other_primary_end','ct_t1_rifle_end','ct_t2_rifle_end','ct_other_primary_end','t_upg_pistol_end','ct_upg_pistol_end','t_grenade_end','ct_grenade_end','t_armor_end','ct_armor_end']].fillna(0))
                        rounds['t_t1_rifle_econ_change'] = (rounds['t_t1_rifle_end'] - rounds['t_t1_rifle'])*2700
                        rounds['ct_t1_rifle_econ_change'] = (rounds['ct_t1_rifle_end'] - rounds['ct_t1_rifle'])*3100
                        rounds['t_t2_rifle_econ_change'] = (rounds['t_t2_rifle_end'] - rounds['t_t2_rifle'])*2000
                        rounds['ct_t2_rifle_econ_change'] = (rounds['ct_t2_rifle_end'] - rounds['ct_t2_rifle'])*2250
                        rounds['t_other_primary_econ_change'] = (rounds['t_other_primary_end'] - rounds['t_other_primary'])*1200
                        rounds['ct_other_primary_econ_change'] = (rounds['ct_other_primary_end'] - rounds['ct_other_primary'])*1200
                        rounds['t_upg_pistol_econ_change'] = (rounds['t_upg_pistol_end'] - rounds['t_upg_pistol'])*300
                        rounds['ct_upg_pistol_econ_change'] = (rounds['ct_upg_pistol_end'] - rounds['ct_upg_pistol'])*300
                        rounds['t_armor_econ_change'] = (rounds['t_armor_end'] - rounds['t_armor'])*600
                        rounds['ct_armor_econ_change'] = (rounds['ct_armor_end'] - rounds['ct_armor'])*600
                        rounds['ct_econ_equip'] = (rounds['ct_t1_rifle_econ_change'] + rounds['ct_t2_rifle_econ_change'] + rounds['ct_other_primary_econ_change'] + rounds['ct_upg_pistol_econ_change'] + rounds['ct_armor_econ_change']) - (rounds['t_t1_rifle_econ_change'] + rounds['t_t2_rifle_econ_change'] + rounds['t_other_primary_econ_change'] + rounds['t_upg_pistol_econ_change'] + rounds['t_armor_econ_change'])
                        rounds = rounds.drop_duplicates()
                        rounds.insert(0, 'mapid', file_[:-5])
                        
                        with open('csv\\match_info.csv', 'ab') as infocsv:
                            match_info.to_csv(infocsv, header = False, index = False)
                        
                        with open('csv\\match_players.csv', 'ab') as playercsv:
                            players.to_csv(playercsv, header = False, index = False)
    
                        try:
                            with open('csv\\match_knife_results.csv', 'ab') as knifecsv:
                                rounds.loc[rounds['round'] == 0,['mapid','round','t_team','ct_team','winner']].to_csv(knifecsv, header = False, index = False)
                        except:
                            pass
                        
                        with open('csv\\match_pistol_results.csv', 'ab') as pistolcsv:
                            rounds.loc[rounds['round'].isin([1,16]),['mapid','round','t_team','ct_team','winner','ct_econ_result','ct_econ_equip','t_upg_pistol','ct_upg_pistol','t_grenade','ct_grenade','t_armor','ct_armor']].to_csv(pistolcsv, header = False, index = False)
                            
                        with open('csv\\match_primary_results.csv', 'ab') as primarycsv:
                            rounds.loc[~rounds['round'].isin([0,1,16]),['mapid','round','t_team','ct_team','winner','ct_econ_result','ct_econ_equip','t_t1_rifle','t_t2_rifle','t_other_primary','ct_t1_rifle','ct_t2_rifle','ct_other_primary','t_upg_pistol','ct_upg_pistol','t_grenade','ct_grenade','t_armor','ct_armor']].to_csv(primarycsv, header = False, index = False)
    
                    except Exception as e:
                        error_msg = str(e)
                        with open('csv\\csv_fails.csv', 'ab') as csvfailcsv:
                            csvfailwriter = csv.writer(csvfailcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                            csvfailwriter.writerow([eventid,file_[:-5],error_msg])