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
    ...
match_info()