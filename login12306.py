# !/user/bin/env python
# -*- coding:utf-8 -*-
# author: ninedays time:2017/12/14
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


# 防止出现InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Mobile Safari/537.36',
}
session = requests.Session()


# 获取验证码图片
def getimage():
    url = 'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand'
    response = session.get(url, headers=headers, verify=False)
    img = response.content
    with open("check.jpg", 'wb',) as f:
        f.write(img)
    position = input('请输入验证码位置（第一行序号为1~4，第二行为5~8.直接输入连续数字）')
    return position


# 提交验证码坐标
def check(position):
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
    response = session.post(url, data=data, headers=headers, verify=False)
    # print(response.text)
    print(response.json()["result_message"])
    return response.json()["result_code"]


# 提交登陆信息
def login(username='shangxu0927', password='1994shangxu0927'):
    url = 'https://kyfw.12306.cn/passport/web/login'
    data = {
        'username': username,
        'password': password,
        'appid': 'otn',
    }
    response = session.post(url, data=data, headers=headers, verify=False)
    print(response.json()["result_message"])


# 跳转'https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin'，跳转之后新网页会设置一个cookie
def userlogin():
    url = 'https://kyfw.12306.cn/otn/login/userlogin'
    data = {'_json_att': ''}
    session.post(url, data=data, headers=headers, verify=False)


# 两个post请求，第一个请求为了拿value，第二个请求会设置一个cookie
def getlogin():
    url1 = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
    url2 = 'https://kyfw.12306.cn/otn/uamauthclient'
    response1 = session.post(url1, data={'appid': 'otn'}, headers=headers, verify=False)
    newapptk = response1.json()["newapptk"]
    response2 = session.post(url2, data={'tk': newapptk}, headers=headers, verify=False)
    # print(response1.text)                     # 验证通过
    uname = response2.json()["username"]
    print('恭喜您，登陆成功， %s' % uname)         # 打印username


# 跳转个人主页
def myindex():
    # url = 'https://kyfw.12306.cn/otn/index/initMy12306'
    url = 'https://kyfw.12306.cn/otn/login/userLogin'
    response = session.get(url, headers=headers, verify=False)
    return response.text


if __name__ == '__main__':
    while 1:
        pos = getimage()
        result_code = check(pos)
        if result_code == "4":
            break
    username = input('请输入用户名:')
    password = input('请输入密码:')
    login()
    userlogin()
    getlogin()
    response_ = myindex()
    print(response_)
