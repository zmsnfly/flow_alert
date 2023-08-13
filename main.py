import requests
import re
import json
import os


def pushplus_bot(title, content):
    try:
        print("\n")
        if not PUSH_PLUS_TOKEN:
            print("PUSHPLUS服务的token未设置!!\n取消推送")
            return
        print("PUSHPLUS服务启动")
        url = 'http://www.pushplus.plus/send'
        data = {
            "token": PUSH_PLUS_TOKEN,
            "title": title,
            "content": content,
            'template': 'markdown'
        }
        body = json.dumps(data).encode(encoding='utf-8')
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url=url, data=body, headers=headers).json()
        if response['code'] == 200:
            print('推送成功！')
        else:
            print('推送失败！')
    except Exception as e:
        print(e)


PUSH_PLUS_TOKEN = ''
if "PUSH_PLUS_TOKEN" in os.environ:
    if len(os.environ["PUSH_PLUS_TOKEN"]) > 1:
        PUSH_PLUS_TOKEN = os.environ["PUSH_PLUS_TOKEN"]

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
    accountFee = str(userinfo_dict['accountFee'])+'元'
    ballinfo = userinfo_dict['ballInfo']
    ballinfo_dict = json.loads(ballinfo)
    flowBalances = str(float(ballinfo_dict[1]['value'])/1000000000)+'G'
    data = '**登录账号**：' + userId + '\n\n**balance**：' + accountFee + '\n\n**剩余流量**：' + flowBalances
    pushplus_bot('校园网流量余额预警', data)

except requests.exceptions.ConnectionError as e:
    pushplus_bot('未登录', "没有登陆账户")
