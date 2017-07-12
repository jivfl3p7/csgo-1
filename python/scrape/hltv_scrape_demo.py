import os
import re
import pandas as pd
import csv
import urllib2

def demo():
    print('########## scrape demos ##########')
    try:
        exist_demos = list(pd.read_csv('csv\\hltv_demos.csv', header = None)[1])
        try:
            rar_fail = list(pd.read_csv('csv\\rar_fails.csv', header = None)[1])
            exist_demos = exist_demos + rar_fail
        except:
            pass
    except:
        exist_demos = pd.DataFrame(index = range(0), columns = [0,1])
    
    zipped_folder = 'E:\\CSGO Demos\\zipped'
    
    hltv_matches = pd.read_csv('csv\\hltv_match_info.csv', header = None)
    hltv_eventids = list(hltv_matches.loc[pd.isnull(hltv_matches[2]) == False,0])
    hltv_matchids = list(hltv_matches.loc[pd.isnull(hltv_matches[2]) == False,1])
    hltv_demoids = list(hltv_matches.loc[pd.isnull(hltv_matches[2]) == False,2])
    
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    
    prev_eventid = None
    for eventid, matchid, demoid in zip(hltv_eventids, hltv_matchids, hltv_demoids):
        if demoid not in exist_demos:
            eventid2 = re.compile('(?<=events\/)[0-9]{1,}(?=\/)').search(eventid).group(0)
            matchid2 = re.compile('(?<=matches\/)[0-9]{1,}(?=\/)').search(matchid).group(0)
            if not os.path.exists(zipped_folder + '\\' + eventid2 + '\\'):
                os.makedirs(zipped_folder + '\\' + eventid2 + '\\')
            if not os.path.exists(zipped_folder + '\\' + eventid2 + '\\' + matchid2 + '.rar'):
                if eventid != prev_eventid:
                    num_hltv_demos = len(hltv_matches.loc[(hltv_matches[0] == eventid) & (pd.isnull(hltv_matches[2]) == False),2])
                    path, dirs, files = os.walk(zipped_folder + '\\' + eventid2 + '\\').next()
                    num_exist_demos = len(files)
                    print(eventid + ', ' + str(num_exist_demos) + '/' + str(num_hltv_demos))
                    prev_eventid = eventid
                try:            
                    demo_url = 'https://www.hltv.org' + demoid
                    req = urllib2.Request(demo_url,headers = header)
                    response = urllib2.urlopen(req)
                    read = response.read()
                    with open(zipped_folder + '\\' + eventid2 + '\\' + matchid2 + '.rar', 'wb+') as file_:
                        file_.write(read)
                    file_.close()
                    with open('csv\\hltv_demos.csv', 'ab') as democsv:
                        demowriter = csv.writer(democsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                        demowriter.writerow([eventid,matchid,demoid,None])
                except Exception, e:
                    with open('csv\\rar_fails.csv', 'ab') as failcsv:
                        failwriter = csv.writer(failcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                        failwriter.writerow([matchid,demoid,str(e)])
                print(matchid)
            else:
                with open('csv\\hltv_demos.csv', 'ab') as democsv:
                    demowriter = csv.writer(democsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                    demowriter.writerow([matchid,demoid,None])
                
demo()