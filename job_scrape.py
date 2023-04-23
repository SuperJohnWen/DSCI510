import sys
import requests
import bs4
import time
import sqlite3
import pandas as pd
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}


def data_download(input_url: str, sample: bool, class_name: str):
    n = 0
    while True:
        try:
            response = requests.get(input_url, headers=headers, timeout=10)
            soup = bs4.BeautifulSoup(response.text, 'html.parser')
            break
        except:
            n += 1
            if n > 10:
                print("Download Falied! Please check your Internet!")
                sys.exit()
    if sample:
        df = pd.DataFrame(columns=["title", "company_name", "detail_url", "class"])
        job_list = soup.find_all("li")
        for li in job_list[:5]:
            hrefs = li.find_all("a")
            if len(hrefs) == 0:
                detail_url = "None"
                company_name = li.find("h4").text.strip()
            elif len(hrefs) == 1:
                detail_url = hrefs[0]['href']
                company_name = li.find("h4").text.strip()
            else:
                detail_url = hrefs[0]['href']
                company_name = hrefs[1].text.strip()
            title = li.find("h3").text.strip()
            new_df = pd.DataFrame(
                columns=["title", "company_name", "detail_url", "class"])
            new_df.loc[0] = [title, company_name, detail_url, class_name]
            df = pd.concat([df, new_df], ignore_index=True)
        pd.set_option('display.max_columns', 8)
        pd.set_option('display.width', 200)
        conn = sqlite3.connect("jobdb.sqlite")
        df.to_sql(name="Joblinkedin_sample", con=conn, if_exists='replace')
        conn.close()
        print("------------------------Download complete!----------------------------")
        print("------------------------The sample data show as below!-------------------------")
        print()
        print(df)
    else:
        job_list = soup.find_all("li")
        for li in job_list:
            hrefs = li.find_all("a")
            if len(hrefs) == 0:
                detail_url = "None"
                company_name = li.find("h4").text.strip()
            elif len(hrefs) == 1:
                detail_url = hrefs[0]['href']
                company_name = li.find("h4").text.strip()
            else:
                detail_url = hrefs[0]['href']
                company_name = hrefs[1].text.strip()
            title = li.find("h3").text.strip()
            result_list.append({'title': title, 'company_name': company_name, 'detail_url': detail_url, 'class': class_name})
        print("The current data amount is " + str(len(result_list)))


def db_create_table():
    conn = sqlite3.connect("jobdb.sqlite")
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS Joblinkedin')
    cur.execute(
        'CREATE TABLE JobLinkedin (title TEXT, company TEXT, detail_url TEXT, class TEXT)')
    conn.commit()
    cur.close()
    conn.close()


def db_operation(data: list):
    conn = sqlite3.connect("jobdb.sqlite")
    cur = conn.cursor()
    for item in data:
        insert_data = (item['title'], item['company_name'], item['detail_url'], item['class'])
        cur.execute(
            "INSERT INTO Joblinkedin (title, company, detail_url, class) VALUES (?,?,?,?)",
            insert_data)

    conn.commit()

    cur.close()
    conn.close()


base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={}&location=United%20States&trk=guest_job_search_jobs-search-bar_search-submit&redirect=false&original_referer=&start={}"
search_keyword = ['Software Development', 'Data Science', 'Data Analysis', 'Software Test', 'Business analysis']
result_list = []
if len(sys.argv) == 1:
    #db_create_table()
    for key in search_keyword[1:]:
        i = 0
        print("--------------Begin to download 1000 records about " + key + " job-----------------")
        while i < 1000:
            url = base_url.format(key, i)
            data_download(url, False, key)
            print("-----------The first " + str(i+25) + " Complete-------------")
            time.sleep(2.5)
            i += 25
        print("-------------- " + key + " Download Complete-----------------")
        print("--------------Save 1000 record of " + key + "into database")
        db_operation(result_list)
        print("--------------Save Successfully!---------------")
        result_list = []
elif len(sys.argv) == 2 and sys.argv[1] == 'sample':
    url = base_url.format(search_keyword[0], "0")
    print("--------------Begin to download sample with 5 records-----------------")
    data_download(url, True, search_keyword[0])
