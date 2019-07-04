import random
import re

import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import subprocess as sp

def get_cookies():
    # url = 'https://www.baidu.com/'
    # headers = {'Upgrade-Insecure-Requests': '1',
    #            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    #            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    #            'Accept-Encoding': 'gzip, deflate, sdch, br',
    #            'Accept-Language': 'zh-CN,zh;q=0.8',
    #            }
    # s = requests.Session()
    # req = s.get(url=url, headers=headers)
    # print(s.cookies)
    #解析灌蜜
    # driver = webdriver.PhantomJS(executable_path='F:\\phantomjs-2.1.1-windows\\bin/phantomjs.exe')
    # driver.get('http://pythonscraping.com/pages/itsatrap.html')
    # print(type(driver))
    # aes = driver.find_elements_by_xpath('//a')
    # print(type(aes))
    # for aa in aes:
    #     print(type(aa))
    #     if not aa.is_displayed():
    #         print("连接 href"+aa.get_attribute('href')+"是一个蜜罐圈套")
    # ines = driver.find_elements_by_xpath("//input")
    # for inpu in ines:
    #     if not inpu.is_displayed():
    #         print("表单"+inpu.get_attribute("name")+"是一个蜜罐")

    #获取cookies
    # driver = webdriver.PhantomJS(executable_path='F:\\phantomjs-2.1.1-windows\\bin/phantomjs.exe')
    # driver.get("http://pythonscraping.com")
    # driver.implicitly_wait(1)
    # print(driver.get_cookies())

    url = 'https://www.xicidaili.com/nn/1'
    header = {'Cache-Control':'max-age=0','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
              'Accept-Encoding':'gzip, deflate, br','Accept-Language':'zh-CN,zh;q=0.9','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    req = requests.get(url=url,headers=header)
    html = req.text
    soup = BeautifulSoup(html,'lxml')
    ip_list = soup.find_all(id='ip_list')
    ips = BeautifulSoup(str(ip_list),'lxml')
    print(ips.table.name)
    tr_list = ips.find_all('tr')
    i=1
    ip_s = []
    for trs in tr_list[0:]:
        resoup = BeautifulSoup(str(trs),'lxml')
        strr = ''
        for td in resoup.find_all('td'):
            if i%10==2:
                strr=''
                strr = td.string
            elif i%10==3:
                strr=strr+"#"+td.string
            elif i%10==6:
                ip_s.append(strr+"#"+td.string)
            i = i + 1

    return ip_s

def initpattern():
    #匹配丢包数
    lose_time = re.compile(u"丢失 = (\d+)", re.IGNORECASE)
    #匹配平均时间
    waste_time = re.compile(u"平均 = (\d+)ms", re.IGNORECASE)
    return lose_time, waste_time


def check_ip(ip, lose_time, waste_time):
    # get_cookies()
    cmd = "ping -n 3 -w 3 %s"
    # 执行命令
    p = sp.Popen(cmd % ip, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
    # 获得返回结果并解码
    out = p.stdout.read().decode("gbk")
    # 丢包数
    lose_time = lose_time.findall(out)
    if len(lose_time) == 0:
        lose = 3
    else:
        lose = int(lose_time[0])
    if lose > 2:
        return 1000
        # 如果丢包数目小于等于2个,获取平均耗时的时间
    else:
        # 平均时间
        average = waste_time.findall(out)
        # 当匹配耗时时间信息失败,默认三次请求严重超时,返回平均好使1000ms
        if len(average) == 0:
            return 1000
        else:
            #
            average_time = int(average[0])
            # 返回平均耗时
            return average_time

if __name__=='__main__':
    proxys_list = get_cookies();
    lose_time, waste_time = initpattern()
    while True:
        # 从100个IP中随机选取一个IP作为代理进行访问
        proxy = random.choice(proxys_list)
        split_proxy = proxy.split('#')
        # 获取IP
        ip = split_proxy[0]
        # 检查ip
        average_time = check_ip(ip, lose_time, waste_time)
        if average_time > 200:
            # 去掉不能使用的IP
            proxys_list.remove(proxy)
            print("ip连接超时, 重新获取中!")
        if average_time < 200:
            break

        # 去掉已经使用的IP
    proxys_list.remove(proxy)
    proxy_dict = {split_proxy[2]: split_proxy[0] + ':' + split_proxy[1]}
    print("使用代理:", proxy_dict)
