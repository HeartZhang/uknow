import datetime
import requests
import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import random
import time
import sqlite3
import re
import sys
import js2py
import datetime
import logging



def cal_quality(add_time, view_number, like_number):
    date = datetime.datetime.strptime(add_time, '%Y-%m-%d')
    today = datetime.datetime.now()
    days = (today - date).days
    print(days)
    mean_view_per_day = int(view_number) / days
    like_view_per_day = int(like_number) / days

    quality = round((like_view_per_day / mean_view_per_day) * 1000, 3)

    print(mean_view_per_day, like_view_per_day, quality)
    return quality


def setHeader():
    randomIP = str(random.randint(0, 255)) + '.' + str(random.randint(0, 255)) + '.' + str(
        random.randint(0, 255)) + '.' + str(random.randint(0, 255))
    headers = {
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.96 Chrome/58.0.3029.96 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
        'Accept-Encoding': 'gzip, deflate, sdch',
        'X-Forwarded-For': randomIP,
    }
    return headers

def get_content(url, stream=False):
    try:
        s = requests.Session()
        retries = Retry(total=5, backoff_factor=10, status_forcelist=[500, 502, 503, 504])
        s.mount('http://', HTTPAdapter(max_retries=retries))
        response = s.get(url, headers=setHeader(), stream=stream)
        response.encoding = response.apparent_encoding
        if response.status_code == 200:
            return response
    except Exception as e:
        print("请求失败{0},reason={1}".format(url, e))
        return None

# URL解密
def decrypt_url(p1, p2):
    jsc, _ = js2py.run_file('md5.js')
    return jsc.encrypt(p1, p2)

# 解析视频详情
def get_video_info(url):
    try:
        start = time.clock()

        content = get_content(url).content
        if not content:
            return None, None, None

        utext = content.decode('utf-8')
        soup2 = BeautifulSoup(utext, 'lxml')
        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        # 判断视频信息有效性
        video_valid= soup2.find('div', attrs={'id': 'container'})
        if video_valid and '视频不存在'in video_valid.get_text():
            elapsed = (time.clock() - start)
            print("get_video_info not found Time used:{}s".format(round(elapsed, 2)))
            return None, None, None

        # 提取添加时间
        video_info = soup2.find('div', attrs={'id': 'videodetails-content'})

        add_time = video_info.select(".title")[1].get_text().strip()

        # 提取URL加密串
        pattern = re.compile(r'strencode\((.*?)\)', re.MULTILINE | re.DOTALL)
        script = soup2.find("script", text=pattern)
        entrypt = pattern.search(script.text).group(1)
        encrypt_1 = entrypt.split(',')[0].strip('"')
        encrypt_2 = entrypt.split(',')[1].strip('"')
        encrypt_3 = entrypt.split(',')[2].strip('"')

        # 解密获取实际URL以及类型
        video_source = decrypt_url(encrypt_1, encrypt_2)
        pattern = re.findall('\'(.*?)\'', video_source)
        video_source_url = pattern[0]
        video_source_type = pattern[1].split('/')[1]

        # print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        elapsed = (time.clock() - start)
        print("get_video_info Time used:{}s".format(round(elapsed, 2)))
        return add_time, video_source_url, video_source_type
    except Exception as e:
        print("获取视频信息失败:", e)
    return None, None, None

#cal_quality('2015-07-14',6708,530)


if __name__ == '__main__':
    print(get_video_info('http://91porn.com/view_video.php?viewkey=ff708ac2e4c28220275a&page=422&viewtype=basic&category=mf'))