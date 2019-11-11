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
from math import sqrt

logging.disable(logging.WARNING)

# 随机取httpheader
uas = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.96 Chrome/58.0.3029.96 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:17.0; Baiduspider-ads) Gecko/17.0 Firefox/17.0",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9b4) Gecko/2008030317 Firefox/3.0b4",
    "Mozilla/5.0 (Windows; U; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727; BIDUBrowser 7.6)",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64; Trident/7.0; Touch; LCJB; rv:11.0) like Gecko",
]
UKNOW_BASE_URL = 'http://91porn.com/v.php'

INIT_RUN = False


# 初始化sqlite3 数据库
def init_db():
    connection = sqlite3.connect("uknow.db")
    connection.execute("DROP TABLE IF EXISTS uknow_video")
    connection.execute(
        "CREATE TABLE IF NOT EXISTS uknow_video("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "video_view_key TEXT UNIQUE,"
        "video_url TEXT UNIQUE,"
        "video_name TEXT,"
        "video_source TEXT,"
        "video_type TEXT,"
        "duration TEXT,"
        "add_time TEXT,"
        "video_author TEXT,"
        "view_number INTEGER,"
        "like_number INTEGER,"
        "comment_number INTEGER,"
        "quality FLOAT,"
        "flag INTEGER DEFAULT 0,"
        "thumbs_up INTEGER DEFAULT 0,"
        "top INTEGER DEFAULT 0,"
        "has_local_cache INTEGER DEFAULT 0,"
        "local_cache_start INTEGER,"
        "local_cache_exp INTEGER,"
        "local_cache_source INTEGER)"
    )


