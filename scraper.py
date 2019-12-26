import urllib.request as ulr
import re
import csv
from bs4 import BeautifulSoup
from datetime import datetime


#Method that gets the results of an event at a regatta
#Takes in that event's html page as a parameter
#Returns a list of countries in the A-final, list of their times, and a flag to indicate if there were no results on the page
def get_event_results(soup):
    #For the html page, pull out the first six countries and times with results (A final only)
    countries = soup.find_all("td","boatCell", limit=6)
    times = soup.find_all("td","timeCell", limit=6)
    #If at a given regata, the boat was not an entry (i.e. Olympic boat classes at non-olympic worlds), raise a flag
    if len(countries) == 0 and len(times) == 0:
        return (countries, times, False)
    else:
        for i in range(0,6):
            #Strip html off so the result is a list of countries and a list of times
            if i < len(countries):
                countries[i] = countries[i].string.strip()
                times[i] = times[i].string.strip()
            #If the A-final had less than 6 entries (cough cough lightweight pair, fill in the rest of the list with blanks)
            else:
                countries.append("")
                times.append("")
        return (countries, times, True)

#Method that gets the world's best time for an event
#Takes in the event's html page as a parameter
#Returns the time, country, and which regatta the world record was set at
def get_wbt_info(soup):
    #Pull the country, time, and regatta out of the event page
    wbt_country = soup.find("td","country")
    wbt_time = soup.find_all("td", "impact")
    wbt_event = soup.find_all("dd")
    #If there is any missing information for the world time, return False to indicate malformed wbt info
    if wbt_country is None or len(wbt_time) == 0 or len(wbt_event) == 0:
        return False
    else:
        #Strip html away and return list of strings of the country, time, and regatta
        return [wbt_country.contents[1].strip(), wbt_time[1].string.strip(), wbt_event[1].contents[1].string.strip()]

#Gets regatta info for an html page
#Takes the soup of the html page as a parameter
#Returns the date, location, and date of that regatta
def get_event_info(soup):
    #Pull the date and convert to a datetime for easier printing to csv
    date_str = soup.time['datetime']
    date_obj = datetime.strptime(date_str, '%m/%d/%Y %I:%M:%S %p')
    #Pull the location and event name, and then return a list of all three
    location_str = soup.find(itemprop="location").string.strip()
    event_name_str = soup.find(itemprop="name").string.strip()
    return [date_obj, location_str, event_name_str]

#Main method, this is where the donuts are made
if __name__ == '__main__':
    #List of all strings included in URL's for the different regattas
    #Pre-2015 World Cups used 'worldcup-1' and Post-2015 World Cups used 'world-rowing-cup-i'
    #Pre-2014 World Championships used 'world-championships' and Post-2014 World Championships used 'world-rowing-championships'
    #The script will try both patterns of URL for each year, and just move on if the URL does not exist
    regatta_list = ["world-rowing-championships","world-championships","olympic-games-regatta","olympic-games","worldcup-3", "world-rowing-cup-iii", "worldcup-2","world-rowing-cup-ii",
    "worldcup-1","world-rowing-cup-i","european-rowing-championships","european-championships"]

    #List of all events at a regatta
    #The script will try every event for every regatta, and just move on if the URL does not exist because the event was not run at that regatta
    event_list = ["lightweight-mens-single-sculls","lightweight-mens-pair","lightweight-mens-double-sculls","lightweight-mens-four","lightweight-mens-quadruple-sculls",
    "lightweight-mens-eight","mens-single-sculls","mens-pair","mens-coxed-pair","mens-double-sculls","mens-four","mens-quadruple-sculls","mens-eight","lightweight-womens-single-sculls",
    "lightweight-womens-double-sculls","lightweight-womens-pair","lightweight-womens-quadruple-sculls","womens-single-sculls","womens-pair","womens-double-sculls","womens-four","womens-quadruple-sculls","womens-eight"]

    #Go through each event in the list
    for event in event_list:
        i = 0
        print("Processing " + event)
        #get data for the given event for every year from 2000 to 2018
        for year in range (2019,2000,-1):
            #For each given year and event, get that year's results from world championships, world cups 1,2,3, and european championships
            for regatta in regatta_list:
                url_string = "http://www.worldrowing.com/events/" + str(year) + "-" + regatta + "/" + event + "/"
                #If the url exists
                try:
                    #Set up the soup to parse html
                    page = ulr.urlopen(url_string)
                    soup = BeautifulSoup(page, features="html.parser")
                    #Get the results, regatta info, and world time info
                    result_countries,result_times,result_flag = get_event_results(soup)
                    info = get_event_info(soup)
                    wbt = get_wbt_info(soup)
                    #Open the csv for the event
                    csv_string = "datasets/" + event + ".csv"
                    with open(csv_string,'a') as csvfile:
                        writer = csv.writer(csvfile, delimiter=',')
                        #If first regatta for the given event, add header and world best time info if it exists
                        if i == 0:
                            writer.writerow(['Year','Event','Location','1st Place Time','1st Place Location','2nd Place Time','2nd Place Location',
                            '3rd Place Time','3rd Place Location','4th Place Time','4th Place Location','5th Place Time','5th Place Location',
                            '6th Place Time','6th Place Location'])
                            if wbt is not False:
                                writer.writerow([wbt[2][0:4], wbt[2][5:], "World Record", wbt[1], wbt[0],"","","","","","","","","",""])
                            else:
                                with open('log.txt','a') as logfile:
                                    log_writer = csv.writer(logfile, delimiter=',')
                                    log_writer.writerow([event,year,'World Best Time Data Not Available'])
                        #If results exist, write them to the csv
                        if result_flag is not False:
                            writer.writerow([info[0].strftime('%Y'),info[2],info[1],result_times[0],result_countries[0],result_times[1],
                            result_countries[1],result_times[2],result_countries[2],result_times[3],result_countries[3],result_times[4],result_countries[4],
                            result_times[5],result_countries[5]])
                    i = i+1
                #otherwise, url doesn't exist, so log it
                except:
                    with open('log.txt','a') as logfile:
                        log_writer = csv.writer(logfile, delimiter=',')
                        log_writer.writerow([event,year,'URL Not Found',url_string])
