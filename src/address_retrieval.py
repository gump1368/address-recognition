#! -*- coding: utf-8 -*-
"""
Author: Gump
Create Time: 2020/1/27
Info: 文本检索
"""
import re
import json
import collections
import Levenshtein

chinese_regex = 'u[^\u4e00-\u9fa5]'
REGEX = re.compile('(自治区|工业园|开发区|街道|社区|东区|地区|园区|省|市|区|县|镇|乡|村|庄|城)$|'
                   '[一二三四五六七八九十]路')
BLACK_LIST = ['经济', '华林', '公司', '物流', '路南', '路东', '环路', '家园', '西外', '环路', '南段', '中心', '工业',
              '路西', '科技', '农业', '大学', '路北', '中路', '广场', '二路', '国际', '集团', '大道', '市东', '南路',
              '南岸']
WHITE_LIST = ['歙', '淇', '荣', '息', '范', '吉', '攸', '米', '沙', '和', '曹', '易', '莘', '理', '滦', '澧', '威',
              '泸', '成', '浚', '富', '湘', '大', '徽', '赵', '横', '环', '铁', '嵩', '彬', '陇', '城', '义',
              '盂', '眉', '冠', '城', '绿', '岷', '寿', '唐', '勉', '单', '索', '户', '忠', '青', '揭', '磁', '河',
              '朗', '乾', '矿', '莒', '隰', '沧', '阳', '任', '蒲', '杞', '房', '沁', '盘', '藤', '兴', '临', '黟',
              '漳', '桥', '康', '洋', '景', '茂', '珙', '代', '赣', '金', '古', '新', '礼', '夏', '凤', '渠', '温',
              '乃', '芒', '蔚', '佳', '沛', '郏', '萧', '滑', '宾', '云', '郫', '魏', '丰', '文', '道', '绛',
              '宁', '颍', '郊', '梁', '江', '泾', '祁', '蠡', '卫', '泗', '费', '睢', '岚', '叶', '雄', '随']


class DataProcess(object):
    def __init__(self, data):
        self.documents = collections.defaultdict(list)
        self.vocabulary = []
        if data is not None:
            self.__build_vocab(data)

    def __build_vocab(self, data: list):
        """构建词表"""
        vocabulary = []
        for index, doc in enumerate(data):
            doc = re.sub(chinese_regex, '', str(doc))
            doc = re.sub(REGEX, '', doc)
            words = [item for item in list(doc)]
            self.documents[str(index)] = words
            vocabulary.extend(words)
        word_count = collections.Counter(vocabulary)
        self.vocabulary = list(word_count.keys())


class InvertedIndex(DataProcess):
    """
    倒排索引
    """
    def __init__(self, data=None, path=None):
        super(InvertedIndex, self).__init__(data)
        self.word_index = {word: [] for word in self.vocabulary}
        if path:
            self.load(path)
        else:
            self.__build_index()

    def __build_index(self):
        """构建索引"""
        for k, doc in self.documents.items():
            counter = collections.Counter(doc)
            for word in counter.keys():
                if word not in self.word_index:
                    continue
                self.word_index[word].append(k)

    def save(self, path):
        """save"""
        state = {
            'word_index': self.word_index,
            # 'vocabulary': self.vocabulary,
            # 'documents': self.documents
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False)

    def load(self, path):
        with open(path,  'r', encoding='utf-8') as f:
            state = json.load(f)
        # self.vocabulary = state['vocabulary']
        # self.documents = state['documents']
        self.word_index = state['word_index']

    def search(self, query: str):
        """
        问句索引
        :param query: str
        :return:
        """
        indexes = []
        for word in query:
            # index = [item['document_ID'] for item in self.word_index.get(word, {}) if item]
            index = self.word_index.get(word, [])
            if not index:
                continue
            if not indexes:
                indexes = index
                continue
            indexes = list(set(indexes).intersection(set(index)))

        if not indexes:
            return []
        docs = [(''.join(self.documents[index]), index) for index in indexes]
        return docs

    def run(self, query):
        """
        主接口
        :param query: list
        :return:
        """
        query = re.sub(REGEX, '', query)
        if query in BLACK_LIST or (len(query) <= 1 and query not in WHITE_LIST):
            return []
        docs = self.search(query)
        if not docs:
            return []
        texts = list(set([text for text, _ in docs]))
        if len(texts) > 20:
            print(query)
        texts = [text for text in texts if re.search(query, text)]
        similarity = {text: Levenshtein.ratio(''.join(query), text) for text in texts}
        docs_collections = collections.defaultdict(list)
        for doc, index in docs:
            if doc in texts:
                docs_collections[doc].append(index)
        docs_collections = [{'words': key, 'indexes': value, 'score': similarity[key]}
                            for key, value in docs_collections.items()]
        # docs_collections = sorted(docs_collections, key=lambda x: x['score'], reverse=True)
        return docs_collections


if __name__ == '__main__':
    import pandas as pd
    test_data = pd.read_csv('../data/address.csv')
     # 'city', 'town', 'village', 'street'
    for key in ['province', 'city', 'county', 'town', 'village']:
        inverted_index = InvertedIndex(data=test_data[key])
        inverted_index.save('../data/retrieval_{}.json'.format(key))
        print('save!')
    import time
    # t1 = time.time()
    # model = InvertedIndex(path='../data/test_retrieval_province.json')
    # print(model.run(['陕西']))
