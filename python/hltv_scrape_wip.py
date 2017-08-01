# -*- coding: utf-8 -*-
"""
Created on Sun Jul 30 23:01:12 2017

@author: wessonmo
"""

from __future__ import division
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import math
import datetime
import csv

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

def event():
    print('########## scrape events ##########')
    try:
        exist_events = list(pd.read_csv('csv\\hltv_events.csv', header = None)[0])
    except:
        exist_events = []
        
    try:
        ranks = pd.read_csv('csv\\hltv_team_ranks.csv', header = None)
    except:
        raise  
    
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
    
    for page in reversed(range(0,num_pages)):
        offset = page*50
        archive_page_url = 'https://www.hltv.org/events/archive?offset=' + str(offset) + '&eventType=MAJOR&eventType=INTLLAN'
        archive_page_req = requests.get(archive_page_url, headers = header)
        archive_page_soup = BeautifulSoup(archive_page_req.content, 'html5lib').find('div', {'class': 'contentCol'})
        months = BeautifulSoup(str(archive_page_soup),'lxml').find_all('div', {'class': 'events-month'})
        for month in reversed(months):
            month_year = int(re.compile('[0-9]{4}').search(month.contents[1].contents[0]).group(0))
            if month_year < 2015:
                continue
            
            events = BeautifulSoup(str(month),'lxml').find_all('a', {'class': 'a-reset small-event standard-box'})
            for event in events:
                if event.get('href') in exist_events:
                    break
                else:
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
                            
                            if prev_month != month.contents[1].contents[0].encode('utf-8').strip():
                                print('\t' + month.contents[1].contents[0].encode('utf-8').strip())
                                prev_month = month.contents[1].contents[0].encode('utf-8').strip()
                                
                            print('\t\t' + event_href)
                            event_type = event.contents[2].contents[1].contents[1].contents[0].contents[7].text.encode('utf-8')
                            with open("csv\\hltv_events.csv", 'ab') as eventcsv:
                                eventwriter = csv.writer(eventcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                eventwriter.writerow([event_href,event_name,event_end,event_type])
                                
                            
                            break
event()

try:
    scraped_events = set(pd.read_csv('csv\\hltv_events.csv', header = None)[0])
except:
    scraped_events = {}

def team_places():
    print('########## scrape team_places ##########')
    
    try:
        exist_team_places = set(pd.read_csv('csv\\hltv_team_places.csv', header = None)[0].drop_duplicates())
    except:
        exist_team_places = {}
    
    if list(scraped_events - exist_team_places) != []:
        for event_href in list(scraped_events - exist_team_places):
            print('\t' + event_href)
            event_req = requests.get('https://www.hltv.org' + event_href, headers = header)
            event_teams_place = BeautifulSoup(event_req.content,'lxml').find_all('div', {'class': 'placement'})
            for team in event_teams_place:
                team_href = team.contents[1].contents[1].get('href')
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
                    teamplacewriter.writerow([event_href,team_href,place,winnings])
team_places()

def match_info():
    print('########## scrape match_info ##########')
    
    try:
        exist_match_info = set(pd.read_csv('csv\\hltv_match_info.csv', header = None)[0].drop_duplicates())
        exist_match_href = set(pd.read_csv('csv\\hltv_match_info.csv', header = None)[1].drop_duplicates())
    except:
        exist_match_info = {}
        exist_match_href = {}
        
    
        
    prev_event = None
        
    if list(scraped_events - exist_match_info) != []:
        for event_href in list(scraped_events - exist_match_info):
            results_href = 'results?event=' + re.compile('(?<=events\/)[0-9]{1,}(?=\/)').search(event_href).group(0)
            results_req = requests.get('https://www.hltv.org/' + results_href, headers = header)
            result_rows = BeautifulSoup(results_req.content,'lxml').find_all('div', {'class': 'result-con'})
            for match in result_rows:
                if match.contents[0].get('href') not in exist_match_href:
                    match_href = match.contents[0].get('href')
                    match_req = requests.get('https://www.hltv.org' + match_href, headers = header)
                    match_soup = BeautifulSoup(match_req.content,'lxml')
                    
                    match_veto_box = match_soup.find_all('div', {'class': 'standard-box veto-box'})
                    if not re.compile('tie(\-)*breaker', re.I).search(str(match_veto_box[0])):
                        if prev_event != event_href:
                            print('\t' + event_href)
                            prev_event = event_href
                        print('\t\t' + match_href)
                        
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
match_info()

try:
    scraped_matches = set(pd.read_csv('csv\\hltv_match_info.csv', header = None)[1])
except:
    scraped_matches = {}

def vetos():
    print('########## scrape vetos ##########')
    
    try:
        exist_match_vetos = set(pd.read_csv('csv\\hltv_vetos.csv', header = None)[1].drop_duplicates())
    except:
        exist_match_vetos = {}
    
    
    if list(scraped_events - exist_match_info) != []:
    if match_href not in exist_match_vetos:
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
                        
vetos()





























