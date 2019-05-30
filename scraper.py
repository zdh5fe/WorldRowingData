import urllib.request as ulr
import re
import csv
from bs4 import BeautifulSoup
from datetime import datetime

def get_event_results(soup):
    countries = soup.find_all("td","boatCell", limit=6)
    times = soup.find_all("td","timeCell", limit=6)
    if len(countries) == 0 and len(times) == 0:
        return (countries, times, False)
    else:
        for i in range(0,min(6,len(countries))):
            countries[i] = countries[i].string.strip()
            times[i] = times[i].string.strip()
        return (countries, times, True)

def get_wbt_info(soup):
    wbt_country = soup.find("td","country")
    wbt_time = soup.find_all("td", "impact")
    wbt_event = soup.find_all("dd")
    if wbt_country is None or len(wbt_time) == 0 or len(wbt_event) == 0:
        return False
    else:
        return [wbt_country.contents[1].strip(), wbt_time[1].string.strip(), wbt_event[1].contents[1].string.strip()]

def get_event_info(soup):
    date_str = soup.time['datetime']
    date_obj = datetime.strptime(date_str, '%m/%d/%Y %I:%M:%S %p')
    location_str = soup.find(itemprop="location").string.strip()
    event_name_str = soup.find(itemprop="name").string.strip()
    return_arr = [date_obj, location_str, event_name_str]
    return return_arr

if __name__ == '__main__':
    regatta_list = ["world-rowing-championships","world-championships","olympic-games-regatta","olympic-games","worldcup-3", "world-rowing-cup-iii", "worldcup-2","world-rowing-cup-ii",
    "worldcup-1","world-rowing-cup-i","european-rowing-championships","european-championships"]
    event_list = ["lightweight-mens-single-sculls","lightweight-mens-pair","lightweight-mens-double-sculls","lightweight-mens-four","lightweight-mens-quadruple-sculls",
    "lightweight-mens-eight","mens-single-sculls","mens-pair","mens-coxed-pair","mens-double-sculls","mens-four","mens-quadruple-sculls","mens-eight","lightweight-womens-single-sculls",
    "lightweight-womens-double-sculls","lightweight-womens-quadruple-sculls","womens-single-sculls","womens-pair","womens-double-sculls","womens-four","womens-quadruple-sculls","womens-eight"]
    i = 0
    for event in event_list:
        print("Processing " + event)
        for year in range (2018,2000,-1):
            for regatta in regatta_list:
                url_string = "http://www.worldrowing.com/events/" + str(year) + "-" + regatta + "/" + event + "/"
                try:
                    page = ulr.urlopen(url_string)
                    soup = BeautifulSoup(page, features="html.parser")
                    result_countries,result_times,result_flag = get_event_results(soup)
                    info = get_event_info(soup)
                    wbt = get_wbt_info(soup)
                    csv_string = event + ".csv"
                    with open(csv_string,'a') as csvfile:
                        writer = csv.writer(csvfile, delimiter=',')
                        if i == 0:
                            writer.writerow(['Year','Event','Location','1st Place Time','1st Place Location','2nd Place Time','2nd Place Location',
                            '3rd Place Time','3rd Place Location','4th Place Time','4th Place Location','5th Place Time','5th Place Location',
                            '6th Place Time','6th Place Location'])
                            if wbt is not False:
                                writer.writerow([wbt[2][0:4], wbt[2][5:], "World Record", wbt[1], wbt[0]])
                        if result_flag is not False:
                            writer.writerow([info[0].strftime('%Y'),info[2],info[1],result_countries[0],result_times[0],result_countries[1],
                            result_times[1],result_countries[2],result_times[2],result_countries[3],result_times[3],result_countries[4],result_times[4],
                            result_countries[5],result_times[5]])
                    i = i+1
                except:
                    with open('log.txt','a') as logfile:
                        log_writer = csv.writer(logfile, delimiter=',')
                        log_writer.writerow([event,year,'URL Not Found',url_string])
