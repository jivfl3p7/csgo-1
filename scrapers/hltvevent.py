# -*- coding: utf-8 -*-
"""
Created on Sat Apr 29 15:56:36 2017

@author: wessonmo
"""

from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
import csv
import os
from fake_useragent import UserAgent
import urllib
import urllib2
import time


def soup_function( url ):
    values = {'name': '','location': '','language': '' }
    result = False
    n = 1
    while result == False and n < 60:
        try:
            headers = {'User-Agent': UserAgent().random}
            data = urllib.urlencode(values)
            req = urllib2.Request(url,data,headers)
            global response
            response = urllib2.urlopen(req)
            soup = BeautifulSoup(response,"lxml")
            result = True
        except:
            time.sleep(1)
            headers = {'User-Agent': UserAgent().random}
            data = urllib.urlencode(values)
            req = urllib2.Request(url,data,headers)
            global response
            response = urllib2.urlopen(req)
            soup = BeautifulSoup(response,"lxml")
            n += 1
    return soup;

hltv_event_exist = os.path.exists("csv\\hltvevents.csv")

ranks = pd.read_csv("csv\\hltvranks.csv", header = None)
rank_dates = list(ranks[0].drop_duplicates().sort_values(ascending = False))

females = pd.read_csv("csv\\hltvfemaleteams.csv", header = None)
female_teams = list(females[0].drop_duplicates())

archive_url = "http://www.hltv.org/?pageid=184"
archive_soup = soup_function( archive_url ).find_all("div", {"class": "covMainBoxContent"})
events = BeautifulSoup(str(archive_soup),"lxml").find_all("div", style = lambda x : x in \
    ["width:606px;height:22px;background-color:white", "width:606px;height:22px;background-color:#E6E5E5"])

