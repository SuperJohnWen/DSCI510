import urllib.request
import urllib.parse
import urllib.error
import json
import sys
import pandas as pd
import time
import sqlite3


def download_data(input_url: str, sample: bool, download_key: str):
    n = 0
    while True:
        try:
            response = urllib.request.urlopen(input_url, timeout=10)
            data_json = json.loads(response.read())
            break
        except:
            n += 1
            if n == 3:
                print("Download Failed!Please check your Internet!")
                sys.exit()
    if sample:
        data_to_dict(data_json, True, download_key)
    else:
        result_data_list.extend(data_to_dict(data_json, False, download_key))
        print("current data amount: " + str(len(result_data_list)))


# Use Dataframe to show the sample dataset(5 entries)
def data_to_dict(json_dict: dict, sample: bool, key_dict: str):
    data_list = []
    df = pd.DataFrame(
        columns=['title', 'category', 'company', 'location', 'salary_predict', 'salary_max', 'salary_min',
                 'detail_url', 'class'])
    for item in json_dict['results']:
        title = item.get('title', "None")
        category = item.get('category', "None")
        if category != "None" and type(category) == dict:
            category = category.get('label', 'None')
        company = item.get('company', 'None')
        if company != "None" and type(company) == dict:
            company = company.get('display_name', 'None')
        location = item.get('location', "None")
        if location != 'None' and type(location) == dict:
            location = location.get('display_name', 'None')
        salary_predict = item.get('salary_is_predicted', '0')
        salary_max = item.get("salary_max", "None")
        salary_min = item.get("salary_min", "None")
        detail_url = item.get("redirect_url", "None")
        if sample:
            new_df = pd.DataFrame(
                columns=['title', 'category', 'company', 'location', 'salary_predict', 'salary_max', 'salary_min',
                         'detail_url', 'class'])
            new_df.loc[0] = [title, category, company, location, salary_predict, salary_max, salary_min, detail_url,
                             key_dict]
            df = pd.concat([df, new_df], ignore_index=True)
        else:
            data_list.append({'title': title, 'category': category, 'company': company, 'location': location,
                              'salary_predict': salary_predict, 'salary_max': salary_max, 'salary_min': salary_min,
                              'detail_url': detail_url, "class": key_dict})
    if sample:
        pd.set_option('display.max_columns', 8)
        pd.set_option('display.width', 200)
        conn = sqlite3.connect("jobdb.sqlite")
        if key_dict == search_keyword_job[0]:
            df.to_sql(name='Jobs_sample', con=conn, if_exists='replace')
        elif key_dict == search_keyword_language[0]:
            df.to_sql(name='Pglanguage_sample', con=conn, if_exists='replace')
        conn.close()
        print("------------------------Download complete!----------------------------")
        print("------------------------The sample data show as below!-------------------------")
        print()
        print(df)
    else:
        return data_list


def save_to_sql(result_list: list, flag: bool):
    if flag:
        conn = sqlite3.connect("jobdb.sqlite")
        cur = conn.cursor()
        cur.execute('DROP TABLE IF EXISTS Pglanguage')
        cur.execute(
            'CREATE TABLE Pglanguage (title TEXT, category TEXT, company TEXT, location TEXT, salary_predict TEXT, salary_max TEXT, salary_min TEXT, detail_url TEXT, class TEXT)')

        for item in result_list:
            insert_data = (
            item['title'], item['category'], item['company'], item['location'], item['salary_predict'], item['salary_max'],
            item['salary_min'], item['detail_url'], item['class'])
            cur.execute(
                "INSERT INTO Pglanguage (title, category, company, location, salary_predict, salary_max, salary_min, detail_url, class) VALUES (?,?,?,?,?,?,?,?,?)",
                insert_data)

        conn.commit()

        cur.close()
        conn.close()
    else:
        conn = sqlite3.connect("jobdb.sqlite")
        cur = conn.cursor()
        cur.execute('DROP TABLE IF EXISTS Jobs')
        cur.execute(
            'CREATE TABLE Jobs (title TEXT, category TEXT, company TEXT, location TEXT, salary_predict TEXT, salary_max TEXT, salary_min TEXT, detail_url TEXT, class TEXT)')

        for item in result_list:
            insert_data = (
                item['title'], item['category'], item['company'], item['location'], item['salary_predict'],
                item['salary_max'],
                item['salary_min'], item['detail_url'], item['class'])
            cur.execute(
                "INSERT INTO Pglanguage (title, category, company, location, salary_predict, salary_max, salary_min, detail_url, class) VALUES (?,?,?,?,?,?,?,?,?)",
                insert_data)

        conn.commit()

        cur.close()
        conn.close()


result_data_list = []
# arguments setting
args = sys.argv
search_keyword_language = ["Python", "Java", "JavaScript", "C++", "C#", "TypeScript", "PHP", "Swift",
                           "Kotlin", "Golang"]
search_keyword_job = ['Software Development', 'Data Science', 'Data Analysis', 'Software Test', 'Business analysis']
app_id = "cd16fb7a"
app_key = "1ed779b81b84dcc02d6c04626c1bd013"

# command executes
url = "https://api.adzuna.com/v1/api/jobs/us/search/{}?app_id={}&app_key={}&results_per_page={}&what={}"
if len(args) == 1:
    for key in search_keyword_job:
        print("--------------Begin to download 1000 records about " + key + " job-----------------")
        for i in range(1, 41):
            url1 = url.format(str(i), app_id, app_key, "50", urllib.parse.quote(key))
            download_data(url1, False, key)
            time.sleep(2.5)
            print("-----------The first " + str(i * 50) + " Complete-------------")
        print("-------------- " + key + " Download Complete-----------------")
    print("---------begin to save the data into the database-----------")
    save_to_sql(result_data_list, False)
    print("----------Save Successfully!-----------")

elif len(args) == 2 and args[1] == 'sample':
    print("--------------Begin to download sample with 5 records-----------------")
    url2 = url.format("1", app_id, app_key, "5", urllib.parse.quote(search_keyword_job[0]))
    download_data(url2, True, search_keyword_job[0])

elif len(args) == 2 and args[1] == 'pglanguage':
    for key in search_keyword_language:
        print("--------------Begin to download 1000 records about " + key + " language-----------------")
        for i in range(1, 21):
            url3 = url.format(str(i), app_id, app_key, "50", urllib.parse.quote(key))
            download_data(url3, False, key)
            time.sleep(2.5)
            print("-----------The first " + str(i * 50) + " Complete-------------")
        print("-------------- " + key + " Download Complete-----------------")
    print("---------begin to save the data into the database-----------")
    save_to_sql(result_data_list, True)
    print("----------Save Successfully!-----------")

elif len(args) == 2 and args[1] == 'sample--language':
    print("--------------Begin to download sample with 5 records-----------------")
    url4 = url.format("1", app_id, app_key, "5", urllib.parse.quote(search_keyword_language[0]))
    download_data(url4, True, search_keyword_language[0])
else:
    print("Wrong command! Please check the readme.txt")
