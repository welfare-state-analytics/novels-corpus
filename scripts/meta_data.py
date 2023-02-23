from kblab import Archive
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import time
import pandas as pd
from pathlib import Path

def remove_suffix_lower(title):
    
    title=title.lower()
    if ":" in title:
        title=title.split(":")[0]
    if "." in title:
        title=title.replace(".","")
    return title

romaner=[{"meta.host_title": "Welfare state analytics"},"https://datalab.kb.se"]


def titles_mapping(filter=romaner,max_number=5000):

    home_dir=str(Path.home())
    with open(f'{home_dir}/Path/to/API_credentials', 'r') as file:
        pw = file.read().replace('\n', '')
    a = Archive("https://datalab.kb.se", auth=("demo", pw))
    books_meta={}

    for package_id in a.search(filter, max=max_number):

        for x in a.get(package_id):
            if "aip.mets.metadata" in x:

                for i in range(5):
                    backoff_time = 0.1 * (2 ** i)
                    meta=requests.get(f"{filter[1]}/{package_id}/{x}", auth=HTTPBasicAuth("demo", pw),stream=True)
                    if meta.status_code == 200:
                        root=ET.fromstring(meta.text)
                        meta_data=root.attrib
                        title=meta_data["LABEL"]
                        title=remove_suffix_lower(title)
                        books_meta[title]=package_id
                        break
            
                    else:
                        time.sleep(backoff_time)
                break

    return books_meta

def compare_words(first, second):

    same_char=0
    for char_first, char_second in zip(first, second):
        if char_first== char_second:
            same_char+=1
    similarity=same_char/max(len(first),len(second))
    if similarity>0.7:
        return True
    
    else: return False

def get_meta_data(path):

    meta_data=pd.read_excel(path)
    for i in range(len(meta_data)):
        meta_data.loc[i,"Titel"]=remove_suffix_lower(meta_data.loc[i,"Titel"][:-1])
    meta_data["Datalab ID"]=""

    for key,value in titles_mapping().items():
        key_not_in=True

        for i in range(len(meta_data)):
            if compare_words(key,meta_data.iloc[i]["Titel"]):
                meta_data.loc[i,"Datalab ID"]+=value
                key_not_in=False

        if key_not_in:
            meta_data.loc[len(meta_data)] = [key,0,0,0,0,0,value]

    return meta_data

if __name__ == "__main__":
    path=""
    metadata=get_meta_data(path)
    metadata.to_csv()