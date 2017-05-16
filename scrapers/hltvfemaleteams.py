# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 20:37:08 2017

@author: wessonmo
"""

import requests
from bs4 import BeautifulSoup
import os
import csv
import re

female_exist = os.path.exists('C:\\Users\\wessonmo\\Documents\\GitHub\\csgo\\csv\\hltvfemaleteams.csv')

archive_url = "http://www.hltv.org/?pageid=184"
soup = BeautifulSoup(requests.get(archive_url).content,"lxml").find_all("div", {"class": "covMainBoxContent"})
events = BeautifulSoup(str(soup),"lxml").find_all("div", style = lambda x : x in \
    ["width:606px;height:22px;background-color:white", "width:606px;height:22px;background-color:#E6E5E5"])    

if female_exist:
    with open('C:\\Users\\wessonmo\\Documents\\GitHub\\csgo\\csv\\hltvfemaleteams.csv', 'a') as femalecsv:
        femalewriter = csv.writer(femalecsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
        for event in events:
            try:
                re.compile("female").search(event.contents[1].contents[1].contents[2].text.encode("utf-8").lower()).group(0)
                
                event_url = "http://www.hltv.org/" + event.contents[1].contents[1].contents[2].get("href")
                            
                if len(BeautifulSoup(requests.get(event_url).content,"lxml").find_all("div", {"class": "hubTeam"})) > 0:
                    teams = BeautifulSoup(requests.get(event_url).content,"lxml").find_all("div", {"class": "hubTeam"})
                else:
                    teams = BeautifulSoup(str(BeautifulSoup(requests.get(event_url).content,"lxml").find_all("div", \
                        {"class": "centerNoHeadline"})),"lxml").find_all("div",{"style":"margin-left:-5px;"})
                
                for team in teams:
                    try:
                        femalewriter.writerow([re.sub(r"\\n","",team.contents[0].text.encode("utf-8")).strip()])
                    except:
                        femalewriter.writerow([re.sub(r"\\n","",team.contents[1].text.encode("utf-8")).strip()])
            except:
                pass
else:
    with open('C:\\Users\\wessonmo\\Documents\\GitHub\\csgo\\csv\\hltvfemaleteams.csv', 'wb') as femalecsv:
        femalewriter = csv.writer(femalecsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)  
        for event in events:
            try:
                re.compile("female").search(event.contents[1].contents[1].contents[2].text.encode("utf-8").lower()).group(0)
                
                event_url = "http://www.hltv.org/" + event.contents[1].contents[1].contents[2].get("href")
                            
                if len(BeautifulSoup(requests.get(event_url).content,"lxml").find_all("div", {"class": "hubTeam"})) > 0:
                    teams = BeautifulSoup(requests.get(event_url).content,"lxml").find_all("div", {"class": "hubTeam"})
                else:
                    teams = BeautifulSoup(str(BeautifulSoup(requests.get(event_url).content,"lxml").find_all("div", \
                        {"class": "centerNoHeadline"})),"lxml").find_all("div",{"style":"margin-left:-5px;"})
                
                for team in teams:
                    try:
                        femalewriter.writerow([re.sub(r"\\n","",team.contents[0].text.encode("utf-8")).strip()])
                    except:
                        femalewriter.writerow([re.sub(r"\\n","",team.contents[1].text.encode("utf-8")).strip()])
                    
            except:
                pass