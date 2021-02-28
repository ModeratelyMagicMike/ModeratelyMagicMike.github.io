#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
import pandas as pd
from arcgis import GIS
from arcgis.features import FeatureLayerCollection
import geopandas as gpd

'''
Updates CUBAD count indicators + campus access map, 
with freeshest accsability data from https://carleton.ca/covid19/return-to-campus/building-updates/
'''

def scrape_info():
    #Scrapes the Carleton buildings page for access updates (see above for link)
    item=[]
    #attemping connection to CU building page.
    try:
        source = requests.get('https://carleton.ca/covid19/return-to-campus/building-updates/').text 
        soup = BeautifulSoup(source,'html.parser')
    except:
        print("Incorrect Webpage.")
    table1 = soup.find('tbody')
    rows = table1.find_all('tr')
    #scraping data
    for row in rows:
        data = row.find_all('td')
        bname = data[0].get_text().strip('*')
        bacess = data[1].get_text()
        if "Restricted" in str(bacess):
            bacess = 'Restricted Access'
        else:
            bacess = 'Public Access'
        item.append((bname, bacess))
    return item

def overwrite_csv():
    #Overwrites hosted table
    global gis
    #Iniate GIS session
    username = "" 
    password = ""
    PortalUrl = ''
    gis = GIS(PortalUrl, username, password)
    it_1 = gis.content.get('layer id')
    update_flayer = FeatureLayerCollection.fromitem(it_1)
    try:
        update_flayer.manager.overwrite('path to file')
        print('Item updated!')
    except:
        print('Update failed.')
        
def join_shp(dframe):
    #Joins building code with newly created csv & shapefile
    b_code = {'Architecture Building':'AA',
             'ARISE Building':'',
              'Athletics Complex':'AC',
              'Azrieli Pavilion':'AP',
              'Azrieli Theatre':'AT',
              'Canal Building':'CB',
              'Carleton Dominion Chalmers Centre':'',
              'Carleton Technology and Training Centre':'TT',
              'Colonel By Child Care Centre':'CC',
              'Dunton Tower':'DT',
              'Health Sciences Building':'HS',
              'Herzberg Laboratories':'HP',
              'Human Computer Interaction Building':'HC',
              'Loeb Building':'LA',
              'Maintenance Building':'MB',
              'Mackenzie Building':'ME',
              'MacOdrum Library':'ML',
              'Minto CASE':'MC',
              'Nesbitt Biology Building':'NB',
              'National Wildlife Research Centre':'NW',
              'Paterson Hall':'PA',
              'Residence Buildings':'',
              'Residence Commons':'CO',
              'Richcraft Hall':'RB',
              'Robertson Hall':'RO',
              'Southam Hall':'SA',
              'Steacie Building':'SC',
              'St. Patrick’s Building':'SP',
              'Social Sciences Research Building':'SR',
              'Tory Building':'TB',
              'University Centre':'UC',
              'Visualization and Simulation Building':'VS',}
    #maps building code to building name
    dframe['BUILDABBRE'] = dframe['Building'].map(b_code)
    gpdf = gpd.read_file('path to file')
    bc_shp = gpdf.merge(dframe, on='BUILDABBRE')
    bc_shp.to_file('path to file', driver='GeoJSON')

def overwrite_map():
    #overwrites hosted map 
    it_2 = gis.content.get('layer id')
    update_flayer = FeatureLayerCollection.fromitem(it_2)
    try:
        update_flayer.manager.overwrite('path to file')
        print("Map updated!")
    except:
        print("Update failed.")
    
def main():
    b_data = scrape_info()
    df = pd.DataFrame.from_records(b_data)
    #naming df columns
    df.columns = ['Building','Access']
    df.to_csv('path to file', index=False)
    overwrite_csv()
    df1 = pd.read_csv('path to file')
    join_shp(df1)
    overwrite_map()
    

if __name__ == "__main__":
    main()
