import requests
import time
import sys
import sqlite3
from bs4 import BeautifulSoup
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}


def download_data(input_data: list, sample: bool):
    n = 0
    i = 0
    insert_list = []
    for item in input_data:
        while True:
            try:
                response = requests.get(item[2], headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                break
            except:
                n += 1
                time.sleep(1)
                if n > 50:
                    print("Download Failed! Please Check Your Internet!")
                    sys.exit()
        description = soup.find("div", class_='show-more-less-html__markup')
        if description is None:
            description_text = "None"
        else:
            description_list = description.find_all("li")
            if len(description_list) == 0:
                description_text = description.text.strip()
            else:
                string_list = []
                for string_item in description_list:
                    string_list.append(string_item.text.strip())
                description_text = ".".join(string_list)
        job_attribute = soup.find_all("span",
                                        class_='description__job-criteria-text description__job-criteria-text--criteria')
        level = job_attribute[0].text.strip()
        employment_type = job_attribute[1].text.strip()
        job_function = job_attribute[2].text.strip()
        insert_item = {'title': item[0], 'description': description_text, 'level': level,
                        'employment_type': employment_type, 'job_function': job_function, 'class': item[3]}
        insert_list.append(insert_item)
        i += 1
        print(str(i) + " completed")
        time.sleep(5)
        if i % 10 == 0:
            print("number " + str(i) + " job detailed saved!")
            db_insert(insert_list)
            insert_list = []
            time.sleep(12)
    if sample:
        df_dict = {key: [d.get(key) for d in insert_list] for key in insert_list[0].keys()}
        df = pd.DataFrame(df_dict)
        conn = sqlite3.connect("jobdb.sqlite")
        df.to_sql(name="JobDetail_sample", con=conn, if_exists='replace')
        conn.close()
        pd.set_option('display.max_columns', 8)
        pd.set_option('display.width', 200)
        print("------------------------Download complete!----------------------------")
        print("------------------------The sample data show as below!-------------------------")
        print()
        print(df)


def table_creation():
    conn = sqlite3.connect("jobdb.sqlite")
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS JobDetail')
    cur.execute(
        'CREATE TABLE JobDetail (title TEXT, description TEXT, levels TEXT, '
        'employment_type TEXT, job_function TEXT, class TEXT )')
    conn.commit()
    cur.close()
    conn.close()


def db_query():
    conn = sqlite3.connect('jobdb.sqlite')
    cur = conn.cursor()

    cur.execute("SELECT * FROM JobLinkedin")
    data_list = cur.fetchall()

    cur.close()
    conn.close()
    return data_list


def db_insert(input_list):
    conn = sqlite3.connect('jobdb.sqlite')
    cur = conn.cursor()

    for entries in input_list:
        insert_data = (entries['title'], entries['description'], entries['level'],
                       entries['employment_type'], entries['job_function'], entries['class'])
        cur.execute("INSERT INTO JobDetail (title, description, levels, employment_type, job_function, class) VALUES (?,?,?,?,?,?)", insert_data)

    conn.commit()
    cur.close()
    conn.close()


if len(sys.argv) == 1:
    data = db_query()
    table_creation()
    # 0-50 1000-1050  2000-2050  3000-3050  4000-4050
    download_data(data[0:50], False)
    time.sleep(10)
    download_data(data[1000:1050], False)
    time.sleep(10)
    download_data(data[2000:2050], False)
    time.sleep(10)
    download_data(data[3000:3050], False)
    time.sleep(10)
    download_data(data[4000:4050], False)
if len(sys.argv) == 2 and sys.argv[1] == 'sample':
    data = db_query()
    print("--------------Begin to download sample with 5 records-----------------")
    download_data(data[0:5], True)

