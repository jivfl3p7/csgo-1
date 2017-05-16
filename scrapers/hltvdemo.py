# -*- coding: utf-8 -*-
"""
Created on Thu May 04 15:57:08 2017

@author: wesso
"""

import pandas as pd
import csv
import os
from fake_useragent import UserAgent
import urllib
import urllib2

hltv_demo_exist = os.path.exists("csv\\hltvdemos.csv")

hltv_matches = pd.read_csv("csv\\hltvmatches.csv", header = None)
want_events = list(hltv_matches.loc[pd.isnull(hltv_matches[2]) == False,0])
want_event_names = list(hltv_matches.loc[pd.isnull(hltv_matches[2]) == False,1])
want_matches = list(hltv_matches.loc[pd.isnull(hltv_matches[2]) == False,2])
want_demos = list(hltv_matches.loc[pd.isnull(hltv_matches[2]) == False,3])


if hltv_demo_exist:
    exist_demos = pd.read_csv("csv\\hltvdemos.csv", header = None)
    demos_list = list(exist_demos.loc[0])
    
    with open("csv\\hltvdemos_update.csv", 'wb') as demoupdatecsv:
        demoupdatewriter = csv.writer(demoupdatecsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
        
        for event_id,event_name,match_id,demo_id in zip(want_events,want_event_names,want_matches,want_demos):
            if demo_id not in demos_list:
                demo_url = "http://www.hltv.org/interfaces/download.php?demoid=" + str(demo_id)
                values = {'name': '',
                              'location': '',
                              'language': '' }
                try:
                    try:
                        headers = {'User-Agent': UserAgent().random}
                    except:
                        headers = {'User-Agent': UserAgent().random}                
                    data = urllib.urlencode(values)
                    req = urllib2.Request(demo_url,data,headers)
                    response = urllib2.urlopen(req)
                    read = response.read() 
                    if not os.path.exists("D:\\CSGO Demos\\" + str(event_id) + " - " + event_name + "\\"):
                        os.makedirs("D:\\CSGO Demos\\" + str(event_id) + " - " + event_name + "\\")
                    with open("D:\\CSGO Demos\\" + str(event_id) + " - " + event_name + "\\" + str(match_id) + ".rar", 'wb+') as file_:
                        file_.write(read)
                    file_.close()
                    demoupdatewriter.writerow([demo_id,None])
                except Exception, e:
                    demoupdatewriter.writerow([demo_id,str(e)])
            else:
                pass
            
    update_demos = pd.read_csv("csv\\hltvdemos_update.csv", header = None)
        
    with open("csv\\hltvdemos.csv", 'wb') as demoscsv:
        exist_demos[~exist_demos[0].isin(list(update_demos[0]))].to_csv(demoscsv, header = False)
        update_demos.to_csv(demoscsv, header = False)
else:
    with open("csv\\hltvdemos.csv", 'wb') as democsv:
        demowriter = csv.writer(democsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
        
        for demo_id in want_demos:
            demo_url = "http://www.hltv.org/interfaces/download.php?demoid=" + str(demo_id)
            values = {'name': '',
                          'location': '',
                          'language': '' }
            try:
                try:
                    headers = {'User-Agent': UserAgent().random}
                except:
                    headers = {'User-Agent': UserAgent().random}                
                data = urllib.urlencode(values)
                req = urllib2.Request(demo_url,data,headers)
                response = urllib2.urlopen(req)
                read = response.read() 
                if not os.path.exists("D:\\CSGO Demos\\" + str(event_id) + " - " + event_name + "\\"):
                    os.makedirs("D:\\CSGO Demos\\" + str(event_id) + " - " + event_name + "\\")
                with open("D:\\CSGO Demos\\" + str(event_id) + " - " + event_name + "\\" + str(match_id) + ".rar", 'wb+') as file_:
                    file_.write(read)
                file_.close()
                demoupdatewriter.writerow([demo_id,None])
            except Exception, e:
                demoupdatewriter.writerow([demo_id,str(e)])