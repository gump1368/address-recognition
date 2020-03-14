#! -*- coding: utf-8 -*-
"""
@Author: Gump
@Create Time: 2020/2/26
@Info: 地址识别
"""
import os
import copy
import time
import pandas as pd
import collections

# from segment import Segment
# from address_retrieval import InvertedIndex
from segment import Segment
from address_retrieval import InvertedIndex

SOURCE_PATH = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(SOURCE_PATH, 'data/')


class Address(object):
    def __init__(self, path):
        self.path = path
        self.address = pd.read_csv(path)

    def add(self, data: pd.DataFrame, saved_path=None):
        """添加数据"""
        if not isinstance(data, pd.DataFrame):
            print('type of added data must be DataFrame!')
            return False
        self.address = pd.merge(self.address, data, how='outer')
        if saved_path:
            self.address.to_csv(saved_path, index=False, encoding='utf_8_sig')

    def select_index(self, index: list):
        """根据索引筛选数据"""
        return self.address.iloc[index]

    def select_column(self, column, value: list):
        """根据列的值筛选数据"""
        return self.address[self.address[column].isin(value)]


class AddressIdentify(Address):
    def __init__(self, path):
        super(AddressIdentify, self).__init__(path)
        self.rank2num = {'province': 1, 'city': 2, 'county': 3, 'town': 4, 'village': 5}
        self.num2rank = {value: key for key, value in self.rank2num.items()}
        self.retrieval_model = {}
        self.segment_model = {}
        self.load_model()

    def load_model(self):
        for key in self.rank2num.keys():
            data = self.address[key]
            self.retrieval_model[key] = InvertedIndex(data=data,
                                                      path=os.path.join(DATA_PATH, 'retrieval_{}.json').format(key))
            self.segment_model[key] = Segment(words_path=os.path.join(DATA_PATH, '{}_tree.json').format(key))

    def address_match(self, s):
        """地址匹配"""
        # 区域匹配
        time3 = time.time()
        address_segment = []
        for key in self.rank2num.keys():
            s = copy.copy(s)
            segment_model = self.segment_model[key]
            segment_result = list(segment_model.segment(s, seg_len=10))
            if not segment_result:
                continue
            last_item = {'words': '', 'offset': (-1, -1)}
            segment_new = []
            for item in segment_result:
                item['rank'] = key
                # 去除重复词
                if last_item['words'] == item['words'] and (item['offset'][0] - last_item['offset'][1]) <= 3:
                    last_item = item
                    continue

                segment_new.append(item)
                last_item = item
            address_segment.append(segment_new)

        if not address_segment:
            return {}
        print('address segment: ', time.time()-time3)

        # 地址排列
        time4 = time.time()
        ranging = []
        for address in address_segment:
            ranging = self.address_rank(address, ranging)

        # # 过滤长度为1但级别不是小区级的
        # def fun(l):
        #     if len(l) == 1 and l[0]['rank'] != 5:
        #         return False
        #     return True
        # ranging = list(filter(fun, ranging))

        # 按长度进行排列
        ranging_by_length = collections.defaultdict(list)
        for item in ranging:
            length = len(item)
            ranging_by_length[length].append(item)
        ranging_by_length = collections.OrderedDict(sorted(ranging_by_length.items(), key=lambda x: x[0], reverse=True))
        print('address ranking:', time.time()-time4)

        # 地址校验
        time5 = time.time()
        words_indexes = {}
        for item in address_segment:
            words = [elem['words'] for elem in item]
            rank = item[0]['rank']
            indexes = self.get_index(words, rank)
            words_indexes[rank] = indexes
        print('get indexes cost:', time.time()-time5)

        checking_result = []
        for _, value in ranging_by_length.items():
            for address in value:
                result = []
                for rank_address in address:
                    rank = rank_address['rank']
                    word = rank_address['words']
                    offset = rank_address['offset']
                    match_res = words_indexes[rank].get(word, [])
                    if not match_res:
                        result = []
                        break
                    result = self.address_checking(result, match_res, rank, offset)
                    if not result:
                        break
                checking_result.extend(result)
            if checking_result:
                break
        # 去除offset为-1的值
        checking_result = list(filter(lambda x: x['offset'] != (-1, -1), checking_result))
        if not checking_result:
            return {}
        # 筛选出rank score最大值
        max_rank_score = sorted(checking_result, key=lambda x: x['rank_score'], reverse=True)[0]['rank_score']
        checking_result = list(filter(lambda x: x['rank_score'] == max_rank_score, checking_result))
        # 筛选出match score最大值
        max_match_score = sorted(checking_result, key=lambda x: float(x['match_score']), reverse=True)[0]['match_score']
        checking_result = list(filter(lambda x: x['match_score'] == max_match_score, checking_result))
        # 再按rank排序
        checking_result = sorted(checking_result, key=lambda x: x['rank'], reverse=True)
        print('address checking:', time.time()-time5)

        # 地址补充输出
        for res in checking_result:
            intersection = res['index']
            high_rank = res['rank']
            address = self.address_complete(intersection[0], high_rank)
            address['last'] = s[res['offset'][1]:]
            return address

        return {}

    def get_index(self, words: list, rank: int):
        """获取词的index"""
        retrieval_model = self.retrieval_model[self.num2rank[rank]]
        indexes = {}
        for word in words:
            retrieval_result = retrieval_model.run(word)
            indexes[word] = retrieval_result
        return indexes

    def address_rank(self, address_segment, address_ranging):
        """地址排列"""
        for item in address_segment:
            item['rank'] = self.rank2num[item['rank']]
            if not address_ranging:
                address_ranging.append([item])
                continue
            for item1 in address_ranging:
                last_ranging = item1[-1]
                if 0 <= (item['offset'][0] - last_ranging['offset'][1]) <= 5 and last_ranging['rank'] < item['rank']:
                    address = copy.copy(item1)
                    address.append(item)
                    address_ranging.append(address)
                elif [item] != address_ranging[-1]:
                    address_ranging.append([item])
        return address_ranging

    @classmethod
    def address_checking(cls, address_result: list, match_address: list, rank, offset):
        """地址校验"""
        if not address_result:
            for item in match_address:
                add = {'index': item['indexes'], 'match_score': 1, 'rank_score': 1, 'rank': rank}
                if rank <= 3:
                    add['offset'] = offset
                else:
                    add['offset'] = (-1, -1)
                address_result.append(add)
            return address_result

        address_res = []
        for address in address_result:
            index = address['index']
            match_score = address['match_score']
            rank_score = address['rank_score']
            last_rank = address['rank']
            for item in match_address:
                match_index = item['indexes']
                section = list(set(index).intersection(set(match_index)))
                if not section:
                    continue

                rank_score_new = rank_score + 1 - (rank-last_rank-1)/5
                match_score = match_score * item['score']
                add = {'index': section, 'match_score': match_score, 'rank_score': rank_score_new, 'rank': rank}
                if rank <= 3:
                    add['offset'] = offset
                else:
                    add['offset'] = address['offset']
                address_res.append(add)

        return address_res

    def address_complete(self, address_id, rank):
        """地址补全"""
        line = self.address.iloc[int(address_id)]
        output = {'province': '', 'city': '', 'county': '', 'town': '', 'village': ''}
        keys = list(output.keys())[:rank]
        for key in keys:
            output[key] = line[key]
        return output

    def address_correct(self, data):
        """地址纠错"""
        pass


if __name__ == '__main__':
    import time
    file_path = os.path.join(DATA_PATH, 'address.csv')
    test_l = ['福建省南安市石井镇后店北片88号祝义汽车投资有限公司']
    address_ident = AddressIdentify(file_path)
    t1 = time.time()
    for q in test_l:
        print('test address:', q)
        test_result = address_ident.address_match(s=q)
        print('address identify result:', test_result)
    # # print(address_ident.address)
    print('time cost:', time.time()-t1)