if hltv_event_exist:
    exist_events = pd.read_csv("csv\\hltvevents.csv", header = None)
    
    with open("csv\\hltvevents_update.csv", 'wb') as updatecsv:
        updatewriter = csv.writer(updatecsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
        
        new_events = 0
        for event in events[:(len(events) - 1861)]:
            
            event_id = int(re.compile("(?<=eventid=)[0-9]{1,}").search(\
                event.contents[1].contents[1].contents[2].get("href")).group(0))
            print(event_id)

            if event_id in list(exist_events.loc[exist_events[2] == 0,0]):
                pass
            elif event_id in list(exist_events.loc[exist_events[2] == 1,0]):
                ongoing_url = "http://www.hltv.org/matches/event/" + str(event_id) + "/"
                ongoing_event = 1 if len(soup_function( ongoing_url ).find_all("div", \
                                         {"class": "matchListDateBox"})) > 0 else 0
                
                if ongoing_event == 1:
                    continue
                else:
                    event_name = exist_events.loc[exist_events[0] == event_id,1].item()
                    
                    female_event = exist_events.loc[exist_events[0] == event_id,3].item()
                    
                    hltv_rank_event = exist_events.loc[exist_events[0] == event_id,4].item()
                    
                    LAN_event = 1 if int(event.contents[1].contents[4].contents[0].encode("utf-8")) > 0 else 0
                    
                    updatewriter.writerow([event_id,event_name,ongoing_event,female_event,hltv_rank_event,LAN_event])
                    
                    new_events += 1
            else:
                event_name = event.contents[1].contents[1].contents[2].text.encode("utf-8")
                print(event_name)
                ongoing_url = "http://www.hltv.org/matches/event/" + str(event_id) + "/"
                ongoing_event = 1 if len(soup_function( ongoing_url ).find_all("div", \
                                         {"class": "matchListDateBox"})) > 0 else 0
                
                event_results_url = "http://www.hltv.org/?pageid=215&eventid=" + str(event_id)
                result_rows = soup_function( event_results_url ).find_all("div",style = lambda x : x in 
                    ["background-color:white;height:26px;", "background-color:#E6E5E5;height:26px;"])
                for result in reversed(result_rows):
                    try:
                        match_id = result.contents[1].contents[1].contents[9].contents[1].get("href")
                        match_url = "http://www.hltv.org" + match_id
                        match_date_raw = soup_function( match_url ).find_all("span", \
                            {"style":"font-size:14px;"})[0].contents[0].encode("utf-8").strip()
                        pyth_match_date = datetime.strptime(\
                            re.sub(r'(?<=[0-9])[a-z]{2}\s{1,}of\s{1,}',' ',match_date_raw),"%d %B %Y")
                        break
                    except:
                        pass
                for rank_date in rank_dates:
                    if pyth_match_date > datetime.strptime(rank_date,"%Y-%m-%d"):
                        hltv_rank_list = ranks.loc[ranks[0] == rank_date,2].tolist()
                        break
                    else:
                        pass
                female_count = 0
                female_event = 0
                for result in result_rows:
                    team1 = result.contents[1].contents[1].contents[1].contents[1].contents[3].text.encode("utf-8")
                    team2 = result.contents[1].contents[1].contents[1].contents[1].contents[7].text.encode("utf-8")
                    if team1 in female_teams or team2 in female_teams:
                        female_count += 1
                        if female_count == 3:
                            female_event = 1
                            break
                        else:
                            pass
                    else:
                        pass
                hltv_rank_event = 0
                for result in result_rows:
                    team1 = result.contents[1].contents[1].contents[1].contents[1].contents[3].text.encode("utf-8")
                    team2 = result.contents[1].contents[1].contents[1].contents[1].contents[7].text.encode("utf-8")
                    if team1 in hltv_rank_list or team2 in hltv_rank_list:
                        hltv_rank_event = 1
                        break
                    else:
                        pass
                
                LAN_event = 1 if int(event.contents[1].contents[4].contents[0].encode("utf-8")) > 0 else 0
                
                updatewriter.writerow([event_id,event_name,ongoing_event,female_event,hltv_rank_event,LAN_event])
                
                new_events += 1
    
    if new_events > 0:
        update_events = pd.read_csv("csv\\hltvevents_update.csv", header = None)
            
        with open("csv\\hltvevents.csv", 'wb') as eventscsv:
            exist_events[~exist_events[0].isin(list(update_events[0]))].to_csv(eventscsv, header = False, index = False)
            update_events.to_csv(eventscsv, header = False, index = False)
    else:
        pass
else:
    with open("csv\\hltvevents.csv", 'wb') as eventscsv:
        eventwriter = csv.writer(eventscsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
        j = 1
        for event in events[:(len(events) - 1861)]:
            print("1",event.contents[1].contents[1].contents[2].text.encode("utf-8"),str(j) + "/" + str((len(events) - 1861)))
            event_id = int(re.compile("(?<=eventid=)[0-9]{1,}").search(\
                event.contents[1].contents[1].contents[2].get("href")).group(0))
            event_name = event.contents[1].contents[1].contents[2].text.encode("utf-8")
            
            ongoing_url = "http://www.hltv.org/matches/event/" + str(event_id) + "/"
            ongoing_event = 1 if len(soup_function( ongoing_url ).find_all("div", \
                                     {"class": "matchListDateBox"})) > 0 else 0
            
            event_results_url = "http://www.hltv.org/?pageid=215&eventid=" + str(event_id)
            result_rows = soup_function( event_results_url ).find_all("div",style = lambda x : x in 
                ["background-color:white;height:26px;", "background-color:#E6E5E5;height:26px;"])
            for result in reversed(result_rows):
                try:
                    match_id = result.contents[1].contents[1].contents[9].contents[1].get("href")
                    match_url = "http://www.hltv.org" + match_id
                    match_date_raw = soup_function( match_url ).find_all("span", \
                        {"style":"font-size:14px;"})[0].contents[0].encode("utf-8").strip()
                    pyth_match_date = datetime.strptime(\
                        re.sub(r'(?<=[0-9])[a-z]{2}\s{1,}of\s{1,}',' ',match_date_raw),"%d %B %Y")
                    break
                except:
                    pass
            print("2")
            for rank_date in rank_dates:
                if pyth_match_date > datetime.strptime(rank_date,"%Y-%m-%d"):
                    hltv_rank_list = ranks.loc[ranks[0] == rank_date,2].tolist()
                    break
                else:
                    pass
            female_count = 0
            female_event = 0
            for result in result_rows:
                team1 = result.contents[1].contents[1].contents[1].contents[1].contents[3].text.encode("utf-8")
                team2 = result.contents[1].contents[1].contents[1].contents[1].contents[7].text.encode("utf-8")
                if team1 in female_teams or team2 in female_teams:
                    female_count += 1
                    if female_count == 3:
                        female_event = 1
                        break
                    else:
                        pass
                else:
                    pass
            hltv_rank_event = 0
            for result in result_rows:
                team1 = result.contents[1].contents[1].contents[1].contents[1].contents[3].text.encode("utf-8")
                team2 = result.contents[1].contents[1].contents[1].contents[1].contents[7].text.encode("utf-8")
                if team1 in hltv_rank_list or team2 in hltv_rank_list:
                    hltv_rank_event = 1
                    break
                else:
                    pass
            print("3")
             
            LAN_event = 1 if int(event.contents[1].contents[4].contents[0].encode("utf-8")) > 0 else 0
            
            eventwriter.writerow([event_id,event_name,ongoing_event,female_event,hltv_rank_event,LAN_event])
            print("5")
            j = j + 1