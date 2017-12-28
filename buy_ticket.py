# !/user/bin/env python
# -*- coding:utf-8 -*-
# author: ninedays time:2017/12/20
from login12306 import Login12306
from choose_ticket import getstation
import datetime
import re
import time


class Buyticket(Login12306):
    def __init__(self, username, password):
        Login12306.__init__(self, username, password)
        self.getstation = getstation

    # 实测不需要这一步！
    # def checkuser(self):
    #     url = 'https://kyfw.12306.cn/otn/login/checkUser'
    #     data = {'_json_att': ''}
    #     resp = self.session.post(url, data=data, headers=self.headers, verify=False)
    #     print(resp.json())

    def leftticket(self, startstation, destination, date, train_info):
        info_ = train_info[0]
        info_list = re.findall(r'%.{2}', info_)
        for i in info_list:
            q = chr(int(i.replace('%', '0x'), 16))
            info_ = info_.replace(i, q)
        # info_ = info_.replace('\n', '')
        today = str(datetime.date.today())
        url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        data = {
            'secretStr': info_,
            'train_date': date,
            'back_train_date': today,
            'tour_flag': 'dc',
            'purpose_codes': 'ADULT',
            'query_from_station_name': startstation,
            'query_to_station_name': destination,
            'undefined': ''
        }
        resp = self.session.post(url, data=data, headers=self.headers, verify=False)

    # 从网页中的js里获取两个变量，留作后面请求时构造data数据
    def confirmPassenger(self):
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        resp = self.session.post(url, headers=self.headers, data={'_json_att': ''}, verify=False)
        resp.status_code = resp.apparent_encoding
        token = re.search(r'globalRepeatSubmitToken = \'(.{32})\'', resp.text).group(1)
        key_check = re.search(r'\'key_check_isChange\':\'(.+?)\'', resp.text).group(1)
        return token, key_check

    # 请求道常用乘客信息，并返回第一个乘客信息
    def getPassengerDTOs(self, token):
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        data = {'_json_att': '', 'REPEAT_SUBMIT_TOKEN': token}
        resp = self.session.post(url, headers=self.headers, data=data, verify=False)
        passengerinfo = resp.json()['data']['normal_passengers'][0]
        return passengerinfo

    # 经验证，此部分吴影响，虽然Set-Cookie，但是其设置的cookie在登陆时已经设置，所以不需要这一步骤
    # def getPassCodeNew(self):
    #     url = 'https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=passenger&rand=randp'
    #     self.session.post(url, headers=self.headers, verify=False)

    # 提交乘客和车辆信息等参数
    def checkOrderInfo(self, passengerinfo, token, key_check, train_info):
        url1 = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        passenger_name = passengerinfo.get('passenger_name')
        passenger_id_no = passengerinfo.get('passenger_id_no')
        mobile_no = passengerinfo.get('mobile_no')
        if train_info[-2].isdigit():
            train_type = '1'
        else:
            train_type = 'O'
        passengerTicketStr = train_type+',0,1,'+passenger_name+',1,'+passenger_id_no+','+mobile_no+',N'
        oldPassengerStr = passenger_name+',1,'+passenger_id_no+',1_'
        data1 = {
            'cancel_flag': '2',
            'bed_level_order_num': '000000000000000000000000000000',
            'passengerTicketStr': passengerTicketStr,
            'oldPassengerStr': oldPassengerStr,
            'tour_flag': 'dc',
            'randCode': '',
            'whatsSelect': '1',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token,
            }
        self.session.post(url1, headers=self.headers, data=data1, verify=False)
        # print(data1)
        # print(resp1.json())

        year = train_info[13][:4]
        month = train_info[13][4:6]
        day = train_info[13][6:]
        time_ = datetime.datetime(int(year), int(month), int(day))
        t = time_.strftime('%a %b %d %Y ')
        url2 = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
        data2 = {
            'train_date': t+'00:00:00 GMT+0800 (中国标准时间)',
            'train_no': train_info[2],
            'stationTrainCode': train_info[3],
            'seatType': train_type,
            'fromStationTelecode': train_info[6],
            'toStationTelecode': train_info[7],
            'leftTicket': train_info[12],
            'purpose_codes': '00',
            'train_location': train_info[15],
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token,
        }
        self.session.post(url2, headers=self.headers, data=data2, verify=False)
        # print(data2)
        # print(resp2.json())

        url3 = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        data3 = {
            'passengerTicketStr': passengerTicketStr,
            'oldPassengerStr': oldPassengerStr,
            'randCode': '',
            'purpose_codes': '00',
            'key_check_isChange': key_check,
            'leftTicketStr': train_info[12],
            'train_location': train_info[15],
            'choose_seats': '',
            'seatDetailType': '000',
            'whatsSelect': '1',
            'roomType': '00',
            'dwAll': 'N',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token
        }
        self.session.post(url3, headers=self.headers, data=data3, verify=False)
        # print(data3)
        # print(resp3.text)

        #  实测发现下面这部分代码不运行也能成功订票，这段代码应该是订票成功后的跳转代码
        # url4 = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime'
        # while True:
        #     num = time.time()
        #     randomnum = str(num).replace('.', '')[:13]
        #     params = {
        #         'random': randomnum,
        #         'tourFlag': 'dc',
        #         '_json_att': '',
        #         'REPEAT_SUBMIT_TOKEN': token,
        #     }
        #     resp4 = self.session.get(url4, headers=self.headers, params=params, verify=False)
        #     print(resp4.text)
        #     orderId = resp4.json()['data']['orderId']
        #     if orderId:
        #         break
        # print(orderId)
        #
        # url5 = ''
        # data5 = {
        #     'orderSequence_no': orderId,
        #     '_json_att': '',
        #     'REPEAT_SUBMIT_TOKEN': token,
        # }
        # resp5 = self.session.post(url5, headers=self.headers, data=data5, verify=False)
        # print(resp5.json())

    def buyticket(self):
        start_station, destination_, date_, traininfo = self.getstation()
        # self.checkuser()
        self.leftticket(start_station, destination_, date_, traininfo)
        submit_token, keycheck = self.confirmPassenger()
        passengerinfo = self.getPassengerDTOs(submit_token)
        # self.getPassCodeNew()
        self.checkOrderInfo(passengerinfo, submit_token, keycheck, traininfo)
        print('购票成功，请登录12306，到未完成订单中查看并完成支付')


if __name__ == '__main__':
    username = input('请输入用户名:')
    password = input('请输入密码:')
    buy = Buyticket(username, password)
    buy.login()
    buy.buyticket()


