# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 21:07:47 2017

@author: wessonmo
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 09:51:09 2017

@author: wessonmo
"""

import requests
from bs4 import BeautifulSoup
import re
import urllib
import urllib2
import time
import pandas as pd
import os
from datetime import datetime
import csv
from fake_useragent import UserAgent
import sys

### Preliminary Definitions

ranks = pd.read_csv('C:\\Users\\wessonmo\\Documents\\GitHub\\csgo\\csv\\hltvranks.csv',header=None) #HLTV Rankings
females = pd.read_csv('C:\\Users\\wessonmo\\Documents\\GitHub\\csgo\\csv\\hltvfemaleteams.csv',header=None) #List of female teams

#Check if these files have already been created
event_exist = os.path.exists('C:\\Users\\wessonmo\\Documents\\GitHub\\csgo\\csv\\event_list.csv')
rost_exist = os.path.exists('C:\\Users\\wessonmo\\Documents\\GitHub\\csgo\\csv\\hltvrosters.csv')

#Scan demos that have already been downloaded
directory = "D:\\CSGO Demos"
file_list,folder_list = [],[]
for folder in os.listdir(directory):
    for filename in os.listdir(str(directory + '\\' + folder)):
        folder_list.append(folder[:4])
        file_list.append(filename[:-4])

#Create list of events from HLTV event archive page
archive_url = "http://www.hltv.org/?pageid=184"
soup = BeautifulSoup(requests.get(archive_url).content,"lxml").find_all("div", {"class": "covMainBoxContent"})
events = BeautifulSoup(str(soup),"lxml").find_all("div", style = lambda x : x in \
    ["width:606px;height:22px;background-color:white", "width:606px;height:22px;background-color:#E6E5E5"])


##eventpiccheck scans the events that have occured since first HLTV ranking.
##The event will be scraped if it meets the following criteria:
##   - pics > 0 (approximation for LAN events)
##   - ongoing_matches < 1 (event is complete and not ongoing)
##   - event_id not in comp_events[0] (comp_events is the list of already-scraped events)
##In addition, the event must also contain a team from the most recent HLTV ranking prior to said event.
##eventpiccheck scans the dates each HLTV ranking was released and assigns the correct date to list_date
#def eventpiccheck( events, comp_events, ranks, sex ):
#    for event in events[:(len(events) - 1731)]:
#        pics = int(event.contents[1].contents[4].contents[0].encode("utf-8"))
#        
#        event_id = re.compile("(?<=eventid=)[0-9]{1,}").search(event.contents[1].contents[1].contents[2].get("href")).group(0)
#        event_name = re.sub("\:"," ",event.contents[1].contents[1].contents[2].text.encode("utf-8"))
#        
#        info_url = "http://www.hltv.org/?pageid=357&eventid=" + event_id
#        try:
#            len(re.compile("Online").search(str(BeautifulSoup(requests.get(info_url).content,"lxml").find_all("div",{"class":"hubFramedBox"})[0])).group(0))
#            online = 1
#        except:
#            online = 0
#        
#        print(pics,event.contents[1].contents[1].contents[2].contents[0].encode("utf-8"))
#        
#        ongoing_url = "http://www.hltv.org/matches/event/" + event_id + "/"
#        ongoing_matches = len(BeautifulSoup(requests.get(ongoing_url).content,"lxml").find_all("div", {"class": "matchListDateBox"}))
#        
#        if ongoing_matches < 1 and int(event_id) not in list(comp_events[0]):
#            results_url = "http://www.hltv.org/?pageid=215&eventid=" + event_id
#            results_soup = BeautifulSoup(requests.get(results_url).content,"lxml")
#            
#            last_match_id = results_soup.find_all("div", \
#                {"class": "covResultBoxContent"})[0].contents[3].contents[1].contents[1].contents[9].contents[1].get("href")
#            last_match_url = "http://www.hltv.org" + last_match_id
#            last_match_date = re.sub(r'(?<=[0-9])[a-z]{2}\s{1,}of\s{1,}',' ',\
#                BeautifulSoup(requests.get(last_match_url).content,"lxml").find_all("span", \
#                    {"style":"font-size:14px;"})[0].contents[0].encode("utf-8").strip())
#            
#            try:
#                del list_date
#            except:
#                pass
#            
#            for rank_date in set(ranks[0]):
#                if datetime.strptime(last_match_date,"%d %B %Y") > datetime.strptime(rank_date,"%Y-%m-%d"):
#                    pass
#                else:
#                    list_date = rank_date
#                    break
#            
#            try:
#                list_date
#            except:
#                list_date = ranks[0].max()
#                
#            if len(BeautifulSoup(requests.get(info_url).content,"lxml").find_all("div", {"class": "hubTeam"})) > 0:
#                teams = BeautifulSoup(requests.get(info_url).content,"lxml").find_all("div", {"class": "hubTeam"})
#            else:
#                teams = BeautifulSoup(str(BeautifulSoup(requests.get(info_url).content,"lxml").find_all("div", \
#                    {"class": "centerNoHeadline"})),"lxml").find_all("div",{"style":"margin-left:-5px;"})
#            
#            eventteamcheck( teams, event_id, folder_list, list_date, results_soup, ranks, page_type )
#        else:
#            pass
#        eventwriter.writerow([int(event_id),online,sex])
#    return;
#
##eventteamcheck scans the teams in an event for a team in the most recent HLTV ranking.
##If the event does not contain a team from the HLTV ranking, the event is skipped.
##In addition, it creates the demos variable to indicate whether or not to download the
##demos from that event.
#def eventteamcheck( teams, event_id, folder_list, list_date, results_soup, ranks, page_type ):
#    for team in teams:
#        try:
#            team.contents[0].contents[0].encode("utf-8")
#            temp_team_name = team.contents[0].contents[0].encode("utf-8")
#        except:
#            temp_team_name = team.contents[1].contents[3].contents[0].encode("utf-8")
#        
#        if temp_team_name in ranks.loc[ranks[0] == list_date,2].tolist():
#            sex = "male"
#            matches = results_soup.find_all("div",style = lambda x : x in \
#                ["background-color:white;height:26px;", "background-color:#E6E5E5;height:26px;"])
#            matchiterator( matches, match_soup, match_url )
#            break
#        elif temp_team_name in list(females[0]):
#            sex = "female"
#            matches = results_soup.find_all("div",style = lambda x : x in \
#                ["background-color:white;height:26px;", "background-color:#E6E5E5;height:26px;"])
#            matchiterator( matches, match_soup, match_url )
#            break
#        else:
#            break
#    return;
#
##matchiterator just defines some variables for playeriterator and demoiterator
#def matchiterator( matches, match_soup, match_url ):
#    for match in matches:
#        match_url = "http://www.hltv.org" + match.contents[1].contents[1].contents[9].contents[1].get("href")
#        match_soup = BeautifulSoup(requests.get(match_url).content,"lxml")
#        match_id = re.compile("(?<=/match/).*").search(\
#            match.contents[1].contents[1].contents[9].contents[1].get("href")).group(0)
#        
#        try:
#            demo_id = int(re.compile("(?<=demoid=)[0-9]{1,}").search(\
#                match.contents[1].contents[1].contents[7].contents[1].get("href")).group(0))
#        except:
#            demo_id = None
#        
#        teams2 = BeautifulSoup(str(match_soup.find_all("div",{"class":"centerNoHeadline"})),"lxml").find_all("a", \
#            {"href": re.compile("teamid=")})[:2]
#        
#        players = BeautifulSoup(str(match_soup.find_all("div",{"class":"hotmatchbox"})),"lxml").find_all("a", \
#            {"href": re.compile("(/player/)|(playerid)")})
#        playeriterator( players, match, teams2, event_id, match_id, demo_id, team_name, team_id, player_name, player_id )
#        
#        if demo_id != None and match_id not in file_list:
#            demoiterator( demo_id, event_id, event_name, match_id )
#        else:
#            pass
#    return;
#
##scrapes match, team, and player details
#def playeriterator( players, match, teams2, event_id, match_id, demo_id, team_name, team_id, player_name, player_id ):
#    n = 1
#    for player in players:
#        player_name = player.text.encode("utf-8")
#        player_id = player.get("href")
#        if n <= 5:
#            team_name = teams2[0].text.encode("utf-8")
#            team_id = re.compile("(?<=teamid\=)[0-9]{1,}").search(teams2[0].get("href")).group(0)
#        else:
#            team_name = teams2[1].text.encode("utf-8")
#            team_id = re.compile("(?<=teamid\=)[0-9]{1,}").search(teams2[1].get("href")).group(0)
#        n = n + 1
#        rosterwriter.writerow([event_id,match_id,demo_id,team_name,team_id,player_name,player_id])
#    return;
#    
##downloads demo
#def demoiterator( demo_id, event_id, event_name, match_id ):
#    try:
#        url = 'http://www.hltv.org/interfaces/download.php?demoid=' + str(demo_id)
#        values = {'name': '',
#                  'location': '',
#                  'language': '' }
#        try:
#            headers = {'User-Agent': UserAgent().random}
#        except:
#            headers = {'User-Agent': UserAgent().random}
#        
#        data = urllib.urlencode(values)
#        req = urllib2.Request(url,data,headers)
#        response = urllib2.urlopen(req)
#        read = response.read() 
#        if not os.path.exists("D:\\CSGO Demos\\" + event_id + " - " + event_name + "\\"):
#            os.makedirs("D:\\CSGO Demos\\" + event_id + " - " + event_name + "\\")
#        print("open file - " + time.strftime("%c"))
#        with open("D:\\CSGO Demos\\" + event_id + " - " + event_name + "\\" + match_id + ".rar", 'wb+') as file_:
#            file_.write(read)
#        file_.close()
#        print("close file - " + time.strftime("%c"))
#    except:
#        pass
#    return;


   

#executes the above functions
try:
    if event_exist and rost_exist:
        comp_events = pd.read_csv('C:\\Users\\wessonmo\\Documents\\GitHub\\csgo\\csv\\event_list.csv',header=None)
        
        with open('C:\\Users\\wessonmo\\Documents\\GitHub\\csgo\\csv\\hltvrosters.csv', 'a') as rosterscsv:
            rosterwriter = csv.writer(rosterscsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
            
            with open('C:\\Users\\wessonmo\\Documents\\GitHub\\csgo\\csv\\event_list.csv', 'a') as eventscsv:
                eventwriter = csv.writer(eventscsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                
                for event in events[:(len(events) - 1731)]:
                    sex = None
                    pics = int(event.contents[1].contents[4].contents[0].encode("utf-8"))
                    
                    event_id = re.compile("(?<=eventid=)[0-9]{1,}").search(event.contents[1].contents[1].contents[2].get("href")).group(0)
                    event_name = re.sub("\:"," ",event.contents[1].contents[1].contents[2].text.encode("utf-8"))
                    
                    info_url = "http://www.hltv.org/?pageid=357&eventid=" + event_id
                    try:
                        len(re.compile("Online").search(str(BeautifulSoup(requests.get(info_url).content,"lxml").find_all("div",{"class":"hubFramedBox"})[0])).group(0))
                        online = 1
                    except:
                        online = 0
                    
                    print(pics,event.contents[1].contents[1].contents[2].contents[0].encode("utf-8"))
                    
                    ongoing_url = "http://www.hltv.org/matches/event/" + event_id + "/"
                    ongoing_matches = len(BeautifulSoup(requests.get(ongoing_url).content,"lxml").find_all("div", {"class": "matchListDateBox"}))
                    
                    if ongoing_matches < 1 and int(event_id) not in list(comp_events[0]) and online == 0:
                        results_url = "http://www.hltv.org/?pageid=215&eventid=" + event_id
                        results_soup = BeautifulSoup(requests.get(results_url).content,"lxml")
                        
                        last_match_id = results_soup.find_all("div", \
                            {"class": "covResultBoxContent"})[0].contents[3].contents[1].contents[1].contents[9].contents[1].get("href")
                        last_match_url = "http://www.hltv.org" + last_match_id
                        last_match_date = re.sub(r'(?<=[0-9])[a-z]{2}\s{1,}of\s{1,}',' ',\
                            BeautifulSoup(requests.get(last_match_url).content,"lxml").find_all("span", \
                                {"style":"font-size:14px;"})[0].contents[0].encode("utf-8").strip())
                        
                        try:
                            del list_date
                        except:
                            pass
                        
                        for rank_date in set(ranks[0]):
                            if datetime.strptime(last_match_date,"%d %B %Y") > datetime.strptime(rank_date,"%Y-%m-%d"):
                                pass
                            else:
                                list_date = rank_date
                                break
                        
                        try:
                            list_date
                        except:
                            list_date = ranks[0].max()
                            
                        if len(BeautifulSoup(requests.get(info_url).content,"lxml").find_all("div", {"class": "hubTeam"})) > 0:
                            teams = BeautifulSoup(requests.get(info_url).content,"lxml").find_all("div", {"class": "hubTeam"})
                        else:
                            teams = BeautifulSoup(str(BeautifulSoup(requests.get(info_url).content,"lxml").find_all("div", \
                                {"class": "centerNoHeadline"})),"lxml").find_all("div",{"style":"margin-left:-5px;"})
                        
                        for team in teams:
                            try:
                                team.contents[0].contents[0].encode("utf-8")
                                temp_team_name = team.contents[0].contents[0].encode("utf-8")
                            except:
                                temp_team_name = team.contents[1].contents[3].contents[0].encode("utf-8")
                            
                            if temp_team_name in ranks.loc[ranks[0] == list_date,2].tolist():
                                sex = "male"
                                matches = results_soup.find_all("div",style = lambda x : x in \
                                    ["background-color:white;height:26px;", "background-color:#E6E5E5;height:26px;"])
                                for match in matches:
                                    match_url = "http://www.hltv.org" + match.contents[1].contents[1].contents[9].contents[1].get("href")
                                    match_soup = BeautifulSoup(requests.get(match_url).content,"lxml")
                                    match_id = re.compile("(?<=/match/).*").search(\
                                        match.contents[1].contents[1].contents[9].contents[1].get("href")).group(0)
                                    
                                    try:
                                        demo_id = int(re.compile("(?<=demoid=)[0-9]{1,}").search(\
                                            match.contents[1].contents[1].contents[7].contents[1].get("href")).group(0))
                                    except:
                                        demo_id = None
                                    
                                    teams2 = BeautifulSoup(str(match_soup.find_all("div",{"class":"centerNoHeadline"})),"lxml").find_all("a", \
                                        {"href": re.compile("teamid=")})[:2]
                                    
                                    players = BeautifulSoup(str(match_soup.find_all("div",{"class":"hotmatchbox"})),"lxml").find_all("a", \
                                        {"href": re.compile("(/player/)|(playerid)")})
                                    n = 1
                                    for player in players:
                                        player_name = player.text.encode("utf-8")
                                        player_id = player.get("href")
                                        if n <= 5:
                                            team_name = teams2[0].text.encode("utf-8")
                                            team_id = re.compile("(?<=teamid\=)[0-9]{1,}").search(teams2[0].get("href")).group(0)
                                        else:
                                            team_name = teams2[1].text.encode("utf-8")
                                            team_id = re.compile("(?<=teamid\=)[0-9]{1,}").search(teams2[1].get("href")).group(0)
                                        n = n + 1
                                        rosterwriter.writerow([event_id,match_id,demo_id,team_name,team_id,player_name,player_id])
                                    
                                    if demo_id != None and match_id not in file_list:
                                        try:
                                            url = 'http://www.hltv.org/interfaces/download.php?demoid=' + str(demo_id)
                                            values = {'name': '',
                                                      'location': '',
                                                      'language': '' }
                                            try:
                                                headers = {'User-Agent': UserAgent().random}
                                            except:
                                                headers = {'User-Agent': UserAgent().random}
                                            
                                            data = urllib.urlencode(values)
                                            req = urllib2.Request(url,data,headers)
                                            response = urllib2.urlopen(req)
                                            read = response.read() 
                                            if not os.path.exists("D:\\CSGO Demos\\" + event_id + " - " + event_name + "\\"):
                                                os.makedirs("D:\\CSGO Demos\\" + event_id + " - " + event_name + "\\")
                                            print("open file - " + time.strftime("%c"))
                                            with open("D:\\CSGO Demos\\" + event_id + " - " + event_name + "\\" + match_id + ".rar", 'wb+') as file_:
                                                file_.write(read)
                                            file_.close()
                                            print("close file - " + time.strftime("%c"))
                                        except:
                                            pass
                                    else:
                                        pass
                                break
                            elif temp_team_name in list(females[0]):
                                sex = "female"
                                matches = results_soup.find_all("div",style = lambda x : x in \
                                    ["background-color:white;height:26px;", "background-color:#E6E5E5;height:26px;"])
                                for match in matches:
                                    match_url = "http://www.hltv.org" + match.contents[1].contents[1].contents[9].contents[1].get("href")
                                    match_soup = BeautifulSoup(requests.get(match_url).content,"lxml")
                                    match_id = re.compile("(?<=/match/).*").search(\
                                        match.contents[1].contents[1].contents[9].contents[1].get("href")).group(0)
                                    
                                    try:
                                        demo_id = int(re.compile("(?<=demoid=)[0-9]{1,}").search(\
                                            match.contents[1].contents[1].contents[7].contents[1].get("href")).group(0))
                                    except:
                                        demo_id = None
                                    
                                    teams2 = BeautifulSoup(str(match_soup.find_all("div",{"class":"centerNoHeadline"})),"lxml").find_all("a", \
                                        {"href": re.compile("teamid=")})[:2]
                                    
                                    players = BeautifulSoup(str(match_soup.find_all("div",{"class":"hotmatchbox"})),"lxml").find_all("a", \
                                        {"href": re.compile("(/player/)|(playerid)")})
                                    n = 1
                                    for player in players:
                                        player_name = player.text.encode("utf-8")
                                        player_id = player.get("href")
                                        if n <= 5:
                                            team_name = teams2[0].text.encode("utf-8")
                                            team_id = re.compile("(?<=teamid\=)[0-9]{1,}").search(teams2[0].get("href")).group(0)
                                        else:
                                            team_name = teams2[1].text.encode("utf-8")
                                            team_id = re.compile("(?<=teamid\=)[0-9]{1,}").search(teams2[1].get("href")).group(0)
                                        n = n + 1
                                        rosterwriter.writerow([event_id,match_id,demo_id,team_name,team_id,player_name,player_id])
                                    
                                    if demo_id != None and match_id not in file_list:
                                        try:
                                            url = 'http://www.hltv.org/interfaces/download.php?demoid=' + str(demo_id)
                                            values = {'name': '',
                                                      'location': '',
                                                      'language': '' }
                                            try:
                                                headers = {'User-Agent': UserAgent().random}
                                            except:
                                                headers = {'User-Agent': UserAgent().random}
                                            
                                            data = urllib.urlencode(values)
                                            req = urllib2.Request(url,data,headers)
                                            response = urllib2.urlopen(req)
                                            read = response.read() 
                                            if not os.path.exists("D:\\CSGO Demos\\" + event_id + " - " + event_name + "\\"):
                                                os.makedirs("D:\\CSGO Demos\\" + event_id + " - " + event_name + "\\")
                                            print("open file - " + time.strftime("%c"))
                                            with open("D:\\CSGO Demos\\" + event_id + " - " + event_name + "\\" + match_id + ".rar", 'wb+') as file_:
                                                file_.write(read)
                                            file_.close()
                                            print("close file - " + time.strftime("%c"))
                                        except:
                                            pass
                                    else:
                                        pass
                                break
                            else:
                                break
                    else:
                        pass
                    eventwriter.writerow([int(event_id),online,sex])
    else:
        with open('C:\\Users\\wessonmo\\Documents\\GitHub\\csgo\\csv\\hltvrosters.csv', 'wb') as rosterscsv:
            rosterwriter = csv.writer(rosterscsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
            
            with open('C:\\Users\\wessonmo\\Documents\\GitHub\\csgo\\csv\\event_list.csv', 'wb') as eventscsv:
                eventwriter = csv.writer(eventscsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                
                for event in events[:(len(events) - 1731)]:
                    sex = None
                    pics = int(event.contents[1].contents[4].contents[0].encode("utf-8"))
                    
                    event_id = re.compile("(?<=eventid=)[0-9]{1,}").search(event.contents[1].contents[1].contents[2].get("href")).group(0)
                    event_name = re.sub("\:"," ",event.contents[1].contents[1].contents[2].text.encode("utf-8"))
                    
                    info_url = "http://www.hltv.org/?pageid=357&eventid=" + event_id
                    try:
                        len(re.compile("Online").search(str(BeautifulSoup(requests.get(info_url).content,"lxml").find_all("div",{"class":"hubFramedBox"})[0])).group(0))
                        online = 1
                    except:
                        online = 0
                    
                    print(pics,event.contents[1].contents[1].contents[2].contents[0].encode("utf-8"))
                    
                    ongoing_url = "http://www.hltv.org/matches/event/" + event_id + "/"
                    ongoing_matches = len(BeautifulSoup(requests.get(ongoing_url).content,"lxml").find_all("div", {"class": "matchListDateBox"}))
                    
                    if ongoing_matches < 1 and online == 0:
                        results_url = "http://www.hltv.org/?pageid=215&eventid=" + event_id
                        results_soup = BeautifulSoup(requests.get(results_url).content,"lxml")
                        
                        last_match_id = results_soup.find_all("div", \
                            {"class": "covResultBoxContent"})[0].contents[3].contents[1].contents[1].contents[9].contents[1].get("href")
                        last_match_url = "http://www.hltv.org" + last_match_id
                        last_match_date = re.sub(r'(?<=[0-9])[a-z]{2}\s{1,}of\s{1,}',' ',\
                            BeautifulSoup(requests.get(last_match_url).content,"lxml").find_all("span", \
                                {"style":"font-size:14px;"})[0].contents[0].encode("utf-8").strip())
                        
                        try:
                            del list_date
                        except:
                            pass
                        
                        for rank_date in set(ranks[0]):
                            if datetime.strptime(last_match_date,"%d %B %Y") > datetime.strptime(rank_date,"%Y-%m-%d"):
                                pass
                            else:
                                list_date = rank_date
                                break
                        
                        try:
                            list_date
                        except:
                            list_date = ranks[0].max()
                            
                        if len(BeautifulSoup(requests.get(info_url).content,"lxml").find_all("div", {"class": "hubTeam"})) > 0:
                            teams = BeautifulSoup(requests.get(info_url).content,"lxml").find_all("div", {"class": "hubTeam"})
                        else:
                            teams = BeautifulSoup(str(BeautifulSoup(requests.get(info_url).content,"lxml").find_all("div", \
                                {"class": "centerNoHeadline"})),"lxml").find_all("div",{"style":"margin-left:-5px;"})
                        
                        for team in teams:
                            try:
                                team.contents[0].contents[0].encode("utf-8")
                                temp_team_name = team.contents[0].contents[0].encode("utf-8")
                            except:
                                temp_team_name = team.contents[1].contents[3].contents[0].encode("utf-8")
                            
                            if temp_team_name in ranks.loc[ranks[0] == list_date,2].tolist():
                                sex = "male"
                                matches = results_soup.find_all("div",style = lambda x : x in \
                                    ["background-color:white;height:26px;", "background-color:#E6E5E5;height:26px;"])
                                for match in matches:
                                    try:
                                        "http://www.hltv.org" + match.contents[1].contents[1].contents[9].contents[1].get("href")
                                    except:
                                        break
                                    match_url = "http://www.hltv.org" + match.contents[1].contents[1].contents[9].contents[1].get("href")
                                    match_soup = BeautifulSoup(requests.get(match_url).content,"lxml")
                                    match_id = re.compile("(?<=/match/).*").search(\
                                        match.contents[1].contents[1].contents[9].contents[1].get("href")).group(0)
                                    
                                    try:
                                        demo_id = int(re.compile("(?<=demoid=)[0-9]{1,}").search(\
                                            match.contents[1].contents[1].contents[7].contents[1].get("href")).group(0))
                                    except:
                                        demo_id = None
                                    
                                    teams2 = BeautifulSoup(str(match_soup.find_all("div",{"class":"centerNoHeadline"})),"lxml").find_all("a", \
                                        {"href": re.compile("teamid=")})[:2]
                                    
                                    players = BeautifulSoup(str(match_soup.find_all("div",{"class":"hotmatchbox"})),"lxml").find_all("a", \
                                        {"href": re.compile("(/player/)|(playerid)")})
                                    n = 1
                                    for player in players:
                                        player_name = player.text.encode("utf-8")
                                        player_id = player.get("href")
                                        if n <= 5:
                                            team_name = teams2[0].text.encode("utf-8")
                                            team_id = re.compile("(?<=teamid\=)[0-9]{1,}").search(teams2[0].get("href")).group(0)
                                        else:
                                            team_name = teams2[1].text.encode("utf-8")
                                            team_id = re.compile("(?<=teamid\=)[0-9]{1,}").search(teams2[1].get("href")).group(0)
                                        n = n + 1
                                        rosterwriter.writerow([event_id,match_id,demo_id,team_name,team_id,player_name,player_id])
                                    
                                    if demo_id != None and match_id not in file_list:
                                        try:
                                            url = 'http://www.hltv.org/interfaces/download.php?demoid=' + str(demo_id)
                                            values = {'name': '',
                                                      'location': '',
                                                      'language': '' }
                                            try:
                                                headers = {'User-Agent': UserAgent().random}
                                            except:
                                                headers = {'User-Agent': UserAgent().random}
                                            
                                            data = urllib.urlencode(values)
                                            req = urllib2.Request(url,data,headers)
                                            response = urllib2.urlopen(req)
                                            read = response.read() 
                                            if not os.path.exists("D:\\CSGO Demos\\" + event_id + " - " + event_name + "\\"):
                                                os.makedirs("D:\\CSGO Demos\\" + event_id + " - " + event_name + "\\")
                                            print("open file - " + time.strftime("%c"))
                                            with open("D:\\CSGO Demos\\" + event_id + " - " + event_name + "\\" + match_id + ".rar", 'wb+') as file_:
                                                file_.write(read)
                                            file_.close()
                                            print("close file - " + time.strftime("%c"))
                                        except:
                                            pass
                                    else:
                                        pass
                                break
                            elif temp_team_name in list(females[0]):
                                sex = "female"
                                matches = results_soup.find_all("div",style = lambda x : x in \
                                    ["background-color:white;height:26px;", "background-color:#E6E5E5;height:26px;"])
                                for match in matches:
                                    try:
                                        "http://www.hltv.org" + match.contents[1].contents[1].contents[9].contents[1].get("href")
                                    except:
                                        break
                                    match_url = "http://www.hltv.org" + match.contents[1].contents[1].contents[9].contents[1].get("href")
                                    match_soup = BeautifulSoup(requests.get(match_url).content,"lxml")
                                    match_id = re.compile("(?<=/match/).*").search(\
                                        match.contents[1].contents[1].contents[9].contents[1].get("href")).group(0)
                                    
                                    try:
                                        demo_id = int(re.compile("(?<=demoid=)[0-9]{1,}").search(\
                                            match.contents[1].contents[1].contents[7].contents[1].get("href")).group(0))
                                    except:
                                        demo_id = None
                                    
                                    teams2 = BeautifulSoup(str(match_soup.find_all("div",{"class":"centerNoHeadline"})),"lxml").find_all("a", \
                                        {"href": re.compile("teamid=")})[:2]
                                    
                                    players = BeautifulSoup(str(match_soup.find_all("div",{"class":"hotmatchbox"})),"lxml").find_all("a", \
                                        {"href": re.compile("(/player/)|(playerid)")})
                                    n = 1
                                    for player in players:
                                        player_name = player.text.encode("utf-8")
                                        player_id = player.get("href")
                                        if n <= 5:
                                            team_name = teams2[0].text.encode("utf-8")
                                            team_id = re.compile("(?<=teamid\=)[0-9]{1,}").search(teams2[0].get("href")).group(0)
                                        else:
                                            team_name = teams2[1].text.encode("utf-8")
                                            team_id = re.compile("(?<=teamid\=)[0-9]{1,}").search(teams2[1].get("href")).group(0)
                                        n = n + 1
                                        rosterwriter.writerow([event_id,match_id,demo_id,team_name,team_id,player_name,player_id])
                                    
                                    if demo_id != None and match_id not in file_list:
                                        try:
                                            url = 'http://www.hltv.org/interfaces/download.php?demoid=' + str(demo_id)
                                            values = {'name': '',
                                                      'location': '',
                                                      'language': '' }
                                            try:
                                                headers = {'User-Agent': UserAgent().random}
                                            except:
                                                headers = {'User-Agent': UserAgent().random}
                                            
                                            data = urllib.urlencode(values)
                                            req = urllib2.Request(url,data,headers)
                                            response = urllib2.urlopen(req)
                                            read = response.read() 
                                            if not os.path.exists("D:\\CSGO Demos\\" + event_id + " - " + event_name + "\\"):
                                                os.makedirs("D:\\CSGO Demos\\" + event_id + " - " + event_name + "\\")
                                            print("open file - " + time.strftime("%c"))
                                            with open("D:\\CSGO Demos\\" + event_id + " - " + event_name + "\\" + match_id + ".rar", 'wb+') as file_:
                                                file_.write(read)
                                            file_.close()
                                            print("close file - " + time.strftime("%c"))
                                        except:
                                            pass
                                    else:
                                        pass
                                break
                            else:
                                break
                    else:
                        pass
                    eventwriter.writerow([int(event_id),online,sex])
except Exception,e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_tb.tb_lineno,e)