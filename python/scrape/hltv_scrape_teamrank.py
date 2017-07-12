from __future__ import division
from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
import datetime
import csv

def teamrank():
    print('########## scrape team ranks ##########')
    try:
        exist_ranks = list(pd.read_csv('csv\\hltv_team_ranks.csv', header = None)[0].drop_duplicates())
    except:
        exist_ranks = pd.DataFrame(index = range(0))
    
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    
    recent_rank_page_req = requests.get('https://www.hltv.org/ranking/teams', headers = header)
    year_hrefs = BeautifulSoup(recent_rank_page_req.content, 'lxml').find_all('div', {'class': 'filter-column-content'})[0].contents
    
    date_list = []
    for year_href in year_hrefs:
        year_url = 'https://www.hltv.org' + year_href.get('href')
        year_req = requests.get(year_url, headers = header)
        month_hrefs = BeautifulSoup(year_req.content, 'lxml').find_all('div', {'class': 'filter-column-content'})[1].contents
        for month_href in month_hrefs:
            month_url = 'https://www.hltv.org' + month_href.get('href')
            month_req = requests.get(month_url, headers = header)
            day_hrefs = BeautifulSoup(month_req.content, 'lxml').find_all('div', {'class': 'filter-column-content'})[2].contents
            for day_href in day_hrefs:
                day_url = 'https://www.hltv.org' + day_href.get('href')
                day_req = requests.get(day_url, headers = header)
                year = re.compile('(?<=teams\/)[0-9]{4}(?=\/)').search(day_url).group(0)
                month = str(datetime.datetime.strptime(re.compile('(?<=20[0-9]{2}\/).*(?=\/)').search(day_url).group(0), '%B').month)
                day = re.compile('[0-9]{1,2}$').search(day_url).group(0)
                date = month + '/' + day + '/' + year
                if date in list(list(exist_ranks) + date_list):
                    return
                else:
                    date_list.append(date)
                    team_rows = BeautifulSoup(day_req.content, 'lxml').find_all('div', {'class': 'ranked-team standard-box'})
                    print(date + ', ' + str(len(team_rows)))
                    for team in team_rows:
                        rank = int(re.sub('#','',team.contents[1].contents[1].contents[0].text.encode('utf-8')))
                        team_href = team.contents[1].contents[1].contents[2].get('data-url')
                        team_name = team.contents[1].contents[1].contents[2].text.encode('utf-8')
                        team_points = int(re.sub('[a-z]|\(|\)| ','',team.contents[1].contents[1].contents[3].text.encode('utf-8')))
                        with open("csv\\hltv_team_ranks.csv", 'ab') as rankcsv:
                            rankwriter = csv.writer(rankcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                            rankwriter.writerow([date,rank,team_name,team_href,team_points])

teamrank()