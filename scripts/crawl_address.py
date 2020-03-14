#!/usr/bin/python3
# -*- coding: utf-8 -*-
# author=He

"""
通过国家统计局数据
获取中国所有城市列表
"""
import pandas as pd
import sys
import os
import re
import requests
import random
from urllib import request
from bs4 import BeautifulSoup
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
source_url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/'
user_agent_list = [
    'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1464.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36',
    'Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:17.0) Gecko/20100101 Firefox/17.0.6',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36',
    'Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36'
]


class GetHttp(object):
    def __init__(self, url, charset='gb2312'):
        self._response = ''
        headers = {'User-Agent': random.choice(user_agent_list)}
        proxy = {'https:': '121.237.148.173:3000'}
        try:
            self._response = requests.get(url=url, headers=headers, proxies=proxy)
            self._response.encoding = charset
        except Exception as e:
            print(e)

    @property
    def text(self):
        return self._response.text


def get_province(url):
    # 获取全国省份和直辖市
    res = {'province': [], 'code1': []}
    html = GetHttp(url).text
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        for i in soup.find_all(attrs={'class': 'provincetr'}):
            for a in i.find_all('a'):
                res['province'].append(a.text)
                res['code1'].append(re.sub("\D", "", a.get('href')))
    return res


def get_city(res):
    # 获取省下级市
    res_new = {'province': [], 'code1': [], 'city': [], 'code2': []}
    for i in tqdm(range(len(res['province'])), total=len(res['province'])):
        province = res['province'][i]
        code1 = res['code1'][i]
        html = GetHttp(source_url+str(code1)+'.html').text
        if not html:
            continue
        soup = BeautifulSoup(html, 'html.parser')
        for item in soup.find_all(attrs={'class': 'citytr'}):
            res_new['province'].append(province)
            res_new['code1'].append(code1)
            res_new['code2'].append(item.find_all('td')[0].text)
            res_new['city'].append(item.find_all('td')[1].text)
    return res_new


def get_county(res):
    # 获取市下级县
    res_new = {'province': [], 'code1': [], 'city': [], 'code2': [], 'county': [], 'code3': []}
    for i in tqdm(range(len(res['city'])), total=len(res['city'])):
        province, code1, city, code2 = res['province'][i], res['code1'][i], res['city'][i], res['code2'][i]
        html = GetHttp(source_url+str(code1)+'/'+str(code2[:4])+'.html').text
        if not html:
            continue
        soup = BeautifulSoup(html, 'html.parser')
        for item in soup.find_all(attrs={'class': 'countytr'}):
            res_new['province'].append(province)
            res_new['code1'].append(code1)
            res_new['city'].append(city)
            res_new['code2'].append(code2)
            res_new['code3'].append(item.find_all('td')[0].text)
            res_new['county'].append(item.find_all('td')[1].text)
    return res_new


def get_town(res):
    # 县下级镇
    res_town = {'province': [], 'code1': [], 'city': [], 'code2': [], 'county': [], 'code3': [],
                'town': [], 'code4': []}
    com = zip(res['province'], res['code1'], res['city'], res['code2'], res['county'], res['code3'])
    for line in tqdm(com, total=len(res['code1'])):
        province, code1, city, code2, county, code3 = line
        html = GetHttp(source_url + str(code1) + '/' + str(code2)[2:4] + '/' + str(code3)[:6] + '.html').text
        if not html:
            continue
        soup = BeautifulSoup(html, 'html.parser')
        for item in soup.find_all(attrs={'class': 'towntr'}):
            res_town['province'].append(province)
            res_town['code1'].append(code1)
            res_town['city'].append(city)
            res_town['code2'].append(code2)
            res_town['county'].append(county)
            res_town['code3'].append(code3)
            res_town['code4'].append(item.find_all('td')[0].text)
            res_town['town'].append(item.find_all('td')[1].text)
    return res_town


def get_village(res):
    # 镇下级村
    res_new = {'province': [], 'code1': [], 'city': [], 'code2': [], 'county': [], 'code3': [],
               'town': [], 'code4': [], 'village': [], 'code5': []}
    com = zip(res['province'], res['code1'], res['city'], res['code2'], res['county'], res['code3'],
              res['town'], res['code4'])
    for line in tqdm(com, total=len(res['code1'])):
        # province, code1, city, code2, county, code3, town, code4 = line
        province, code1, city, code2, county, code3,  town, code4 = line
        # html = GetHttp(source_url+str(code1)+'/'+str(code2)+'/'+str(code3)+'/'+str(code4)+'.html').text
        html = GetHttp(source_url+str(code1)+'/'+str(code2)[2:4]+'/' + str(code3)[4:6] + '/' + str(code4)[:9]+'.html')\
            .text
        if not html:
            continue
        soup = BeautifulSoup(html, 'html.parser')
        for item in soup.find_all(attrs={'class': 'villagetr'}):
            res_new['province'].append(province)
            res_new['code1'].append(code1)
            res_new['city'].append(city)
            res_new['code2'].append(code2)
            res_new['code3'].append(code3)
            res_new['county'].append(county)
            res_new['town'].append(town)
            res_new['code4'].append(code4)
            res_new['village'].append(item.find_all('td')[-1].text)
            res_new['code5'].append(item.find_all('td')[0].text)
    return res_new


if __name__ == '__main__':
    import re
    chinese_regex = re.compile(u'[^\u4e00-\u9fa5]')
    # province = get_province(source_url)
    # res_province = {'province': ['广东省'], 'code1': ['44']}
    # city = get_city(res_province)
    res_city = {'province': ['河北省'], 'code1': ['13'], 'city': ['石家庄市'], 'code2': ['1301']}
    res_county = get_county(res_city)
    # res_county = {'province': ['山西省'], 'code1': ['14'], 'city': ['芜湖市'], 'code2': ['1410'], 'county': ['霍州市'],
    #               'code3': ['141082']}
    # res_town = get_town(res_county)
    # res_village = get_village(res_town)
    # frame = {'province': [], 'city': [], 'county': [], 'town': [], 'village': []}
    # for i in range(len(res_village['province'])):
    #     town = res_village['town'][i]
    #     village = res_village['village'][i]
    #     if re.search(chinese_regex, str(town)) or re.search(chinese_regex, str(village)):
    #         print(town, village)
    #         continue
    #     frame['province'].append(res_village['province'][i])
    #     frame['city'].append(res_village['city'][i])
    #     frame['county'].append(res_village['county'][i])
    #     frame['town'].append(res_village['town'][i])
    #     frame['village'].append(res_village['village'][i])
    # df = pd.DataFrame(frame)
    #
    # df.to_csv('石家庄市.csv', index=False, encoding='utf_8_sig')
