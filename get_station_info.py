# !/user/bin/env python
# -*- coding:utf-8 -*-
# author: ninedays time:2017/12/14
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pymysql
import json

# 防止出现InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def getinfo():
    headers = { 'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Mobile Safari/537.36', }
    url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9035'
    response = requests.get(url, headers=headers, verify=False)
    info = response.text
    return info


def save_to_sql(info):
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3000,
        user='root',
        passwd='185949205',
        db='test',
        )
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS traininfo')
    cursor.execute('CREATE TABLE traininfo (id int primary key auto_increment,city VARCHAR(30),sign VARCHAR(10))')
    b = info[:-2].split('@')
    try:
        for i in b[1:]:
            value = i.split('|')
            a = value[1].encode('utf-8')
            b = value[2]
            cursor.execute('INSERT INTO traininfo (city,sign) VALUES (%s,%s)', (a, b))
        print('Done')
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.commit()
        conn.close()


def save_to_file(info):
    b = info[:-2].split('@')
    infokv = {}
    for i in b[1:]:
        value = i.split('|')
        infokv[value[1]] = value[2]
    with open('traininfo.json', 'w') as f:
        f.write(json.dumps(infokv))


if __name__ == '__main__':
    info = getinfo()
    save_to_file(info)
    save_to_sql(info)
