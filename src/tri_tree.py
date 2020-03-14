#! -*- coding:utf-8 -*-
"""
@Author: Gump
@Create Time: 2020/2/26
@Info: 采用萃树的方式构建词表
"""
import json
from collections import defaultdict


class TrieTree(object):
    def __init__(self, word_list=None, compact=False):
        self.tree = {'root': {}}
        self.root = -1
        if word_list:
            self.add_words(word_list)
        if compact:
            new_tree = {}
            self.compacted_tree(self.tree, new_tree)
            self.tree = new_tree

    def add_words(self, words_list):
        for index, word in enumerate(words_list):
            self.add_word(word)

    def add_word(self, word):
        tree = self.tree['root']
        for char in word:
            if char in tree:
                # tree['is_root'] = -1
                tree = tree[char]
            else:
                tree[char] = {}
                tree = tree[char]
                # tree['is_root'] = 1

    def compacted_tree(self, old_tree, new_tree, new_key=''):
        """压缩树"""
        for key, value in old_tree.items():
            new_key += key
            if not value:
                new_tree[new_key] = value
                new_key = ''
            elif len(value) > 1:
                new_tree[new_key] = {}
                next_tree = new_tree[new_key]
                new_key = self.compacted_tree(value, next_tree, '')
            else:
                sub_key = list(value.keys())[0]
                sub_tree = list(value.values())[0]
                new_key += sub_key
                if not sub_tree:
                    new_tree[new_key] = {}
                    new_key = ''
                else:
                    new_key = self.compacted_tree(sub_tree, new_tree, new_key)
        return new_key

    def is_has_word(self, word):
        local_tree = self.tree['root']
        for char in word:
            if char in local_tree:
                local_tree = local_tree[char]
            else:
                return False
        return True

    def save(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.tree, f, ensure_ascii=False)

    def load(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            word_tree = json.load(f)
        self.tree = word_tree


if __name__ == '__main__':
    import pandas as pd
    data = pd.read_csv('../data/address.csv')
    # 'city', 'town', 'village', 'street'
    for col in ['province', 'city', 'county', 'town', 'village']:
        part = data[col]
        part = list(set(part))
        part = [str(item).strip() for item in part]
        trie = TrieTree(word_list=part)
        trie.save('../data/{}_tree.json'.format(col))
        print(trie.is_has_word('南召县'))
