import requests
import os
import json
import time
from datetime import datetime, timedelta
#this script collects all articles with the word "Trump" in the title from the past month using the newsapi everything endpoint
def main():
    path = os.path.dirname(__file__)[:-3]
    outpath = path + 'data/'#change this to choose which folder to generate the .json files into
    key = get_key(path)

    for i in range(0, 10):
        get_json(i, path, outpath, key)
        time.sleep(3)

def get_json(iteration, path, outpath, key):
    url = 'https://newsapi.org/v2/everything?'
    today = datetime.today()
    fro = today - timedelta(days= 3 + 3 * iteration)
    to = today - timedelta(days= 3 * iteration)
    fromdate = fro.strftime('%Y-%m-%d')
    todate = to.strftime('%Y-%m-%d')

    parameters = {"q": "\"Trump\"",#this is the search keyword
                  "searchIn": "title",
                  "from": fromdate,
                  "to": todate,
                  "language": "en",
                  "pageSize": "100",
                  "apiKey": get_key(path)}
    
    for param, val in parameters.items():
        url = url + param + '=' + val + '&'
    url = url[:-1]

    response = requests.get(url)
    
    with open(outpath + f'titleSearch{fromdate}_{todate}.json', 'w') as f:
        json.dump(response.json(), f)

def get_key(directory):
    path = directory + 'credentials/api_key.md'

    with open(path, 'r') as f:
        return f.read()

if __name__ == '__main__':
    main()