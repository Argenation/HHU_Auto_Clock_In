import argparse
import os
import ddddocr
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

url_aolan = "http://smst.hhu.edu.cn/login.aspx"
url_pic = "http://smst.hhu.edu.cn/Vcode.ASPX"

parser = argparse.ArgumentParser()
parser.add_argument('--username', type=str)
parser.add_argument('--password', type=str)

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument("window-size=1295,843")
chrome_options.add_argument("--no-sandbox")
args = parser.parse_args()
username_list = args.username.split(',')
password_list = args.password.split(',')

for i in range(len(username_list)):
    username = username_list[i]
    password = password_list[i]
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='../chrome/chromedriver')
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
    driver.find_element(By.NAME,'save2').click()

    driver.get("http://smst.hhu.edu.cn/txxm/default.aspx?dfldm=02")

    driver.find_element(By.XPATH, '//*[@id="my_menu"]/div/a[1]').click()
    iframe = driver.find_element_by_name("r_3_3")
    driver.switch_to.frame(iframe)

    driver.find_element(By.NAME, 'databc').click()
    driver.quit()
