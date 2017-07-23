from __future__ import division
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import math
import datetime
import csv

def teamrank():
    print('########## scrape team ranks ##########')
    try:
        exist_ranks = list(pd.read_csv('csv\\hltv_team_ranks.csv', header = None)[0].drop_duplicates())
    except:
        exist_ranks = pd.DataFrame(index = range(0))
    
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    
    recent_rank_page_req = requests.get('https://www.hltv.org/ranking/teams', headers = header)
    year_hrefs = BeautifulSoup(recent_rank_page_req.content, 'lxml').find_all('div', {'class': 'filter-column-content'})[0].contents
    
    date_list = []
    for year_href in year_hrefs:
        year_url = 'https://www.hltv.org' + year_href.get('href')
        year_req = requests.get(year_url, headers = header)
        month_hrefs = BeautifulSoup(year_req.content, 'lxml').find_all('div', {'class': 'filter-column-content'})[1].contents
        for month_href in month_hrefs:
            month_url = 'https://www.hltv.org' + month_href.get('href')
            month_req = requests.get(month_url, headers = header)
            day_hrefs = BeautifulSoup(month_req.content, 'lxml').find_all('div', {'class': 'filter-column-content'})[2].contents
            for day_href in day_hrefs:
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
                    print(date + ', ' + str(len(team_rows)))
                    for team in team_rows:
                        rank = int(re.sub('#','',team.contents[1].contents[1].contents[0].text.encode('utf-8')))
                        team_href = team.contents[1].contents[1].contents[2].get('data-url')
                        team_name = team.contents[1].contents[1].contents[2].text.encode('utf-8')
                        team_points = int(re.sub('[a-z]|\(|\)| ','',team.contents[1].contents[1].contents[3].text.encode('utf-8')))
                        with open("csv\\hltv_team_ranks.csv", 'ab') as rankcsv:
                            rankwriter = csv.writer(rankcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                            rankwriter.writerow([date,rank,team_name,team_href,team_points])

teamrank()

def event():
    print('########## scrape events ##########')
    try:
        exist_events = list(pd.read_csv('csv\\hltv_events.csv', header = None)[0])
    except:
        exist_events = pd.DataFrame(index = range(0), columns = [0,1])
        
    try:
        ranks = pd.read_csv('csv\\hltv_team_ranks.csv', header = None)
    except:
        raise
    
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    
    initial_archive_page_req = requests.get('https://www.hltv.org/events/archive?eventType=MAJOR&eventType=INTLLAN', headers = header)
    try:
        initial_archive_page_soup = BeautifulSoup(initial_archive_page_req.content, 'lxml').find_all('div', {'class': 'pagination-component pagination-top '})
    except:
        initial_archive_page_soup = BeautifulSoup(initial_archive_page_req.content, 'lxml').find_all('div', {'class': 'pagination-component pagination-top'})
    pagination_string = initial_archive_page_soup[0].contents[0].encode('utf-8')
    page_results = int(re.compile('(?<= - )[0-9]{1,}(?= of )').search(pagination_string).group(0))
    total_results = int(re.compile('(?<= of )[0-9]{1,}').search(pagination_string).group(0))
    num_pages = 1 + int(math.ceil((total_results - page_results)/page_results))
    
    prev_month = None
    
    for page in range(0,num_pages):
        offset = page*50
        archive_page_url = 'https://www.hltv.org/events/archive?offset=' + str(offset) + '&eventType=MAJOR&eventType=INTLLAN'
        archive_page_req = requests.get(archive_page_url, headers = header)
        archive_page_soup = BeautifulSoup(archive_page_req.content, 'html5lib').find('div', {'class': 'contentCol'})
        months = BeautifulSoup(str(archive_page_soup),'lxml').find_all('div', {'class': 'events-month'})
        for month in months:
            month_year = int(re.compile('[0-9]{4}').search(month.contents[1].contents[0]).group(0))
            if month_year >= 2015:
                events = BeautifulSoup(str(month),'lxml').find_all('a', {'class': 'a-reset small-event standard-box'})
                for event in events:
                    if event.get('href') in exist_events:
                        continue
                    else:
                        if prev_month != month.contents[1].contents[0].encode('utf-8').strip():
                            print(month.contents[1].contents[0].encode('utf-8').strip() + ', ' + str(len(events)))
                            prev_month = month.contents[1].contents[0].encode('utf-8').strip()
                        
                        event_href = event.get('href')
                        event_name = event.contents[2].contents[1].contents[1].contents[0].contents[1].text.encode('utf-8').strip()
                        event_req = requests.get('https://www.hltv.org' + event_href, headers = header)
                        
                        event_date = BeautifulSoup(event_req.content,'lxml').find_all('td', {'class': 'eventdate'})
                        event_start = datetime.datetime.utcfromtimestamp(int(event_date[1].contents[0].get('data-unix'))/1000).strftime('%m/%d/%Y')
                        try:
                            event_end = datetime.datetime.utcfromtimestamp(int(event_date[1].contents[1].contents[1].get('data-unix'))/1000).strftime('%m/%d/%Y')
                        except:
                            event_end = event_start
                        
                        for rank_dt in reversed(list(pd.to_datetime(ranks[0].drop_duplicates()).sort_values(0))):
                            if rank_dt < pd.to_datetime(event_start):
                                hltv_rank_teams = list(ranks.loc[ranks[0] == re.sub('^0(?=[0-9])|(?<=\/)0(?=[0-9])','',rank_dt.strftime('%m/%d/%Y')),3])
                                break
                            
                        event_teams_place = BeautifulSoup(event_req.content,'lxml').find_all('div', {'class': 'placement'})
                        for team in event_teams_place:
                            try:
                                team.contents[1].contents[1].get('href')
                            except:
                                break
                            if team.contents[1].contents[1].get('href') in hltv_rank_teams:
                                event_type = event.contents[2].contents[1].contents[1].contents[0].contents[7].text.encode('utf-8')
                                with open("csv\\hltv_events.csv", 'ab') as eventcsv:
                                    eventwriter = csv.writer(eventcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                    eventwriter.writerow([event_href,event_name,event_end,event_type])
                                    
                                team_name_set = set()
                                for team in event_teams_place:
                                    team_name_set.add(team.contents[1].contents[1].text.encode('utf-8'))
                                    team_href = team.contents[1].contents[1].get('href')
                                    try:
                                        team_hltv_points = int(ranks.loc[(ranks[3] == team_href) & (ranks[0] == re.sub('^0(?=[0-9])|(?<=\/)0(?=[0-9])','',rank_dt.strftime('%m/%d/%Y'))),4])
                                    except:
                                        team_hltv_points = 0
                                    try:
                                        place = int(re.findall(r'\d+',team.contents[3].text.split('-')[0])[0])
                                    except:
                                        place = int(re.findall(r'\d+',team.contents[3].text)[0])
                                    try:
                                        winnings = int(re.sub('\$|,','',team.contents[5].text))
                                    except:
                                        if event.contents[2].contents[1].contents[1].contents[0].contents[5].text.encode('utf-8') == 'Other':
                                            winnings = None
                                        else:
                                            winnings = 0
                                    with open("csv\\hltv_team_places.csv", 'ab') as teamplacecsv:
                                        teamplacewriter = csv.writer(teamplacecsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                        teamplacewriter.writerow([event_href,event_end,team_href,team_hltv_points,place,winnings])
                                        
                                results_href = 'results?event=' + re.compile('(?<=events\/)[0-9]{1,}(?=\/)').search(event.get('href')).group(0)
                                results_req = requests.get('https://www.hltv.org/' + results_href, headers = header)
                                result_rows = BeautifulSoup(results_req.content,'lxml').find_all('div', {'class': 'result-con'})
                                print('\t' + event_href + ', ' + str(len(result_rows)))
                                for match in result_rows:
                                    match_href = match.contents[0].get('href')
                                    print('\t\t' + match_href)
                                    match_req = requests.get('https://www.hltv.org' + match_href, headers = header)
                                    match_soup = BeautifulSoup(match_req.content,'lxml')
                                    
                                    match_veto_box = match_soup.find_all('div', {'class': 'standard-box veto-box'})
                                    if not re.compile('tie(\-)*breaker', re.I).search(str(match_veto_box[0])):
                                        if re.compile('nuke|c(o)*bble|mirage|inferno|cache|dust( )*2|overpass|train', re.I).search(str(match_veto_box[0])):
                                            if len(match_veto_box) == 1:
                                                match_veto_process = match_veto_box[0].contents[1].contents[0].split('\n')
                                            elif len(match_veto_box) == 2:
                                                match_veto_process = match_veto_box[1].contents[1].text.split('\n')
                                            for veto_step in match_veto_process:
                                                i = 1
                                                if re.compile('remove|pick|remain|left').search(veto_step.encode('utf-8')):
                                                    try:
                                                        step = int(veto_step.encode('utf-8')[0])
                                                    except:
                                                        step = i
                                                    try:
                                                        if re.compile('random').search(veto_step.encode('utf-8')):
                                                            team = None
                                                            action = None
                                                        else:
                                                            team = re.sub('^[0-9]\. ','',re.compile('.*(?= remove|pick)').search(veto_step.encode('utf-8')).group(0)).encode('utf-8').strip()
                                                            action = re.compile('remove|pick').search(veto_step.encode('utf-8')).group(0)
                                                    except:
                                                        team = None
                                                        action = None
                                                    map_ = re.compile('nuke|c(o)*bble|mirage|inferno|cache|dust( )*2|overpass|train', re.I).search(veto_step.encode('utf-8')).group(0)
                                                    with open("csv\\hltv_vetos.csv", 'ab') as vetocsv:
                                                        vetowriter = csv.writer(vetocsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                                        vetowriter.writerow([match_href, step, team, action, map_])
                                                    i += 1
                                        
                                        try:
                                            match_team1_name = match_soup.find_all('div', {'class': 'teamName'})[0].text.encode('utf-8').strip()
                                        except:
                                            continue
                                        match_team1_href = match_soup.find_all('a', {'class': 'teamName'})[0].get('href')
                                        match_team2_name = match_soup.find_all('div', {'class': 'teamName'})[1].text.encode('utf-8').strip()
                                        match_team2_href = match_soup.find_all('a', {'class': 'teamName'})[1].get('href')
                                        match_unix_time = int(match_soup.find_all('div', {'class': 'timeAndEvent'})[0].contents[1].get('data-unix'))/1000
                                        match_datetime_utc = datetime.datetime.utcfromtimestamp(match_unix_time).isoformat()
                                        try:
                                            match_demo_pt1 = BeautifulSoup(str(match_soup.find_all('div', {'class': 'match-page'})), 'lxml')
                                            match_demo = match_demo_pt1.find_all('a', {'href': re.compile('demo')})[0].get('href')
                                        except:
                                            match_demo = None
                                        with open("csv\\hltv_match_info.csv", 'ab') as matchcsv:
                                            matchwriter = csv.writer(matchcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                            matchwriter.writerow([event_href, match_href, match_demo, match_datetime_utc, match_team1_name, match_team1_href, match_team2_name, match_team2_href])
                                                
                                        map_stats = match_soup.find_all('div', {'class': 'stats-content'})
                                        if not map_stats == []:
                                            for map_ in map_stats:
                                                if map_.get('id') != 'all-content':
                                                    if match_href == '/matches/2294998/atlantis-vs-puta-copenhagen-games-2015' and re.compile('.*(?=[0-9]{5})').search(map_.get('id')).group(0) == 'Nuke':
                                                        map_name = 'Dust2'
                                                    else:
                                                        map_name = re.compile('.*(?=[0-9]{5})').search(map_.get('id')).group(0)
                                                    for team in [1,3]:
                                                        player_rows = map_.contents[team].find_all('tr', class_=lambda x: x != 'header-row')
                                                        team_href = map_.contents[team].contents[1].contents[1].contents[1].contents[1].get('href')
                                                        for player in player_rows:
                                                            player_href = player.contents[1].contents[0].get('href')
#                                                            player_name = player.contents[1].contents[0].contents[1].contents[2].contents[1].text.encode('utf-8')
                                                            player_name = player.contents[1].contents[0].contents[1].contents[4].text.encode('utf-8')
                                                            kd = int(player.contents[3].text.split('-')[0])/int(player.contents[3].text.split('-')[1])
                                                            with open("csv\\hltv_match_stats.csv", 'ab') as statscsv:
                                                                statswriter = csv.writer(statscsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                                                statswriter.writerow([event_href, match_href, map_name, team_href, player_href, player_name, kd])
                                        else:
                                            map_lineups = match_soup.find_all('div', {'class': 'lineups'})
                                            map_results = match_soup.find_all('div', {'class': 'mapholder'})
                                            for map_ in map_results:
                                                map_name = map_.contents[1].contents[1].contents[2].contents[0]
                                                for team in [1,3]:
                                                    team_href = map_lineups[0].contents[2].contents[team].contents[1].contents[1].get('href')
                                                    players = map_lineups[0].contents[2].contents[team].contents[3].contents[1].contents[1].find_all('td', {'class':'player'})
                                                    for player in players:
                                                        player_href = player.contents[0].get('href')
                                                        if '\'' in player.contents[0].contents[1].contents[0].get('title'):
                                                            player_name = re.sub('\'','',re.compile('(?=\').*(?<=\')').search(player.contents[0].contents[1].contents[0].get('title')).group(0))
                                                        else:
                                                            player_name = re.sub(' ','',player.contents[0].contents[1].contents[0].get('title'))
                                                        with open("csv\\hltv_match_stats.csv", 'ab') as statscsv:
                                                            statswriter = csv.writer(statscsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                                            statswriter.writerow([event_href, match_href, map_name, team_href, player_href, player_name, None])
                                        
                                        map_results = match_soup.find_all('div', {'class': 'mapholder'})
                                        for map_ in map_results:
                                            if match_href == '/matches/2306391/gambit-vs-fnatic-academy-predator-masters-3' and map_.contents[1].contents[1].contents[2].contents[0] == 'Cobblestone':
                                                continue
                                            else:
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
                                                    elif team1_rounds == 16:
                                                        result = 1
                                                        abs_result = 1
                                                    else:
                                                        result = 0
                                                        abs_result = 0
                                                    with open("csv\\hltv_map_results.csv", 'ab') as resultcsv:
                                                        resultwriter = csv.writer(resultcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                                        resultwriter.writerow([match_href, map_name, match_team1_href, team1_rounds, match_team2_href, team2_rounds, result, abs_result])
                                                except:
                                                    pass
                                break

event()