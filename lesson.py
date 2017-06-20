#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
import time
import logging
import json

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

# 课程信息
courses = []
course = {
    "kch" : "",
    "cxkxh" : "",
    "done" : False
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

# 选课子程序
# urp教务系统需要按照步骤一步一步完成
def xk(param, lesson):
    global s
    global headers
    try:
        # 查找课程
        r = s.get("http://" + jwc_ip + "/xkAction.do?actionType=-1", timeout = time_delay)
        r = s.get("http://" + jwc_ip + "/xkAction.do?actionType=5&pageNumber=-1&cx=ori", timeout = time_delay)
        r = s.post("http://" + jwc_ip + "/xkAction.do", data = lesson, timeout = time_delay)
        # print(lesson)
        # print(r.text)
        # 选课
        r = s.post("http://" + jwc_ip + "/xkAction.do", data = param, timeout = time_delay)
        # print(param)
        info = ''

        # 中途被顶掉登录了
        if "请您登录后再使用" in r.text:
            logging.info("重复登录，程序重新登陆...")
            info = "重复登录，程序重新登陆..."
            print(info)
            login()

        # 课余量不足
        # 并不需要显示这个信息 因为很多时候都是这个状态
        # 使用debug
        elif "没有课余量" in r.text:
            logging.debug("课程" + ' ' + param["kcId"] + ' ' + "没有课余量...")
            info = "课程" + ' ' + param["kcId"] + ' ' + "没有课余量..."
            print(info)
        # 非选课时间
        elif "非选课阶段" in r.text:
            logging.info("现阶段不允许选课\n具体时间请参看学校教务处公告...")
            info = "现阶段不允许选课\n具体时间请参看学校教务处公告..."
            print(info)

        # 已选择
        elif "你已经选择了课程" in r.text:
            logging.info("你已经选择了课程" + ' ' + param["kcId"])
            # info = "你已经选择了课程" + ' ' + param["kcId"]
            # print(info)
            return 1

        # 检查是否选课成功
        elif "选课成功" in r.text:
            logging.info("课程" + ' ' + param["kcId"] + ' ' + "选择成功")
            info = "课程" + ' ' + param["kcId"] + ' ' + "选择成功"
            print(info)
            # 成功，返回1
            return 1

    except requests.exceptions.Timeout:
        logging.info("网络有问题，正在重连...")
        login()
    except requests.exceptions.ConnectionError as e:
        logging.info(e)
        logging.info("有可能是教务处宕机了，也有可能没联网...\n请检查网络后，重启程序")
        time.sleep(1008611)

    # 若不成功, 返回0
    return 0

def update(lesson):
    global param
    param["kcId"] = lesson["kch"] + '_' + lesson["cxkxh"]
    return param

if __name__ == "__main__":
    # 登录
    while True:
        f = open("student.json", encoding='utf-8')
        global data
        data = json.load(f)
        print(u'学号: '+data['zjh']+'  ' + u'密码: ' + data['mm'])
        if login(True) == 1:
            break

    f = open("lessons.json", encoding='utf-8')
    lessons = json.load(f)
    lessons = lessons["lessons"]

    firsttime = True # 第一次的话，就选快点，后面有个间隔就好
    num = 0
    print(len(lessons))
    while num < len(lessons):
        for lesson in lessons:
            if xk(update(lesson), lesson) == 1:
                num = num + 1
                lessons.remove(lesson)
            if not firsttime:
                time.sleep(sleeptime)
        firsttime = False
        print('一次循环')

    logging.info("已完成所有工作...\n好好学习，天天向上！！！")

