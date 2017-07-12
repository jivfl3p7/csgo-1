import os
from pyunpack import Archive
import csv

def rar_to_demo():
    print('########## rar to demo ##########')
    zipped_folder = r'E:\\CSGO Demos\\zipped'
    unzipped_folder = r'E:\\CSGO Demos\\unzipped'
    
    for folder in os.listdir(zipped_folder):
        for file_ in os.listdir(zipped_folder + '\\' + folder):
            if not os.path.exists(unzipped_folder + '\\' + folder + '\\' + file_[:-4]):
                os.makedirs(unzipped_folder + '\\' + folder + '\\' + file_[:-4])
                try:
                    Archive(zipped_folder + '\\' + folder + '\\' + file_).extractall(unzipped_folder + '\\' + folder + '\\' + file_[:-4])
                    print(zipped_folder + '\\' + folder + '\\' + file_)
                except:
                    with open('csv\\demo_fails.csv', 'ab') as demofailcsv:
                        demofailwriter = csv.writer(demofailcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                        demofailwriter.writerow([folder,file_[:-4],'fail'])
                        
rar_to_demo()