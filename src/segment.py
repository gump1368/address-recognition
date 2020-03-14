#! -*- coding: utf-8 -*-
"""
@Author: Gump
@Create Time: 2020/2/26
@Info: 采用最大正向匹配算法做机械分词
"""

import re
from tri_tree import TrieTree

PUNCTUATION = re.compile('[，。？！,.?!]|\s')
EN = re.compile('[a-zA-Z]+')
chinese_regex = 'u[^\u4e00-\u9fa5]'
BLACK_LIST = ['市南', '市北']


class Segment(object):
    def __init__(self, words_path=None):
        self.tree = TrieTree()
        if words_path:
            self.load_word_tree(words_path)

    def load_word_tree(self, path):
        self.tree.load(path)

    def build_word_tree(self, word):
        self.tree.add_word(word)

    def segment(self, sentence, seg_len=4):
        sentence = re.sub(chinese_regex, '', sentence)
        start = 0
        part = sentence[start:seg_len]

        while True:
            seg_words, position = self.part_segment(part)
            if seg_words in BLACK_LIST:
                position = position - (len(seg_words) - 1)
                seg_words = seg_words[0]

            if len(seg_words) > 1:
                yield {'words': seg_words, 'offset': (start, start+position)}

            start += position
            part = sentence[start:start+seg_len]

            if start >= len(sentence):
                break

    def part_segment(self, part_sentence):
        position = len(part_sentence)
        while True:
            if self.tree.is_has_word(part_sentence) or part_sentence == '*' or len(part_sentence) == 1:
                break
            position -= 1
            part_sentence = part_sentence[:position]

        return part_sentence, position


if __name__ == '__main__':
    seg = Segment(words_path='../data/town_tree.json')
    test_s = '深圳市南山区桃源街道平山设区'
    seg_result = seg.segment(sentence=test_s, seg_len=10)
    print(list(seg_result))
