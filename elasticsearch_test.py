# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch

# 默认host为localhost,port为9200.但也可以指定host与port
es = Elasticsearch(hosts=['172.16.189.1'])

result = es.search(index="article", doc_type="doc")
print(result)

# 插入数据,index，doc_type名称可以自定义，id可以根据需求赋值,body为内容
# es.index(index="my_index", doc_type="test_type", id=0, body={"name": "python", "addr": "深圳"})
# es.index(index="my_index", doc_type="test_type", id=1, body={"name": "python", "addr": "深圳"})

# 同样是插入数据，create() 方法需要我们指定 id 字段来唯一标识该条数据，而 index() 方法则不需要，如果不指定 id，会自动生成一个 id
# es.create(index="my_index", doc_type="test_type", id=1, body={"name": "python", "addr": "深圳"})

# 删除指定的index、type、id的文档
# es.delete(index='my_index', doc_type='test_type', id=1)

# 删除index
# es.indices.delete(index='my_index', ignore=[400, 404])

# query = {'query': {'match_all': {}}}  # 查找所有文档
# query1 = {'query': {'match': {'sex': 'famale'}}}  # 删除性别为女性的所有文档
# query2 = {'query': {'range': {'age': {'lt': 11}}}}  # 删除年龄小于11的所有文档
# query3 = {'query': {'term': {'name': 'jack'}}}  # 查找名字叫做jack的所有文档

# # 删除所有文档
# es.delete_by_query(index="my_index", doc_type="test_type", body=query)
#
# # get：获取指定index、type、id所对应的文档
# es.get(index="my_index", doc_type="test_type", id=1)
#
# # search：查询满足条件的所有文档，没有id属性，且index，type和body均可为None
# result = es.search(index="my_index", doc_type="test_type", body=query)
# print(result['hits']['hits'][0])  # 返回第一个文档的内容
#
# # update：更新指定index、type、id所对应的文档
# # 更新的主要点：
# # 1. 需要指定 id
# # 2. body={"doc": <xxxx>} , 这个doc是必须的
# es.update(index="my_index", doc_type="test_type", id=1, body={"doc": {"name": "python1", "addr": "深圳1"}})
