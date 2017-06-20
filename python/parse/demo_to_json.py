# -*- coding: utf-8 -*-
"""
Created on Mon May 22 20:12:28 2017

@author: wesso
"""

import os
import subprocess
import csv

def demo_to_json(drive, username):
    unzipped_folder = drive + ':\\CSGO Demos\\unzipped'
    json_folder = drive + ':\\CSGO Demos\\json'
    parse_string1 = 'cd C:\\Users\\' + username + '\\Documents\\Github\\dem2json && node dem2json.js '
    
    for eventid in os.listdir(unzipped_folder):
        print('demo_to_json, ' + eventid)
        for matchid in os.listdir(unzipped_folder + '\\' + eventid):
            if not os.path.exists(json_folder + '\\' + eventid + '\\' + matchid):
                os.makedirs(json_folder + '\\' + eventid + '\\' + matchid)
            for root, dirs, files in os.walk(unzipped_folder + '\\' + eventid + '\\' + matchid, topdown = False):
                files = (x for x in files if x[-4:] == '.dem')
                for idx, item in enumerate(files):
                    if not os.path.exists(json_folder + '\\' + eventid + "\\" + matchid + "\\" + matchid + "-" + str(idx) + ".json"):
                        parse_string2 = "\"" + unzipped_folder + '\\' + eventid + '\\' + matchid + "\\" + item + "\" > "
                        args = parse_string1 + parse_string2 + "\"" + json_folder + '\\' + eventid + "\\" + matchid + "\\" + matchid + "-" + str(idx) + ".json\""
                        try:
                            subprocess.check_output(args, shell = True, stderr=subprocess.STDOUT)
                        except Exception as e:
                            error_msg = str(e)
                            with open("csv\\json_fails.csv", 'ab') as jsonfailcsv:
                                jsonfailwriter = csv.writer(jsonfailcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                                jsonfailwriter.writerow([eventid,matchid,error_msg])