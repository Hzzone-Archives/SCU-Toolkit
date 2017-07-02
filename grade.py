#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
import time
import logging
import json
from bs4 import BeautifulSoup

# 配置log文件
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='lesson.log',
                filemode='w')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
headers = {
    "User-Agent": agent
}

# 学生信息
data = {
    "zjh": "",
    "mm": ""
}

param = {
    "kcId": "306003010_01",
    "preActionType": "5",
    "actionType" : "9"
}


# 教务处ip
jwc_ip = "202.115.47.141"
time_delay = 1
sleeptime = 5

# 会话
s = requests.Session()

# login 负责更新Session的cookies和登录
# first_flag 用来标记是否是第一次登录
def login(first_flag = False):
    global s
    s.headers.update(headers)
    while True:
        try:
            s.get("http://" + jwc_ip + "/loginAction.do", timeout = time_delay)
            # 再访问一次加入cookies
            r = s.get("http://" + jwc_ip + "/loginAction.do", timeout = time_delay)
            # 登录
            r = s.post("http://" + jwc_ip + "/loginAction.do", data = data, timeout = time_delay)



            # 检查密码是否正确
            r = s.get("http://" + jwc_ip + "/xkAction.do?actionType=6", timeout = time_delay)


            if "错误信息" not in r.text:
                break
            else:
                print("账号或密码不正确，请重新输入账号和密码...")
                return 0 # 账号和密码不正确
        except requests.exceptions.Timeout:
            logging.info("网络有问题，正在重连...")
        except requests.exceptions.ConnectionError as e:
            logging.info(e)
            logging.info("有可能是教务处宕机了，也有可能没联网...\n请检查网络后，重启程序")
            time.sleep(1008611)
    if first_flag:
        logging.info("登陆成功，开始工作...")
    return 1

def grade():
    global s
    global headers
    try:
        r = s.get("http://" + jwc_ip + "/gradeLnAllAction.do?type=ln&oper=fainfo&fajhh=2932", timeout = time_delay)
        soup = BeautifulSoup(r.text)
        table = soup.find(id='user')
        body = table.tbody
        courses = []
        for tr in body.findAll('tr'):
            one_course = tr.findAll('td')
            course = {}
            course['课程号'] = one_course[0].string.strip()
            course['课序号'] = one_course[1].string.strip()
            course['课程名'] = one_course[2].string.strip()
            course['英文课程名'] = one_course[3].string.strip()
            course['学分'] = one_course[4].string.strip()
            course['课程属性'] = one_course[5].string.strip()
            course['成绩'] = one_course[6].p.string.strip()
            print(str(course))
            courses.append(course)
        print('-------------------')
        info = ''

        # 中途被顶掉登录了
        if "请您登录后再使用" in r.text:
            logging.info("重复登录，程序重新登陆...")
            info = "重复登录，程序重新登陆..."
            print(info)
            login()

    except requests.exceptions.Timeout:
        logging.info("网络有问题，正在重连...")
        login()
    except requests.exceptions.ConnectionError as e:
        logging.info(e)
        logging.info("有可能是教务处宕机了，也有可能没联网...\n请检查网络后，重启程序")
        time.sleep(1008611)

    # 若不成功, 返回0
    return courses


if __name__ == "__main__":
    # 登录
    while True:
        f = open("student.json", encoding='utf-8')
        global data
        data = json.load(f)
        print(u'学号: '+data['zjh']+'  ' + u'密码: ' + data['mm'])
        if login(True) == 1:
            break

    firsttime = True # 第一次的话，就选快点，后面有个间隔就好
    courses = grade()
    initial = len(courses)
    while True:
        courses = grade()
        course_sum = len(courses)
        if course_sum>initial:
            # 发送短信
            initial = course_sum


    grade()

    logging.info("已完成所有工作...\n好好学习，天天向上！！！")

