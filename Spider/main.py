import argparse
import os
import ddddocr
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
import datetime
from datetime import timedelta

# 奥蓝系统登录网址
url_aolan = "http://smst.hhu.edu.cn/login.aspx"

# 传入用户名和密码参数
parser = argparse.ArgumentParser()
parser.add_argument('--username', type=str)
parser.add_argument('--password', type=str)
parser.add_argument('--email', type=str)
parser.add_argument('--email_password', type=str)
args = parser.parse_args()
username_list = args.username.split(',')
password_list = args.password.split(',')
email_list = args.email.split(',')
email_password = args.email_password

# 设置Google Chrome参数
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument("window-size=1295,843")
chrome_options.add_argument("--no-sandbox")


def send_email(message, to_addrs, cc_show=''):
    user = '2877307937@qq.com'
    # 邮件内容
    msg = MIMEText(message, 'plain', _charset="utf-8")
    # 邮件主题描述
    msg["Subject"] = "自动健康打卡"
    # 发件人显示，不起实际作用
    msg["from"] = 'Argena'
    # 收件人显示，不起实际作用
    msg["to"] = '同学'
    # 抄送人显示，不起实际作用
    msg["Cc"] = cc_show
    with SMTP_SSL(host="smtp.qq.com", port=465) as smtp:
        # 登录发邮件服务器
        smtp.login(user=user, password=email_password)
        # 实际发送、接收邮件配置
        smtp.sendmail(from_addr=user, to_addrs=to_addrs, msg=msg.as_string())


for i in range(len(username_list)):
    try:
        username = username_list[i]
        password = password_list[i]
        driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='/usr/bin/chromedriver')
        driver.get(url=url_aolan)
        driver.find_element(By.ID, 'userbh').send_keys(username)
        driver.find_element(By.ID, 'pas1s').send_keys(password)
        verif_code = driver.find_element(By.ID, 'Image1')

        verif_loc, verif_size = verif_code.location, verif_code.size
        x, y = verif_loc.values()
        h, w = verif_size.values()
        panel_height = driver.execute_script('return window.outerHeight - window.innerHeight')
        panel_width = driver.execute_script('return window.outerWidth - window.innerWidth')

        driver.save_screenshot('login.png')
        login_img = Image.open('login.png')
        verif_pic = login_img.crop((x, y, x + w, y + h))
        # draw = ImageDraw.Draw(login_img)
        # draw.rectangle([x,y,x+w,y+h], outline=(25,25,112))
        # login_img.save('new.png')
        verif_pic.save('yzm.png')

        ocr = ddddocr.DdddOcr()
        with open('yzm.png', 'rb') as f:
            img_bytes = f.read()
        res = ocr.classification(img_bytes)
        os.remove('login.png')
        os.remove('yzm.png')
        # print(res)
        driver.find_element(By.ID, 'vcode').send_keys(res)
        driver.find_element(By.NAME, 'save2').click()

        driver.get("http://smst.hhu.edu.cn/txxm/default.aspx?dfldm=02")

        driver.find_element(By.XPATH, '//*[@id="my_menu"]/div/a[1]').click()
        iframe = driver.find_element_by_name("r_3_3")
        driver.switch_to.frame(iframe)
        last_time = driver.find_element(By.NAME, 'tbrq').get_attribute('value').split('-')
        now_time = (datetime.datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d').split('-')
        last_time = list(map(int, last_time))
        now_time = list(map(int, now_time))

        if last_time != now_time:
            driver.find_element(By.NAME, 'databc').click()
            driver.quit()
            message = str((datetime.datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')) + '\n' + username +" 打卡成功，感谢您的支持！"
            print(message)
            send_email(message=message, to_addrs=email_list[i])
        else:
            driver.quit()
            print(username, '今日已打卡')
    except:
        username = username_list[i]
        message = str((datetime.datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')) + '\n' + username +" 打卡失败，请等待下一次打卡或手动打卡"
        print(message)
        send_email(message=message, to_addrs=email_list[i])
