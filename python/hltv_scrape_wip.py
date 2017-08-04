from __future__ import division
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import math
import datetime
import csv

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 \
    Safari/537.36'}


def rank_data():
    print('### Team Ranks ###')
    try:
        exist_ranks = list(pd.read_csv('csv\\hltv_team_ranks.csv', header = None)[0].drop_duplicates())
    except:
        exist_ranks = pd.DataFrame(index = range(0))
    
    recent_rank_page_req = requests.get('https://www.hltv.org/ranking/teams', headers = header)
    year_hrefs = BeautifulSoup(recent_rank_page_req.content, 'lxml').find_all('div', {'class': 'filter-column-content'})[0].contents
    
    date_list = []
    
    for year_href in reversed(year_hrefs):
        year_url = 'https://www.hltv.org' + year_href.get('href')
        year_req = requests.get(year_url, headers = header)
        month_hrefs = BeautifulSoup(year_req.content, 'lxml').find_all('div', {'class': 'filter-column-content'})[1].contents
        for month_href in reversed(month_hrefs):
            month_url = 'https://www.hltv.org' + month_href.get('href')
            month_req = requests.get(month_url, headers = header)
            day_hrefs = BeautifulSoup(month_req.content, 'lxml').find_all('div', {'class': 'filter-column-content'})[2].contents
            for day_href in reversed(day_hrefs):
                day_url = 'https://www.hltv.org' + day_href.get('href')
                day_req = requests.get(day_url, headers = header)
                year = re.compile('(?<=teams\/)[0-9]{4}(?=\/)').search(day_url).group(0)
                month = str(datetime.datetime.strptime(re.compile('(?<=20[0-9]{2}\/).*(?=\/)').search(day_url).group(0), '%B').month)
                day = re.compile('[0-9]{1,2}$').search(day_url).group(0)
                date = month + '/' + day + '/' + year
                if date in list(list(exist_ranks) + date_list):
                    return
                else:
                    date_list.append(date)
                    team_rows = BeautifulSoup(day_req.content, 'lxml').find_all('div', {'class': 'ranked-team standard-box'})
                    for team in team_rows:
                        rank = int(re.sub('#','',team.contents[1].contents[1].contents[0].text.encode('utf-8')))
                        team_href = team.contents[1].contents[1].contents[2].get('data-url')
                        team_name = team.contents[1].contents[1].contents[2].text.encode('utf-8')
                        team_points = int(re.sub('[a-z]|\(|\)| ','',team.contents[1].contents[1].contents[3].text.encode('utf-8')))
                        with open("csv\\hltv_team_ranks.csv", 'ab') as rankcsv:
                            rankwriter = csv.writer(rankcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                            rankwriter.writerow([date,rank,team_name,team_href,team_points])
                print('\t' + 'Added: ' + date)

rank_data()

def event_data():
    print('### Events ###')
    
    ranks = pd.read_csv('csv\\hltv_team_ranks.csv', header = None)
    rank_min_date = min(pd.to_datetime(ranks[0].drop_duplicates()).sort_values(0))
    
    try:
        exist_events = list(pd.read_csv('csv\\hltv_events.csv', header = None)[0])
    except:
        exist_events = []
        
    try:
        exist_team_places = set(pd.read_csv('csv\\hltv_team_places.csv', header = None)[0])
    except:
        exist_team_places = {}
    
    initial_archive_page_req = requests.get('https://www.hltv.org/events/archive?eventType=MAJOR&eventType=INTLLAN', headers = header)
    try:
        initial_archive_page_soup = BeautifulSoup(initial_archive_page_req.content, 'lxml').find_all('div', {'class': 
            'pagination-component pagination-top '})
    except:
        initial_archive_page_soup = BeautifulSoup(initial_archive_page_req.content, 'lxml').find_all('div', {'class': 
            'pagination-component pagination-top'})
    pagination_string = initial_archive_page_soup[0].contents[0].encode('utf-8')
    page_results = int(re.compile('(?<= - )[0-9]{1,}(?= of )').search(pagination_string).group(0))
    total_results = int(re.compile('(?<= of )[0-9]{1,}').search(pagination_string).group(0))
    num_pages = 1 + int(math.ceil((total_results - page_results)/page_results))
    
    prev_month = None    
    prev_event = None
    
    for page in reversed(range(0,num_pages)):
        offset = page*50
        archive_page_url = 'https://www.hltv.org/events/archive?offset=' + str(offset) + '&eventType=MAJOR&eventType=INTLLAN'
        archive_page_req = requests.get(archive_page_url, headers = header)
        archive_page_soup = BeautifulSoup(archive_page_req.content, 'html5lib').find('div', {'class': 'contentCol'})
        months = BeautifulSoup(str(archive_page_soup),'lxml').find_all('div', {'class': 'events-month'})
        for month in reversed(months):
            if datetime.datetime.strptime(month.contents[1].contents[0].strip(), '%B %Y') >= rank_min_date:
                if month.contents[1].contents[0].strip() != prev_month:
                    print('\t' + month.contents[1].contents[0].strip())
                    prev_month = month.contents[1].contents[0].strip()
                
                events = BeautifulSoup(str(month),'lxml').find_all('a', {'class': 'a-reset small-event standard-box'})
                for event in reversed(events):
                    if (event.get('href') not in exist_events) | (event.get('href') not in exist_team_places):
                        event_href = event.get('href')
                        event_name = event.contents[2].contents[1].contents[1].contents[0].contents[1].text.encode('utf-8').strip()
                        event_req = requests.get('https://www.hltv.org' + event_href, headers = header)
                        
                        event_date = BeautifulSoup(event_req.content,'lxml').find_all('td', {'class': 'eventdate'})
                        event_start = datetime.datetime.utcfromtimestamp(
                            int(event_date[1].contents[0].get('data-unix'))/1000).strftime('%m/%d/%Y')
                        try:
                            event_end = datetime.datetime.utcfromtimestamp(
                                int(event_date[1].contents[1].contents[1].get('data-unix'))/1000).strftime('%m/%d/%Y')
                        except:
                            event_end = event_start
                        
                        for rank_dt in reversed(list(pd.to_datetime(ranks[0].drop_duplicates()).sort_values(0))):
                            if rank_dt < pd.to_datetime(event_start):
                                hltv_rank_teams = list(ranks.loc[ranks[0] == re.sub('^0(?=[0-9])|(?<=\/)0(?=[0-9])','',
                                                                 rank_dt.strftime('%m/%d/%Y')),3])
                                break
                        
                        event_teams_place = BeautifulSoup(event_req.content,'lxml').find_all('div', {'class': 'placement'})
                        for team in event_teams_place:
                            try:
                                team.contents[1].contents[1].get('href')
                            except:
                                continue
                            
                            if team.contents[1].contents[1].get('href') in hltv_rank_teams:
                                if event_href not in exist_events:
                                    if event_href != prev_event:
                                        print('\t\t' + event_href)
                                        prev_event = event_href
                                    
                                    results_href = 'results?event=' + re.compile('(?<=events\/)[0-9]{1,}(?=\/)').search(event_href)\
                                        .group(0)
                                    results_req = requests.get('https://www.hltv.org/' + results_href, headers = header)
                                    result_rows = len(BeautifulSoup(results_req.content,'lxml').find_all('div', {'class': 'result-con'}))
                                    event_type = event.contents[2].contents[1].contents[1].contents[0].contents[7].text.encode('utf-8')
                                    with open("csv\\hltv_events.csv", 'ab') as eventcsv:
                                        eventwriter = csv.writer(eventcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                        eventwriter.writerow([event_href,event_name,event_end,event_type, result_rows])
                                
                                if event_href not in exist_team_places:
                                    if event_href != prev_event:
                                        print('\t\t' + event_href)
                                        prev_event = event_href
                                        
                                    for team in event_teams_place:
                                        team_href = team.contents[1].contents[1].get('href')
                                        try:
                                            place = int(re.findall(r'\d+',team.contents[3].text.split('-')[0])[0])
                                        except:
                                            place = int(re.findall(r'\d+',team.contents[3].text)[0])
                                        try:
                                            winnings = int(re.sub('\$|,','',team.contents[5].text))
                                        except:
                                            if event.contents[2].contents[1].contents[1].contents[0].contents[5].text.encode('utf-8') \
                                                    == 'Other':
                                                winnings = None
                                            else:
                                                winnings = 0
                                        with open("csv\\hltv_team_places.csv", 'ab') as teamplacecsv:
                                            teamplacewriter = csv.writer(teamplacecsv, delimiter = ',', quotechar = '"',
                                                                         quoting = csv.QUOTE_MINIMAL)
                                            teamplacewriter.writerow([event_href,team_href,place,winnings])
                                
                                break
                
event_data()


def match_data():
    print('### Matches ###')
    
    scraped_events = pd.read_csv('csv\\hltv_events.csv', header = None)
    
    try:
        exist_match_info = pd.read_csv('csv\\hltv_match_info.csv', header = None)
    except:
        exist_match_info = pd.DataFrame(index = range(0), columns = [0,1])

    try:
        exist_vetos = pd.read_csv('csv\\hltv_vetos.csv', header = None)
    except:
        exist_vetos = pd.DataFrame(index = range(0), columns = [0])
    
    map_search_re = 'nuke|c(o)*bble|mirage|inferno|cache|dust( )*2|overpass|train'
    veto_words_re = 'remove|pick|remain|left|veto|choose|ban'
        
    try:
        exist_player_stats = pd.read_csv('csv\\hltv_player_stats.csv', header = None)
    except:
        exist_player_stats = pd.DataFrame(index = range(0), columns = [0])
    
    try:
        exist_map_results = pd.read_csv('csv\\hltv_map_results.csv', header = None)
    except:
        exist_map_results = pd.DataFrame(index = range(0), columns = [0])
        
    try:
        exist_map_rounds = pd.read_csv('csv\\hltv_map_rounds.csv', header = None)
    except:
        exist_map_rounds = pd.DataFrame(index = range(0), columns = [0])
    
    match_iterator = pd.DataFrame(index = range(0), columns = [0,1,2,3,4,5,6])
    
    for index, row in scraped_events.iterrows():
        event_href = row[0]
        if len(exist_match_info.loc[exist_match_info[0] == event_href,1].drop_duplicates()) < row[4]:
            results_href = 'results?event=' + re.compile('(?<=events\/)[0-9]{1,}(?=\/)').search(event_href).group(0)
            results_req = requests.get('https://www.hltv.org/' + results_href, headers = header)
            result_rows = BeautifulSoup(results_req.content,'lxml').find_all('div', {'class': 'result-con'})
            for match in result_rows:
                match_href = match.contents[0].get('href')
                if match_href in list(exist_match_info[1]):
                    match_iterator.loc[len(match_iterator)] = [None,match_href,0,0,0,0,0]
                else:
                    match_iterator.loc[len(match_iterator)] = [event_href,match_href,1,0,0,0,0]
        else:
            for match_href in set(exist_match_info.loc[exist_match_info[0] == event_href,1]):
                match_iterator.loc[len(match_iterator)] = [None,match_href,0,0,0,0,0]
                
    for match_href in set(match_iterator[1]):
        if match_href not in set(exist_vetos[0]):
            match_iterator.loc[match_iterator[1] == match_href,3] = 1
        if match_href not in set(exist_player_stats[0]):
            match_iterator.loc[match_iterator[1] == match_href,4] = 1
        if match_href not in set(exist_map_results[0]):
            match_iterator.loc[match_iterator[1] == match_href,5] = 1
        if match_href not in set(exist_map_rounds[0]):
            match_iterator.loc[match_iterator[1] == match_href,6] = 1
            
    prev_match = None
            
    for index, row in match_iterator.loc[match_iterator.sum(axis = 1) > 0].iterrows():
        event_href = row[0]        
        match_href = row[1]
        match_req = requests.get('https://www.hltv.org' + match_href, headers = header)
        match_soup = BeautifulSoup(match_req.content,'lxml')
        
        if (row[2] == 1) | (row[5] == 1) | (row[6] == 1):
            if match_href != prev_match:
                print('\t' + match_href)
                prev_match = match_href
                
            try:
                match_team1_name = match_soup.find_all('div', {'class': 'teamName'})[0].text.encode('utf-8').strip()
                try:
                    match_team1_href = match_soup.find_all('a', {'class': 'teamName'})[0].get('href')
                except:
                    match_team1_href = None
                match_team2_name = match_soup.find_all('div', {'class': 'teamName'})[1].text.encode('utf-8').strip()
                match_team2_href = match_soup.find_all('a', {'class': 'teamName'})[1].get('href')
                match_unix_time = int(match_soup.find_all('div', {'class': 'timeAndEvent'})[0].contents[1].get('data-unix'))/1000
                match_datetime_utc = datetime.datetime.utcfromtimestamp(match_unix_time).isoformat()
                try:
                    match_demo_pt1 = BeautifulSoup(str(match_soup.find_all('div', {'class': 'match-page'})), 'lxml')
                    match_demo = match_demo_pt1.find_all('a', {'href': re.compile('demo')})[0].get('href')
                except:
                    match_demo = None
                if row[2] == 1:
                    with open("csv\\hltv_match_info.csv", 'ab') as matchcsv:
                        matchwriter = csv.writer(matchcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                        matchwriter.writerow([event_href, match_href, match_demo, match_datetime_utc,
                                              match_team1_name, match_team1_href, match_team2_name, match_team2_href])
            except:
                if row[2] == 1:
                    with open("csv\\hltv_match_info.csv", 'ab') as matchcsv:
                        matchwriter = csv.writer(matchcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                        matchwriter.writerow([event_href, match_href, None, None, None, None, None, None])
        
        if row[3] == 1:
            if match_href != prev_match:
                print('\t' + match_href)
                prev_match = match_href
                
            match_veto_box = match_soup.find_all('div', {'class': 'standard-box veto-box'})
                        
            match_veto_process = None
            for box in range(0,len(match_veto_box)):
                if re.compile(map_search_re, re.I).search(str(match_veto_box[box])):
                    try:
                        match_veto_process = match_veto_box[box].text.split('\n')
                        break
                    except:
                        for box2 in range(0,len(match_veto_box[box].contents)):
                            if re.compile(map_search_re, re.I).search(str(match_veto_box[box].contents[box2])):
                                try:
                                    match_veto_process = match_veto_box[box].contents[box2].text.split('\n')
                                    break
                                except:
                                    for box3 in range(0,len(match_veto_box[box].contents[box2])):
                                        if re.compile(map_search_re, re.I).search(str(match_veto_box[box].contents[box2].contents[box3])):
                                            try:
                                                match_veto_process = match_veto_box[box].contents[box2].contents[box3].text.split('\n')
                                                break
                                            except:
                                                pass
            if not match_veto_process == None:
                for veto_step in match_veto_process:
                        i = 1
                        if re.compile(veto_words_re).search(veto_step.encode('utf-8')):
                            try:
                                step = int(veto_step.encode('utf-8')[0])
                            except:
                                step = i
                            try:
                                if re.compile('random|decider').search(veto_step.encode('utf-8')):
                                    team = None
                                    action = None
                                else:
                                    team = re.sub('^[0-9]\.( )*','',re.compile('.*(?= ' + veto_words_re + ')').search(
                                        veto_step.encode('utf-8')).group(0)).encode('utf-8').strip()
                                    action = re.compile(veto_words_re).search(veto_step.encode('utf-8')).group(0)
                            except:
                                team = None
                                action = None
                            try:
                                map_ = re.compile(map_search_re, re.I).search(veto_step.encode('utf-8')).group(0)
                            except:
                                continue
                            with open("csv\\hltv_vetos.csv", 'ab') as vetocsv:
                                vetowriter = csv.writer(vetocsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                vetowriter.writerow([match_href, step, team, action, map_])
                            i += 1
            else:
                with open("csv\\hltv_vetos.csv", 'ab') as vetocsv:
                    vetowriter = csv.writer(vetocsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                    vetowriter.writerow([match_href, None, None, None, None])
                            
        if row[4] == 1:
            if match_href != prev_match:
                print('\t' + match_href)
                prev_match = match_href
                
            map_stats = match_soup.find_all('div', {'class': 'stats-content'})
            if not map_stats == []:
                for map_ in map_stats:
                    if map_.get('id') != 'all-content':
                        if (match_href == '/matches/2294998/atlantis-vs-puta-copenhagen-games-2015' and
                                re.compile('.*(?=[0-9]{5})').search(map_.get('id')).group(0) == 'Nuke'):
                            map_name = 'Dust2'
                        else:
                            map_name = re.compile('.*(?=[0-9]{5})').search(map_.get('id')).group(0)
                        for team in [1,3]:
                            player_rows = map_.contents[team].find_all('tr', class_=lambda x: x != 'header-row')
                            team_href = map_.contents[team].contents[1].contents[1].contents[1].contents[1].get('href')
                            for player in player_rows:
                                player_href = player.contents[1].contents[0].get('href')
                                player_name = player.contents[1].contents[0].contents[1].contents[4].text.encode('utf-8')
                                if int(player.contents[3].text.split('-')[1]) == 0:
                                    kd = int(player.contents[3].text.split('-')[0])/1
                                else:
                                    kd = int(player.contents[3].text.split('-')[0])/int(player.contents[3].text.split('-')[1])
                                with open("csv\\hltv_player_stats.csv", 'ab') as statscsv:
                                    statswriter = csv.writer(statscsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                    statswriter.writerow([match_href, map_name, team_href, player_href, player_name, kd])
            else:
                map_lineups = match_soup.find_all('div', {'class': 'lineups'})
                map_results = match_soup.find_all('div', {'class': 'mapholder'})
                for map_ in map_results:
                    map_name = map_.contents[1].contents[1].contents[2].contents[0]
                    for team in [1,3]:
                        team_href = map_lineups[0].contents[2].contents[team].contents[1].contents[1].get('href')
                        players = map_lineups[0].contents[2].contents[team].contents[3].contents[1].contents[1].find_all('td', {'class':
                            'player'})
                        for player in players:
                            player_href = player.contents[0].get('href')
                            if '\'' in player.contents[0].contents[1].contents[0].get('title'):
                                player_name = re.sub('\'','',re.compile('(?=\').*(?<=\')').search(
                                    player.contents[0].contents[1].contents[0].get('title')).group(0))
                            else:
                                player_name = re.sub(' ','',player.contents[0].contents[1].contents[0].get('title'))
                            with open("csv\\hltv_player_stats.csv", 'ab') as statscsv:
                                statswriter = csv.writer(statscsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                statswriter.writerow([match_href, map_name, team_href, player_href, player_name, None])
                                    
        if (row[5] == 1) | (row[6] == 1):
            if match_href != prev_match:
                print('\t' + match_href)
                prev_match = match_href
                
            if match_team1_href != None:
                map_results = match_soup.find_all('div', {'class': 'mapholder'})
                for map_,map_num in zip(map_results,range(1,len(map_results) + 1)):
                    if not (match_href == '/matches/2306391/gambit-vs-fnatic-academy-predator-masters-3' and
                            map_.contents[1].contents[1].contents[2].contents[0] == 'Cobblestone'):
                        try:
                            map_name = map_.contents[1].contents[1].contents[2].contents[0]
                            team1_rounds = int(map_.contents[3].contents[0].contents[0])
                            team2_rounds = int(map_.contents[3].contents[2].contents[0])
                            if team1_rounds > 16:
                                result = 0.5
                                if team1_rounds > team2_rounds:
                                    abs_result = 1
                                else:
                                    abs_result = 0
                            elif team1_rounds > team2_rounds:
                                result = 1
                                abs_result = 1
                            else:
                                result = 0
                                abs_result = 0
                                
                            if row[5] == 1:
                                with open("csv\\hltv_map_results.csv", 'ab') as resultcsv:
                                    resultwriter = csv.writer(resultcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                    resultwriter.writerow([match_href, map_num, map_name, match_team1_href, team1_rounds,
                                                           match_team2_href, team2_rounds, result, abs_result])
                            if row[6] == 1:
                                for half in [1,2]:
                                    team1_side = map_.contents[3].contents[4*half].get('class')[0]
                                    team2_side = map_.contents[3].contents[4*half + 2].get('class')[0]
                                    for t1_win in range(1,int(map_.contents[3].contents[4*half].text) + 1):
                                        with open("csv\\hltv_map_rounds.csv", 'ab') as roundcsv:
                                            roundwriter = csv.writer(roundcsv, delimiter = ',', quotechar = '"',
                                                                     quoting = csv.QUOTE_MINIMAL)
                                            roundwriter.writerow([match_href, map_num, map_name, half,
                                                                  t1_win, match_team1_href, team1_side, match_team2_href, team2_side, 1])
                                    for t2_win in range(1,int(map_.contents[3].contents[4*half + 2].text) + 1):
                                        with open("csv\\hltv_map_rounds.csv", 'ab') as roundcsv:
                                            roundwriter = csv.writer(roundcsv, delimiter = ',', quotechar = '"',
                                                                     quoting = csv.QUOTE_MINIMAL)
                                            roundwriter.writerow([match_href, map_num, map_name, half,
                                                                  t2_win, match_team1_href, team1_side, match_team2_href, team2_side, 0])
                        except:
                            if row[5] == 1:
                                with open("csv\\hltv_map_results.csv", 'ab') as resultcsv:
                                    resultwriter = csv.writer(resultcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                    resultwriter.writerow([match_href, map_num, None, None, None, None, None, None, None])
                            if row[6] == 1:
                                with open("csv\\hltv_map_rounds.csv", 'ab') as roundcsv:
                                    roundwriter = csv.writer(roundcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                    roundwriter.writerow([match_href, map_num, None, None, None, None, None, None, None, None])
                        
            else:
                if row[5] == 1:
                    with open("csv\\hltv_map_results.csv", 'ab') as resultcsv:
                        resultwriter = csv.writer(resultcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                        resultwriter.writerow([match_href, map_num, None, None, None, None, None, None, None])
                if row[6] == 1:
                    with open("csv\\hltv_map_rounds.csv", 'ab') as roundcsv:
                        roundwriter = csv.writer(roundcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                        roundwriter.writerow([match_href, map_num, None, None, None, None, None, None, None, None])
                        
match_data()