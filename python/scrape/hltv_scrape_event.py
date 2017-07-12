from __future__ import division
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import math
from dateutil.parser import parse
import datetime
import csv

def event():
    print('########## scrape events ##########')
    try:
        exist_events = list(pd.read_csv('csv\\hltv_events.csv', header = None)[1])
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
    
    for page in range(0,num_pages):
        offset = page*50
        archive_page_url = 'https://www.hltv.org/events/archive?offset=' + str(offset) + '&eventType=MAJOR&eventType=INTLLAN'
        archive_page_req = requests.get(archive_page_url, headers = header)
        archive_page_soup = BeautifulSoup(archive_page_req.content, 'html5lib').find('div', {'class': 'contentCol'})
        months = BeautifulSoup(str(archive_page_soup),'lxml').find_all('div', {'class': 'events-month'})
        for month in months:
            month_year = int(re.compile('[0-9]{4}').search(month.contents[1].contents[0].encode('utf-8')).group(0))
            if month_year >= 2016:
                events = BeautifulSoup(str(month),'lxml').find_all('a', {'class': 'a-reset small-event standard-box'})
                for event in events:
                    event_name = event.contents[2].contents[1].contents[1].contents[0].contents[1].text.encode('utf-8').strip()
                    if event_name in exist_events:
                        return
                    else:
                        print(month.contents[1].contents[0].encode('utf-8').strip() + ', ' + str(len(events)))
                        event_url = event.get('href')
                        
                        event_req = requests.get('https://www.hltv.org/' + event_url, headers = header)
                        event_date_box = BeautifulSoup(event_req.content,'lxml').find_all('div', {'class': 'event-header-component standard-box padding no-top-border'})
                        event_date = BeautifulSoup(str(event_date_box),'lxml').find_all('td', {'class': 'eventdate'})
                        
                        event_start = datetime.datetime.utcfromtimestamp(int(event_date[1].contents[0].get('data-unix'))/1000).strftime('%m/%d/%Y')
                        try:
                            event_end = datetime.datetime.utcfromtimestamp(int(event_date[1].contents[1].contents[1].get('data-unix'))/1000).strftime('%m/%d/%Y')
                        except:
                            event_end = None
                        hltv_rank_teams = []
                        for rank_dt in reversed(list(pd.to_datetime(ranks[0].drop_duplicates()).sort_values(0))):
                            if rank_dt < pd.to_datetime(event_start):
                                hltv_rank_teams = hltv_rank_teams + list(ranks.loc[ranks[0] == re.sub('^0(?=[0-9])|(?<=\/)0(?=[0-9])','',rank_dt.strftime('%m/%d/%Y')),3])
                                break
                        if not event_end == None:
                            for rank_dt in reversed(list(pd.to_datetime(ranks[0].drop_duplicates()).sort_values(0))):
                                if rank_dt < pd.to_datetime(event_end):
                                    hltv_rank_teams = hltv_rank_teams + list(ranks.loc[ranks[0] == re.sub('^0(?=[0-9])|(?<=\/)0(?=[0-9])','',rank_dt.strftime('%m/%d/%Y')),3])
                                    break
                        event_teams_grid = BeautifulSoup(event_req.content,'lxml').find_all('div', {'class': 'teams-attending grid'})
                        event_teams = BeautifulSoup(str(event_teams_grid),'lxml').find_all('div', {'class': 'team-name'})
                        event_use = False
                        for team in event_teams:
                            if team.contents[0].get('href') in hltv_rank_teams:
                                event_use = True
                                break
                            
                        if event_use == True:
                            event_date_raw = event.contents[2].contents[1].contents[1].contents[2].contents[1].contents[1].contents[0].text.encode('utf-8')
                            event_end_date_raw = re.sub('.* - ','',event_date_raw)
                            event_end_date = datetime.datetime.strftime(parse(event_end_date_raw), '%Y-%m-%d')
                            try:
                                prize_money = int(re.sub('\$|,','',event.contents[2].contents[1].contents[1].contents[0].contents[5].text.encode('utf-8')))
                            except:
                                prize_money = None
                            event_type = event.contents[2].contents[1].contents[1].contents[0].contents[7].text.encode('utf-8')
                            with open("csv\\hltv_events.csv", 'ab') as eventcsv:
                                eventwriter = csv.writer(eventcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                eventwriter.writerow([event_url,event_name,event_end_date,prize_money,event_type])

event()