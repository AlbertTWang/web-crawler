#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from googleapiclient.discovery import build
import requests
from bs4 import BeautifulSoup
from API_KEY import api_key, cse_id
from datetime import datetime

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey = api_key)
    res = service.cse().list(q = search_term, cx = cse_id, **kwargs).execute()
    return res

data = pd.read_excel('web_scraping.xlsx')

startTime = datetime.now()
i = 0
for index, row in data.iterrows():
    if (i >= 5):
        break
    state = row['State']
    city = row['City']
    checked = row['Checked']

    if(checked == "Done"):
        continue
    
    if(state == "Washington"):
        print("FINDING SITE...")
        result = google_search(state + " state " + city + " city website", api_key, cse_id)
        print("Site: " + result['items'][0]['formattedUrl'])
        data.loc[index, "Website"] = result['items'][0]['formattedUrl']
        print("CRAWLING SITE...")
        url = result['items'][0]['formattedUrl']
        if("http://" not in url and "https://" not in url):
            url = "http://" + url
        
        try:
            response = requests.get(url)
        except:
            data.loc[index, "Checked"] = "Done"
            i += 1
            continue
        
        soup = BeautifulSoup(response.text, 'html.parser')
        first_level_links = set()
        second_level_links = set()
        third_level_links = set()
        email_set = set()
        
        for link in soup.find_all('a'): #collect front page emails & hyperlinks
            first_level_links.add(str(link.get('href')))
            if("@" in str(link.get('href')) and "mailto:" in str(link.get('href'))):
                    email_set.add(link.get('href')[7:])
                    
        print("Front Page Complete")
        
        for link in first_level_links: #collect first level emails & hyperlinks
            if("http://" not in link and "https://" not in link):
                link = "http://" + link
            try:
                response = requests.get(link)
            except:
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            for email in soup.findAll('a'):
                second_level_links.add(str(email.get('href')))
                if("@" in str(email.get('href')) and "mailto:" in str(email.get('href'))):
                    email_set.add(email.get('href')[7:])
                    
        print("First Level Complete")
        
        for link in second_level_links: #collect second level emails & hyperlinks
            if("http://" not in link and "https://" not in link):
                link = "http://" + link
            try:
                response = requests.get(link)
            except:
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            for email in soup.findAll('a'):
                third_level_links.add(str(email.get('href')))
                if("@" in str(email.get('href')) and "mailto:" in str(email.get('href'))):
                    email_set.add(email.get('href')[7:])
                    
        print("Second Level Complete")
        print(len(first_level_links))
        print(len(second_level_links))
        print(len(third_level_links))
#        for link in third_level_links: #collect third level emails
#            if("http://" not in link and "https://" not in link):
#                link = "http://" + link
#            try:
#                response = requests.get(link)
#            except:
#                continue
#            soup = BeautifulSoup(response.text, 'lxml')
#            for email in soup.findAll('a'):
#                if("@" in str(email.get('href')) and "mailto:" in str(email.get('href'))):
#                    email_set.add(email.get('href')[7:])
#                    
#        print("Third Level Complete")    
        print("Email List: " + str(email_set))
        data.loc[index, "Mayor Email"] = str(list(email_set))
        data.loc[index, "Checked"] = "Done"
        
        i += 1
        print("Total Completed: " + str(i) + "\n")

print("Time Taken: " + str(datetime.now() - startTime))
data.to_excel("web_scraping.xlsx", encoding='utf-8', index=False)
