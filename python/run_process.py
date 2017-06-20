# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 16:21:07 2017

@author: wesso
"""

import sys
sys.path.append('C:\\Users\\wesso\\Documents\\Github\\csgo\\python')

from scrape.hltv_scrape_teamrank import teamrank
teamrank()
from scrape.hltv_scrape_event import event
event()
from scrape.hltv_scrape_match import match
match()
from scrape.hltv_scrape_demo import demo
demo()

from parse.rar_to_demo import rar_to_demo
rar_to_demo()
from parse.demo_to_json import demo_to_json
demo_to_json()
from parse.json_to_csv import json_to_csv
json_to_csv()

from other.team_name_match import team_name_match
team_name_match()

