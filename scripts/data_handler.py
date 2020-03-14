#! -*- coding: utf-8 -*-
import re
import json
import pandas as pd


def merge_frame(df1, df2, method='outer', save_path=None):
    """合并df2到df1"""
    df_new = pd.merge(df1, df2, method)
    if save_path:
        df_new.to_csv(save_path, encoding='utf_8_sig', index=False)


address = ['东营市', '临沂市', '南阳市', '商丘市', '平顶山市', '日照市','洛阳市', '石家庄市', '芜湖市', '西安市', '银川市',
           '霍州市', '青岛市']
data = pd.DataFrame()
for add in address:
    df = pd.read_csv(add+'.csv')
    data = pd.concat([data, df])
# data.to_csv('concat.csv', index=False, encoding='utf_8_sig')

#
df1 = pd.read_csv('../data/address_2.3.csv')
# df2 = pd.read_csv('霍州市.csv')
merge_frame(df1, data, save_path='../data/address_2.4.csv')
