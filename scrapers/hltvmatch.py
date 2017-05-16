# -*- coding: utf-8 -*-
"""
Created on Tue May 02 19:34:37 2017

@author: wesso
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

hltv_match_exist = os.path.exists("csv\\hltvmatches.csv")

hltv_events = pd.read_csv("csv\\hltvevents.csv", header = None)
want_events = list(hltv_events.loc[(hltv_events[2] == 0) & \
                                   ((hltv_events[3] == 1) | ((hltv_events[4] == 1) & (hltv_events[5] == 1))),0])
event_names = list(hltv_events.loc[(hltv_events[2] == 0) & \
                                   ((hltv_events[3] == 1) | ((hltv_events[4] == 1) & (hltv_events[5] == 1))),1])

if hltv_match_exist:
    exist_matches = pd.read_csv("csv\\hltvmatches.csv", header = None)
    matches_list = list(exist_matches.loc[(pd.isnull(exist_matches[3]) == False) & \
                                          (pd.isnull(exist_matches[10]) == False),2].drop_duplicates())
    complete_events = list(exist_matches.loc[(pd.isnull(exist_matches[3]) == False) | \
                                          (pd.isnull(exist_matches[10]) == False),0].drop_duplicates()) - exist_matches.iloc[-1,0]
    
    with open("csv\\hltvmatches_update.csv", 'wb') as matchupdatecsv:
        matchupdatewriter = csv.writer(matchupdatecsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
        
        new_matches = 0
        i = 1
        for event_id,event_name in zip(want_events,event_names):
            if event_id not in complete_events:
                print(event_name,str(i) + "/" + str(len(event_names)))
                event_results_url = "http://www.hltv.org/?pageid=215&eventid=" + str(event_id)
                event_results_soup = soup_function( event_results_url )
                match_rows = event_results_soup.find_all("div",style = lambda x : x in 
                    ["background-color:white;height:26px;", "background-color:#E6E5E5;height:26px;"])
                for match_row in match_rows:
                    try:
                        match_id = re.sub("/match/","",match_row.contents[1].contents[1].contents[9].contents[1].get("href"))
                    except:
                        continue
                    if match_id not in matches_list:
                        print("0")
                        try:
                            demo_id = re.sub("/\?pageid=[0-9]{1,}\&demoid=","",\
                                             match_row.contents[1].contents[1].contents[7].contents[1].get("href"))
                        except:
                            demo_id = None
                        try:
                            best_of = int(re.compile("[0-9]").search(\
                                          match_row.contents[1].contents[1].contents[5].contents[0].encode("utf-8")).group(0))
                        except:
                            best_of = 1
                        match_url = "http://www.hltv.org/match/" + match_id
                        for iteration in range(0,60):
                            try:
                                match_soup = soup_function( match_url )
                                match_soup.find_all("span", \
                                                {"style":"font-size:14px;"})[0].contents[0].encode("utf-8").strip()
                                break
                            except:
                                time.sleep(0.5)
                        try:
                            match_date_raw = match_soup.find_all("span", \
                                            {"style":"font-size:14px;"})[0].contents[0].encode("utf-8").strip()
                        except:
                            matchupdatewriter.writerow([event_id,event_name,match_id,None,None,None,None,None,\
                                                  None,None,None])
                            break
                        match_date = datetime.strptime(re.sub(r'(?<=[0-9])[a-z]{2}\s{1,}of\s{1,}'\
                                                              ,' ',match_date_raw),"%d %B %Y").strftime("%Y-%m-%d")
                        veto_process_box = match_soup.find_all("div", {"style": "width: 49%;float:left;"})[0]
                        try:
                            veto_process = BeautifulSoup(str(veto_process_box),"lxml").find_all(text = \
                                            re.compile(" remain| left| pick| remove| ban"))
                            for step in veto_process:
                                step_number = re.compile("^[0-9]").search(step.encode("utf-8")).group(0)
                                try:
                                    team = re.compile("(?<=\. ).*(?= (pick|remove))").search(step.encode("utf-8")).group(0)
                                    action = re.compile("pick|remove").search(step.encode("utf-8")).group(0)
                                    map_ = re.compile("nuke|dust2|cache|cobble(stone)*|mirage|overpass|train|inferno",\
                                                      re.I).search(step.encode("utf-8")).group(0)
                                    step_raw = step.encode("utf-8")
                                    matchupdatewriter.writerow([event_id,event_name,match_id,demo_id,match_date,best_of,step_number,\
                                                                team,action,map_,step_raw])
                                except:
                                    team = None
                                    action = None
                                    map_ = re.compile("nuke|dust2|cache|cobble(stone)*|mirage|overpass|train|inferno",\
                                                      re.I).search(step.encode("utf-8")).group(0)
                                    step_raw = step.encode("utf-8")
                                    matchupdatewriter.writerow([event_id,event_name,match_id,demo_id,match_date,best_of,step_number,\
                                                                team,action,map_,step_raw])
                        except:
                            step_number = None
                            team = None
                            action = None
                            map_ = None
                            step_raw = None
                            matchupdatewriter.writerow([event_id,event_name,match_id,demo_id,match_date,best_of,step_number,team,\
                                                        action,map_,step_raw])
                    else:
                        pass
                    new_matches += 1
                i += 1
            else:
                pass
    if new_matches > 0:
        update_matches = pd.read_csv("csv\\hltvmatches_update.csv", header = None)
        
        with open("csv\\hltvmatches.csv", 'wb') as matchescsv:
            exist_matches[~exist_matches[2].isin(list(update_matches[2]))].to_csv(matchescsv, header = False, index = False)
            update_matches.to_csv(matchescsv, header = False, index = False)
    else:
        pass
else:
    with open("csv\\hltvmatches.csv", 'wb') as matchcsv:
        matchwriter = csv.writer(matchcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
        
        i = 1
        for event_id,event_name in zip(want_events,event_names):
            print(event_name,str(i) + "/" + str(len(event_names)))
            event_results_url = "http://www.hltv.org/?pageid=215&eventid=" + str(event_id)
            event_results_soup = soup_function( event_results_url )
            match_rows = event_results_soup.find_all("div",style = lambda x : x in 
                ["background-color:white;height:26px;", "background-color:#E6E5E5;height:26px;"])
            for match_row in match_rows:
                print("0")
                try:
                    match_id = re.sub("/match/","",match_row.contents[1].contents[1].contents[9].contents[1].get("href"))
                    print("1a")
                except:
                    print("1b")
                    continue
                try:
                    demo_id = re.sub("/\?pageid=[0-9]{1,}\&demoid=","",\
                                     match_row.contents[1].contents[1].contents[7].contents[1].get("href"))
                    print("2a")
                except:
                    print("2b")
                    demo_id = None
                try:
                    best_of = int(re.compile("[0-9]").search(\
                                  match_row.contents[1].contents[1].contents[5].contents[0].encode("utf-8")).group(0))
                    print("3a")
                except:
                    print("3b")
                    best_of = 1
                match_url = "http://www.hltv.org/match/" + match_id
                for iteration in range(0,60):
                    try:
                        match_soup = soup_function( match_url )
                        match_soup.find_all("span", \
                                        {"style":"font-size:14px;"})[0].contents[0].encode("utf-8").strip()
                        break
                    except:
                        time.sleep(0.5)
                try:
                    match_date_raw = match_soup.find_all("span", \
                                    {"style":"font-size:14px;"})[0].contents[0].encode("utf-8").strip()
                except:
                    matchwriter.writerow([event_id,event_name,match_id,None,None,None,None,None,\
                                          None,None,None])
                    break
                match_date = datetime.strptime(re.sub(r'(?<=[0-9])[a-z]{2}\s{1,}of\s{1,}'\
                                                      ,' ',match_date_raw),"%d %B %Y").strftime("%Y-%m-%d")
                veto_process_box = match_soup.find_all("div", {"style": "width: 49%;float:left;"})[0]
                try:
                    veto_process = BeautifulSoup(str(veto_process_box),"lxml").find_all(text = \
                                    re.compile(" remain| left| pick| remove| ban"))
                    for step in veto_process:
                        step_number = int(re.compile("^[0-9]").search(step.encode("utf-8")).group(0))
                        try:
                            team = re.compile("(?<=\. ).*(?= (pick|remove))").search(step.encode("utf-8")).group(0)
                            action = re.compile("pick|remove").search(step.encode("utf-8")).group(0)
                            map_ = re.compile("nuke|dust2|cache|cobble(stone)*|mirage|overpass|train|inferno",\
                                                  re.I).search(step.encode("utf-8")).group(0)
                            step_raw = step.encode("utf-8")
                            matchwriter.writerow([event_id,event_name,match_id,demo_id,match_date,best_of,step_number,\
                                                        team,action,map_,step_raw])
                            print("4a")
                        except:
                            team = None
                            action = None
                            map_ = re.compile("nuke|dust2|cache|cobble(stone)*|mirage|overpass|train|inferno",\
                                                  re.I).search(step.encode("utf-8")).group(0)
                            step_raw = step.encode("utf-8")
                            matchwriter.writerow([event_id,event_name,match_id,demo_id,match_date,best_of,step_number,\
                                                        team,action,map_,step_raw])
                            print("4b")
                    print("5a")
                except:
                    print
                    step_number = None
                    team = None
                    action = None
                    map_ = None
                    step_raw = None
                    matchwriter.writerow([event_id,event_name,match_id,demo_id,match_date,best_of,step_number,team,\
                                                action,map_,step_raw])
                    print("5b")
            i += 1