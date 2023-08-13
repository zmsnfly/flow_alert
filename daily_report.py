"""
cron: 0 22 * * *
new Env('校园网流量预警');
"""

import requests
import json
import os


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


PUSH_PLUS_TOKEN = '62663a910c9d4dd2a08ef2d3f9552615'
PUSH_PLUS_Group = 'flow'

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
        accountFee = str(userinfo_dict['accountFee'])+'元'
        ballinfo = userinfo_dict['ballInfo']
        ballinfo_dict = json.loads(ballinfo)
        flowBalances = str(float(ballinfo_dict[1]['value'])/1000000000)+'G'
        data = '**登录账号**：' + userId + '\n\n**balance**：' + accountFee + '\n\n**剩余流量**：' + flowBalances
        notify('校园网流量日报', data)

except requests.exceptions.ConnectionError as e:
    notify('未登录', "没有登陆账户")
