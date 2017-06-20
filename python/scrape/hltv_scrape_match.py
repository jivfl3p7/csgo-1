# -*- coding: utf-8 -*-
"""
Created on Tue May 02 19:34:37 2017

@author: wesso
"""

from __future__ import division
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import math
import datetime
import csv

def match():
    try:
        exist_matches = list(pd.read_csv('csv\\hltv_matches.csv', header = None)[1])
    except:
        exist_matches = pd.DataFrame(index = range(0), columns = [0,1])
        
    hltv_events = list(pd.read_csv('csv\\hltv_events.csv', header = None)[0])
    
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    
    for event_href in reversed(hltv_events):
        eventid = re.compile('(?<=events\/)[0-9]{1,}(?=\/)').search(event_href).group(0)
        
        event_results_url = 'https://www.hltv.org/results?event=' + eventid
        event_results_req = requests.get(event_results_url, headers = header)
        event_results_soup = BeautifulSoup(event_results_req.content,'lxml').find_all('div', {'class': 'results-all'})
        match_hrefs = BeautifulSoup(str(event_results_soup),'lxml').find_all('a', {'class': 'a-reset'})
        for match_href in match_hrefs:
            if match_href.get('href') not in exist_matches:
                match_url = 'https://www.hltv.org' + match_href.get('href')
                match_req = requests.get(match_url, headers = header)
                match_soup = BeautifulSoup(match_req.content,'lxml')
                try:
                    match_team1_name = match_soup.find_all('div', {'class': 'teamName'})[0].text.encode('utf-8')
                except:
                    continue
                match_team1_href = match_soup.find_all('a', {'class': 'teamName'})[0].get('href')
                match_team2_name = match_soup.find_all('div', {'class': 'teamName'})[1].text.encode('utf-8')
                match_team2_href = match_soup.find_all('a', {'class': 'teamName'})[1].get('href')
                match_unix_time = int(match_soup.find_all('div', {'class': 'timeAndEvent'})[0].contents[1].get('data-unix'))/1000
                match_datetime_utc = datetime.datetime.utcfromtimestamp(match_unix_time).isoformat()
                try:
                    match_demo_pt1 = BeautifulSoup(str(match_soup.find_all('div', {'class': 'match-page'})), 'lxml')
                    match_demo = match_demo_pt1.find_all('a', {'href': re.compile('demo')})[0].get('href')
                except:
                    match_demo = None
                with open("csv\\hltv_matches.csv", 'ab') as matchcsv:
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
                            team = re.sub('^[0-9]\. ','',re.compile('.*(?= remove|pick)').search(veto_step.encode('utf-8')).group(0))
                            action = re.compile('remove|pick').search(veto_step.encode('utf-8')).group(0)
                        except:
                            team = None
                            action = None
                        map_ = re.compile('nuke|cobble|mirage|inferno|cache|dust( )*2|overpass|train', re.I).search(veto_step.encode('utf-8')).group(0)
                        with open("csv\\hltv_vetos.csv", 'ab') as vetocsv:
                            vetowriter = csv.writer(vetocsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                            vetowriter.writerow([match_href.get('href'), step, team, action, map_])
                        i += 1