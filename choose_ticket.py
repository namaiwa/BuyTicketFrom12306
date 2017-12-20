# !/user/bin/env python
# -*- coding:utf-8 -*-
# author: ninedays time:2017/12/20
import requests
import json
import re

headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Mobile Safari/537.36', }


def getstation():
    try:
        with open('traininfo.json', 'r') as f:
            kv = json.loads(f.read())
    except FileNotFoundError:
        print('缺少文件，请运行 “get_station_info.py” 获得 “traininfo.json” 文件')

    while 1:
        startstation = input("输入出发地")
        from_station = kv.get(startstation)
        if from_station:
            break
        else:
            print('地址有误，请核实')

    while 1:
        destination = input("请输入目的地")
        to_station = kv.get(destination)
        if to_station:
            break
        else:
            print('地址有误，请核实')

    while True:
        date = input('情输入日期，格式为：YYYY-MM-DD')
        if re.match(r'201\d-[01]\d-[0123]\d', date):
            break
        else:
            print('格式有误，请核实')

    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Mobile Safari/537.36', }
    params = {
        'leftTicketDTO.train_date': date,
        'leftTicketDTO.from_station': from_station,
        'leftTicketDTO.to_station': to_station,
        'purpose_codes': 'ADULT',
    }
    url = 'https://kyfw.12306.cn/otn/leftTicket/query'
    response = requests.get(url, params=params, headers=headers, verify=False)
    traininfolist = response.json()['data']['result']
    for i in traininfolist:
        traininfo = i.split('|')
        if traininfo[0] != 'null':
            print(traininfo[3:11], traininfo[13:])
            break
    return traininfo


if __name__ == '__main__':
    info = getstation()
    print(info)
