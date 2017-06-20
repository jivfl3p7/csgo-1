# -*- coding: utf-8 -*-
"""
Created on Mon May 22 15:59:25 2017

@author: wesso
"""

import os
from pyunpack import Archive
import csv

def rar_to_demo(drive):
    zipped_folder = drive + ':\\CSGO Demos\\zipped'
    unzipped_folder = drive + 'E:\\CSGO Demos\\unzipped'
    
    for folder in os.listdir(zipped_folder):
        print('rar_to_demo, ' + folder)
        for file_ in os.listdir(zipped_folder + '\\' + folder):
            if not os.path.exists(unzipped_folder + '\\' + folder + '\\' + file_[:-4]):
                os.makedirs(unzipped_folder + '\\' + folder + '\\' + file_[:-4])
                try:
                    Archive(zipped_folder + '\\' + folder + '\\' + file_).extractall(unzipped_folder + '\\' + folder + '\\' + file_[:-4])
                except:
                    with open("csv\\demo_fails.csv", 'ab') as demofailcsv:
                        demofailwriter = csv.writer(demofailcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                        demofailwriter.writerow([folder,file_[:-4],'fail'])