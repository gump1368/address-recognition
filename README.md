# address-recognition
 中文地址回收
## 简要
根据中国5级地址库：省-市-区/县-镇/乡/街道-村/小区，对文本中地址做提取。 

基于各级地址库分别构建Trie-tree字典树进行切词。可进行完整词长度`len(words))`分词，也可进行部分词`1<len(part_words)<len(words)`
分词。 

基于各级地址库分别构建基于字的倒排索引。这样做的目的是当出现个别错别字时，不影响整体的识别。当然，基于词的索引，效率更高一些。

可对缺省的上级地址做补充。例如：

> 

test address: 我住在深圳市平山社区 

address identify result: {'province': '广东省', 'city': '深圳市', 'county': '南山区', 'town': '桃源街道', 'village': '平山社区'}

## 数据来源
数据来源：[国家统计局](http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/)  

爬虫代码：`scripts/crawl_address.py`  

部分城市需要手动爬取，最终爬取结果一共614157条地址数据。下载链接如下： 

链接：https://pan.baidu.com/s/13M0cAPEHtjfuZpe1jQpIyw 
提取码：y9ap

## 运行说明
`src/tri_tree.py`: 构建分词模型； 

`src/address_retrieval.py`: 构建倒排索引； 

`src/address_identific.py`: 地址识别。
