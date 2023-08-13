"""
cron: 0 0-23/3 * * *
new Env('流量超出自动退出账号');
"""

import requests
import json
import os
import smtplib
import ssl
from email.message import EmailMessage


def notify(title, content):
    print(content)
    print("\n")
    contacts = EMAILS.split("&")
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.163.com", 465, context=context) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            for contact in contacts:
                subject = title
                body = content
                msg = EmailMessage()
                msg['subject'] = subject
                msg['From'] = EMAIL_ADDRESS
                msg['To'] = contact
                msg.set_content(body)
                smtp.send_message(msg)
    except Exception as e:
        print(e)


THRESHOLD = 10
EMAIL_ADDRESS = "@163.com"
EMAIL_PASSWORD = ""
EMAILS = os.getenv("EMAIL")
if "EMAIL_ADDRESS" in os.environ:
    if len(os.environ["EMAIL_ADDRESS"]) > 1:
        EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]

if "EMAIL_PASSWORD" in os.environ:
    if len(os.environ["EMAIL_PASSWORD"]) > 1:
        EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]


url = "http://auth.dlut.edu.cn"
url_logout = "http://auth.dlut.edu.cn/eportal/InterFace.do?method=logout"
url_info = "http://auth.dlut.edu.cn/eportal/InterFace.do?method=getOnlineUserInfo"
if "THRESHOLD" in os.environ:
    if len(os.environ["THRESHOLD"]) > 1:
        THRESHOLD = os.environ["THRESHOLD"]
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept-Encoding': 'gzip, deflate'
}
s = requests.Session()
try:
    s.get(url, headers=headers)
    response = s.get(url_info, headers=headers)
    userinfo_dict = json.loads(response.text)
    userId = userinfo_dict['userId']
    if userId is None:
        notify('未登录', "没有登陆账户")
    else:
        ballinfo = userinfo_dict['ballInfo']
        ballinfo_dict = json.loads(ballinfo)
        flowBalances = float(ballinfo_dict[1]['value'])/1000000000
        if flowBalances < float(THRESHOLD):
            notify("流量超出通知", "账号 " + userId + " 剩余流量：" + str(flowBalances) + "G，已退出账号")
            response = s.get(url_logout, headers=headers)
            if response.status_code == 200:
                print("账号已退出")
            else:
                print("账号退出失败")
        else:
            print("账号 " + userId + "流量还多，剩余流量：" + str(flowBalances) + "G")

except requests.exceptions.ConnectionError as e:
    notify('未登录', "没有登陆账户")
