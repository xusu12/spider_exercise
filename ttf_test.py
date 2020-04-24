"""
    字体反爬
"""
import requests
import xml
import time
from lxml import etree
from fontTools.ttLib import TTFont


# 加载woff字体
font = TTFont('1.ttf')
# 将woff字体保存成xml格式
font.saveXML('1.xml')

