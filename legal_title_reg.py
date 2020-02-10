from lxml import html
import requests
import pandas as pd

#create an empty list to store the data
versions = []

#import the text file into the list
with open('faa_registry_names.txt','r') as fp:
    line = fp.readline()
    while line:
        versions.append(line.rstrip("\n").split("\t"))
        line = fp.readline()

        
def scrape(schedules):
    dept_dict = {}
    dept_counter = 0
    for version in versions :
        schedule, version_start_date, version_end_date, url = version
        if schedule in schedules:
            print(url)
            page = requests.get(url)
            print(page.status_code)
            tree = html.fromstring(page.content)

            version_depts_en = tree.xpath('//*/p[@class="BilingualItemFirst"]/text()')
            version_depts_fr = tree.xpath('//*/p[@class="BilingualItemSecond"]/text()')
            version_depts_bilingual = list(zip(version_depts_en,version_depts_fr))

            for dept in version_depts_bilingual:
                dept_name = dept[0]
                if dept_name in dept_dict:
                    #if the department already exists, extend the end date
                    dept_dict[dept_name][5] = version_end_date
                else: 
                    #if this is the first time we see this name, add the department
                    dept_counter += 1
                    dept_dict[dept_name] = [dept_counter,         #id
                                            schedule,             #schedule
                                            dept_name,            #name en 
                                            dept[1],              #name fr
                                            version_start_date,   #start date
                                            version_end_date]     #end date

    all_final_depts = pd.DataFrame.from_dict(dept_dict)
    all_final_depts = all_final_depts.T
    all_final_depts.columns = ['id','schedule','title_en','title_fr','start','end']
    all_final_depts.to_csv('schedules ' + ','.join(schedules) + '.csv', index=False)

scrape(['1','1.1','2','3'])  #financial departments
scrape(['1','4','5'])        #HR departments