# 随机生成http header
def setHeader():
    randomIP = str(random.randint(0, 255)) + '.' + str(random.randint(0, 255)) + '.' + str(
        random.randint(0, 255)) + '.' + str(random.randint(0, 255))
    headers = {
        'User-Agent': random.choice(uas),
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


# 获取91总页数
def get_page_number():
    html = get_content(UKNOW_BASE_URL).content
    if html:
        bs = BeautifulSoup(html, "html.parser")
        return bs.select(".page_number")[-1].find_all_previous("a")[1].text


# 抓取页面

def list_url(from_page=1):
    pages = get_page_number()
    page_count = int(pages)
    print("总计{0}个页面".format(page_count))
    if int(page_count) > 0:
        current_page = from_page
        while current_page <= page_count:
            size = random.randint(10, 50)
            print("本次任务抓取{0}个页面".format(size))
            for page in range(current_page, current_page + size):
                start = time.clock()

                fv_url = UKNOW_BASE_URL + '?category=mf&viewtype=basic&page=' + str(page)
                print("开始抓取第{0}页...".format(page))
                response = get_content(fv_url)
                if response and response.content:
                    get_url_content(response.content)
                else:
                    print("抓取页面失败")
                elapsed = (time.clock() - start)
                print("抓取第{0}页完成 Time used:{1}s".format(page, round(elapsed, 2)))
                print("总体进度 {0}% ".format(round((page / page_count) * 100, 2)))
            current_page = size + current_page
            # downLoadBatch()
        # downLoadBatch(-1)


# 质量计算--作废
def cal_quality(add_time, view_number, like_number):
    date = datetime.datetime.strptime(add_time, '%Y-%m-%d')
    today = datetime.datetime.now()
    days = (today - date).days + 1

    mean_view_per_day = int(view_number) / days
    like_view_per_day = int(like_number) / days

    quality = round((like_view_per_day / mean_view_per_day) * 1000, 3)
    return quality


# 新的质量信心得分算法
def cal_confidence(view_number, like_number):
    n = int(view_number)
    l = int(like_number)
    if n == 0 or l == 0:
        return 0

    z = 1.6  # 1.0 = 85%, 1.6 = 95%
    phat = float(like_number) / n
    return round(
        (sqrt(phat + z * z / (2 * n) - z * ((phat * (1 - phat) + z * z / (4 * n)) / n)) / (1 + z * z / n)) * 10, 4)


def get_url_content(html):
    soup = BeautifulSoup(html, "html.parser")
    video_content_list = soup.find('div', attrs={'id': 'videobox'})
    i = 0
    connection = sqlite3.connect("uknow.db")
    for videoLi in video_content_list.find_all('div', attrs={'class': 'listchannel'}):
        video_name = videoLi.find('img', attrs={'width': '120'}).get('title').replace("'", "")
        video_url = videoLi.find('a', attrs={'target': 'blank'}).get('href')
        video_view_key= get_view_key(video_url)
        duration = videoLi.select(".info")[0].next_sibling.strip()
        try:
            video_author = videoLi.select(".info")[2].next_sibling.strip().replace("'", "")
        except AttributeError:
            video_author = "None"
        view_number = videoLi.select(".info")[3].next_sibling.strip()
        like_number = videoLi.select(".info")[4].next_sibling.strip()
        comment_number = videoLi.select(".info")[5].next_sibling.strip()
        i += 1
        if INIT_RUN:
            add_time, video_source, video_type = get_video_info(video_url)
            # 视频不存在或者解析信息失败,跳过
            if not video_source:
                continue

            quality = cal_confidence(view_number, like_number)

            connection.execute(
                "INSERT or REPLACE INTO uknow_video(video_view_key, video_url,video_name ,video_source, video_type ,duration ,"
                "add_time ,video_author ,view_number ,like_number ,comment_number, quality) values('"
                + video_view_key + "','" + video_url + "','" + video_name + "','" + video_source + "','" + video_type + "','" + duration + "','"
                + add_time + "','" + video_author + "'," + view_number + "," + like_number + "," + comment_number + "," + str(
                    quality) + ")")
        else:
            quality = cal_confidence(view_number, like_number)

            connection.execute(
                "INSERT or REPLACE INTO uknow_video(video_view_key, video_url,video_name ,duration ,"
                "video_author ,view_number ,like_number ,comment_number, quality) values('"
                + video_view_key + "','"+ video_url + "','" + video_name + "','" + duration + "','"
                + video_author + "'," + view_number + "," + like_number + "," + comment_number + "," + str(
                    quality) + ")")

    connection.commit()
    connection.close()


# 解析视频详情
def get_video_info(url):
    try:
        start = time.clock()

        response = get_content(url)
        if not response:
            return None, None, None
        if not response.content:
            return None, None, None

        utext = response.content.decode('utf-8')
        soup2 = BeautifulSoup(utext, 'lxml')
        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        # 判断视频信息有效性
        video_valid = soup2.find('div', attrs={'id': 'container'})
        if video_valid and '视频不存在' in video_valid.get_text():
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
        video_source_type = pattern[1]

        # print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        elapsed = (time.clock() - start)
        print("get_video_info Time used:{}s".format(round(elapsed, 2)))
        return add_time, video_source_url, video_source_type
    except Exception as e:
        print("获取视频信息失败:", e)
    return None, None, None


# URL解密
def decrypt_url(p1, p2):
    jsc, _ = js2py.run_file('md5.js')
    return jsc.encrypt(p1, p2)


# 提取view_key
def get_view_key(url):
    if not url:
        return None
    pattern = re.compile(r'viewkey=(.*?)\&', re.MULTILINE | re.DOTALL)
    view_key = pattern.search(url).group(1)
    return view_key


def downLoad(link):
    connection = sqlite3.connect("uknow.db")
    sql = "UPDATE url set flag={0} WHERE videoUrl='{1}'"
    try:
        print("开始下载地址为{0}".format(link))
        content = get_content(link).content
        utext = content.decode('utf-8')
        soup2 = BeautifulSoup(utext, 'lxml')
        vurl = soup2.find('video').find('source').get('src')
        videoTitle = soup2.find(id='viewvideo-title').get_text().strip()
        fileType = re.findall('\.(.{3}?)\?', vurl)  # .mp4\.avi
        fileName = videoTitle + '.' + fileType[0]
        filePath = os.path.join(target_folder, fileName)
        if (not os.path.isfile(filePath)):
            res = get_content(vurl, stream=True)
            if (res):
                file = open(filePath, 'wb')
                for chunk in res.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
        else:
            print("文件已存在 本次不下载")
        sql = sql.format(1, link)
        print("下载完成")
    except Exception as e:
        print("下载失败{0}", e)
        # 更新为下载失败
        sql = sql.format(-1, link)
    connection.execute(sql)
    connection.commit()
    connection.close()


# 递归下载
def downLoadBatch(flag=0):
    connection = sqlite3.connect("uknow.db")
    cursor = connection.execute("SELECT count(1) FROM url WHERE flag={0}".format(flag))
    urlList = []
    if (cursor):
        for i in cursor:
            totalCount = i[0]
        print("本次还有{0}条未下载".format(totalCount))
        if (totalCount > 0):
            cursor = connection.execute("SELECT videoUrl FROM url WHERE flag={0}".format(flag))
            for str in cursor:
                urlList.append(str[0])
            connection.close()
        if len(urlList) > 0:
            for str in urlList:
                downLoad(str)
            downLoadBatch(flag)


if __name__ == '__main__':
    import os

    current_folder = os.getcwd()
    target_folder = os.path.join(current_folder, "temp")
    if not os.path.isdir(target_folder):
        os.mkdir(target_folder)
    init_db()
    list_url(from_page=0)
