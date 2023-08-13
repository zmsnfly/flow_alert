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
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.163.com", 465, context=context) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            for contact in contacts:
                subject = title
                body = f"{contact}邮件主体内容"
                msg = EmailMessage()
                msg['subject'] = subject  # 邮件标题
                msg['From'] = EMAIL_ADDRESS  # 邮件发件人
                msg['To'] = contact  # 邮件的收件人
                msg.set_content(body)  # 使用set_content()方法设置邮件的主体内容
                # 使用send_message方法发送邮件信息
                smtp.send_message(msg)


    except Exception as e:
        print(e)



THRESHOLD = 10
EMAIL_ADDRESS = "diskstation422@163.com"
EMAIL_PASSWORD = "ACQPCUYQVBFJATWH"
contacts = os.getenv("EMAIL")


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
            response = s.get(url_logout, headers=headers)
            if response.status_code == 200:
                notify("流量超出，已退出账号")
            else:
                notify("流量超出，但退出失败")
except requests.exceptions.ConnectionError as e:
    notify('未登录', "没有登陆账户")