# !/user/bin/env python
# -*- coding:utf-8 -*-
# author: ninedays time:2017/12/14
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from PIL import Image

# 防止出现InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Login12306(object):
    def __init__(self, username, password):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Mobile Safari/537.36',
            }
        self.session = requests.Session()
        self.username = username
        self.password = password

    # 获取验证码图片
    def getimage(self):
        url = 'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand'
        response = self.session.get(url, headers=self.headers, verify=False)
        img = response.content
        with open("check.jpg", 'wb',) as f:
            f.write(img)
        check = Image.open("check.jpg")
        check.show()
        position = input('请输入验证码位置（第一行序号为1~4，第二行为5~8.直接输入连续数字）')
        return position

    # 提交验证码坐标
    def check(self, position):
        url = 'https://kyfw.12306.cn/passport/captcha/captcha-check'
        result_list = []
        p_list = ['30,42', '125,42', '192,42', '265,42', '30,111', '125,111', '192,111', '265,112']
        for i in position:
            result_list.append(p_list[int(i)-1])
        result = ",".join(result_list)
        data = {
            'answer': result,
            'login_site': 'E',
            'rand': 'sjrand'
        }
        response = self.session.post(url, data=data, headers=self.headers, verify=False)
        # print(response.text)
        print(response.json()["result_message"])
        return response.json()["result_code"]

    # 提交登陆信息
    def postvalue(self, username, password):
        url = 'https://kyfw.12306.cn/passport/web/login'
        data = {
            'username': username,
            'password': password,
            'appid': 'otn',
        }
        response = self.session.post(url, data=data, headers=self.headers, verify=False)
        print(response.json()["result_message"])

    # 三个post请求，第二个请求为了拿value，第一个和第三个请求会设置一个cookie
    def getlogin(self):
        url = 'https://kyfw.12306.cn/otn/login/userlogin'
        data = {'_json_att': ''}
        self.session.post(url, data=data, headers=self.headers, verify=False)
        url1 = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
        response1 = self.session.post(url1, data={'appid': 'otn'}, headers=self.headers, verify=False)
        newapptk = response1.json()["newapptk"]
        url2 = 'https://kyfw.12306.cn/otn/uamauthclient'
        response2 = self.session.post(url2, data={'tk': newapptk}, headers=self.headers, verify=False)
        # print(response1.text)                     # 验证通过
        uname = response2.json()["username"]
        print('%s,您好' % uname)         # 打印username

    # 跳转个人主页
    def myindex(self):
        # url = 'https://kyfw.12306.cn/otn/index/initMy12306'
        url = 'https://kyfw.12306.cn/otn/login/userLogin'
        response = self.session.get(url, headers=self.headers, verify=False)
        return response.text

    def login(self):
        while True:
            pos = self.getimage()
            result_code = self.check(pos)
            if result_code == "4":
                break
        self.postvalue(self.username, self.password)
        self.getlogin()
        return self.myindex()


if __name__ == '__main__':
    username = input('请输入用户名:')
    password = input('请输入密码:')
    loginto = Login12306(username, password)
    response = loginto.login()
    print(response)
