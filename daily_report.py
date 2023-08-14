"""
cron: 0 22 * * *
new Env('校园网流量状态日报');
"""

import requests
import json
import os
import redis
from datetime import datetime, timedelta

def notify(title, content):
    print(content)
    print("\n")
    try:
        if not PUSH_PLUS_TOKEN:
            print("PUSHPLUS服务的token未设置!!\n取消推送")
            return
        url_push = 'http://www.pushplus.plus/send'
        data_push = {
            "token": PUSH_PLUS_TOKEN,
            "title": title,
            "content": content,
            'template': 'markdown',
            'topic': PUSH_PLUS_Group
        }

        body = json.dumps(data_push).encode(encoding='utf-8')
        headers_push = {'Content-Type': 'application/json'}
        requests.post(url=url_push, data=body, headers=headers_push).json()

    except Exception as e:
        print(e)


PUSH_PLUS_TOKEN = ''
PUSH_PLUS_Group = 'flow'
dic_db = {"12003068": 0}

if "PUSH_PLUS_TOKEN" in os.environ:
    if len(os.environ["PUSH_PLUS_TOKEN"]) > 1:
        PUSH_PLUS_TOKEN = os.environ["PUSH_PLUS_TOKEN"]
if "PUSH_PLUS_Group" in os.environ:
    if len(os.environ["PUSH_PLUS_Group"]) > 1:
        PUSH_PLUS_Group = os.environ["PUSH_PLUS_Group"]


url = "http://auth.dlut.edu.cn"
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept-Encoding': 'gzip, deflate'
}
s = requests.Session()
try:
    s.get(url, headers=headers)
    response = s.get('http://auth.dlut.edu.cn/eportal/InterFace.do?method=getOnlineUserInfo', headers=headers)
    userinfo_dict = json.loads(response.text)
    userId = userinfo_dict['userId']
    if userId is None:
        notify('未登录', "没有登陆账户")
    else:
        ballinfo = userinfo_dict['ballInfo']
        ballinfo_dict = json.loads(ballinfo)
        flowBalances = float(ballinfo_dict[1]['value'])/1000000000
        accountFee = float(ballinfo_dict[0]['value'])
        flowBalances_str = str(flowBalances)+'G'
        accountFee_str = str(accountFee)+'元'
        delta = 0.0
        if dic_db[userId] is not None:
            r = redis.Redis(host='192.168.31.76', port=6379, db=dic_db[userId], password='dlut1949')
            date = datetime.now()
            date_str = date.strftime('%Y%m%d')
            r.set(date_str, flowBalances)
            yesterday = date - timedelta(days=1)
            yesterday_str = yesterday.strftime('%Y%m%d')
            yesterday_flow = r.get(yesterday_str)
            if yesterday_flow is not None:
                delta = float(yesterday_flow) - flowBalances
        data = '**登录账号**：' + userId + '\n\n**balance**：' + accountFee_str + '\n\n**剩余流量**：' + flowBalances_str +\
               '\n\n**今日使用**：' + str(delta) + 'G'
        notify('校园网流量日报', data)

except requests.exceptions.ConnectionError as e:
    notify('未登录', "没有登陆账户")
