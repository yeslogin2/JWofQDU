import urllib
import urllib.request
import http.cookiejar
from PIL import Image
import pytesseract
import io
import requests
import random
from bs4 import BeautifulSoup

my_headers={
    "Host":"jw.qdu.edu.cn",
    "Referer":"http://jw.qdu.edu.cn/academic/common/security/login.jsp",
    "User-Agent":"Mozilla/5.0 (Windows NT 5.1; rv:37.0) Gecko/20100101 Firefox/37.0"
}


hosturl = 'http://jw.qdu.edu.cn/academic/common/security/login.jsp'
posturl = 'http://jw.qdu.edu.cn/academic/j_acegi_security_check'
captchaurl = 'http://jw.qdu.edu.cn/academic/getCaptcha.do'

def cookie_dealer():
    cj = http.cookiejar.LWPCookieJar()  
    cookie_support = urllib.request.HTTPCookieProcessor(cj)  
    opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)  
    return opener

def login(opener, info):

    h = urllib.request.urlopen(hosturl)

    captcha_file = urllib.request.Request(captchaurl +'?'+ str(random.random()))
    captcha_response = opener.open(captcha_file)
    captcha_img = Image.open(io.BytesIO(captcha_response.read()))
    captcha = pytesseract.image_to_string(captcha_img)

    
    postdata = {
        'j_username': info[0],
        'j_password': info[1],
    }
    postdata.update({'j_captcha': captcha})
    postdata = urllib.parse.urlencode(postdata).encode('utf-8')

    request = urllib.request.Request(posturl, postdata, my_headers)

    response = opener.open(request)
    
    return response


def get_and_print_score(opener):
    scoreurl = "http://jw.qdu.edu.cn/academic/manager/score/studentOwnScore.do?groupId=&moduleId=2020"
    score_request = urllib.request.Request(scoreurl)
    score_response = opener.open(score_request)
    
    score_str = score_response.read().decode('utf-8')

    soup = BeautifulSoup(score_str, "html.parser")

    score_table = soup.find(class_='datalist')

    print("\n成绩出来了！\n")
    for tr in score_table.find_all('tr'):
        for th in tr.find_all('th'):
            print(str_trim(th.get_text()), end=' ')
        print('\n')
        for td in tr.find_all('td'):
            print(str_trim(td.get_text()), end=' ')
        print('\n')


def str_trim(text):
    result = ''
    for ch in text:
        if ch == ' ' or ch == '\n' or ch == '\t':
            pass
        else:
            result += ch
    return result

def get_input():
    username = input("请输入学号：")
    password = input("密码：")
    return (username, password)

if __name__ == "__main__":
    opener = cookie_dealer()
    urllib.request.install_opener(opener)
    info = get_input()
    print('正在登录中......')
    while True:
        response = login(opener, info)
        if response.geturl() == 'http://jw.qdu.edu.cn/academic/index_new.jsp':
            print("由西，登录成功了！")
            break
        else:
            print(response.info())
            error_cate = response.getheader('Content-Length')
            error_cate = str_trim(error_cate)
            if error_cate == '4296':
                print("啊呀，验证码好像识别错了呢，我再试试吧！")
            elif error_cate == '4284':
                print("小姐，你密码打错了！")
                info = get_input()
            else:
                print("大妈，学号不对哦！")
                info = get_input()
    get_and_print_score(opener)

