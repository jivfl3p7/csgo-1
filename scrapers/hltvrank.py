# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 17:04:49 2017

@author: wessonmo
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import csv

with open('C:\\Users\\wessonmo\\Documents\\GitHub\\csgo\\csv\\hltvranks.csv', 'wb') as rankcsv:
    rankwriter = csv.writer(rankcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
    
    url = "http://www.hltv.org/ranking/teams/"
    soup = BeautifulSoup(requests.get(url).content,"lxml").find_all("div", {"class":"tab_groups"})
    soup2 = BeautifulSoup(str(BeautifulSoup(str(soup),"lxml").find_all("div", {"style":"z-index: 3; "})),"lxml").find_all("div", {"class":"tab_content"})
    years = BeautifulSoup(str(soup2),"lxml").find_all("a", class_ = lambda x : x in ["tab_selected","tab_unselected"])
    
    for year in years:
        url2 = "http://www.hltv.org" + year.get("href")
        soup3 = BeautifulSoup(requests.get(url2).content,"lxml").find_all("div", {"class":"tab_groups"})
        soup4 = BeautifulSoup(str(soup3),"lxml").find_all("div", {"style":"z-index: 2; "})
        months = BeautifulSoup(str(soup4),"lxml").find_all("a", class_ = lambda x : x in ["tab_selected","tab_unselected"])
        
        for month in months:
            url3 = "http://www.hltv.org" + month.get("href")
            soup5 = BeautifulSoup(requests.get(url3).content,"lxml").find_all("div", {"class":"tab_groups"})
            soup6 = BeautifulSoup(str(soup5),"lxml").find_all("div", {"style":"z-index: 1; "})
            days = BeautifulSoup(str(soup6),"lxml").find_all("a", class_ = lambda x : x in ["tab_selected","tab_unselected"])
            
            for day in days:
                url4 = "http://www.hltv.org" + day.get("href")
                teams = BeautifulSoup(requests.get(url4).content,"lxml").find_all("div", {"class":"framedBox ranking-box"})
                
                for team in teams:
                    date = datetime.strptime(day.get("href").split("/")[3] + day.get("href").split("/")[4] + day.get("href").split("/")[5],
                                             "%Y%B%d").strftime("%Y-%m-%d")
                    rank = int(re.sub("#","",team.contents[1].contents[1].contents[0].encode('utf-8')))
                    team_name = team.contents[1].contents[3].contents[3].contents[0].encode('utf-8')
                    rankwriter.writerow([date,rank,team_name])