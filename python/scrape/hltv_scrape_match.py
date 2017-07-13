from __future__ import division
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import datetime
import csv

def match():
    print('########## scrape matches ##########')
    try:
        exist_events = list(pd.read_csv('csv\\hltv_match_info.csv', header = None)[0])
    except:
        exist_events = pd.DataFrame(index = range(0), columns = [0,1])
        
    hltv_events = list(pd.read_csv('csv\\hltv_events.csv', header = None)[0])
    
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    
    for event_href in reversed(hltv_events):
        if event_href not in exist_events:
            eventid = re.compile('(?<=events\/)[0-9]{1,}(?=\/)').search(event_href).group(0)
            
            event_results_url = 'https://www.hltv.org/results?event=' + eventid
            event_results_req = requests.get(event_results_url, headers = header)
            event_results_soup = BeautifulSoup(event_results_req.content,'lxml').find_all('div', {'class': 'results-all'})
            match_hrefs = BeautifulSoup(str(event_results_soup),'lxml').find_all('a', {'class': 'a-reset'})
            print(event_href + ', ' + str(len(match_hrefs)))
            for match_href in match_hrefs:
                match_url = 'https://www.hltv.org' + match_href.get('href')
                match_req = requests.get(match_url, headers = header)
                match_soup = BeautifulSoup(match_req.content,'lxml')
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
                    matchwriter.writerow([event_href, match_href.get('href'), match_demo, match_datetime_utc, match_team1_name, match_team1_href, match_team2_name, match_team2_href])
                
                match_veto_box = match_soup.find_all('div', {'class': 'standard-box veto-box'})
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
                        map_ = re.compile('nuke|cobble|mirage|inferno|cache|dust( )*2|overpass|train', re.I).search(veto_step.encode('utf-8')).group(0)
                        with open("csv\\hltv_vetos.csv", 'ab') as vetocsv:
                            vetowriter = csv.writer(vetocsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                            vetowriter.writerow([match_href.get('href'), step, team, action, map_])
                        i += 1
                
                map_results = match_soup.find_all('div', {'class': 'mapholder'})
                for map_ in map_results:
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
                            resultwriter.writerow([match_href.get('href'), map_name, match_team1_href, team1_rounds, match_team2_href, team2_rounds, result, abs_result])
                    except:
                        pass
        else:
            return
        
match()