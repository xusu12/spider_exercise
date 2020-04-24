import xlwt
import requests
from lxml import etree


# 请求网页数据
def download(url):
    res = requests.get(url)
    text = res.content.decode('utf8')
    html = etree.HTML(text)
    return html


# 保存数据
def save_data(data, file_name):
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = book.add_sheet('mysheet', cell_overwrite_ok=True)

    length = len(data['日期'])
    sheet.write(0, 0, '股票简介')
    sheet.write(0, 1, '公司名称')
    sheet.write(0, 2, '股票代码')
    for y in range(1, length+1):
        sheet.write(y, 0, '国电电力')
        sheet.write(y, 1, '国电电力发展股份有限公司')
        sheet.write(y, 2, 600795)

    x = 3
    for key, value in data.items():
        sheet.write(0, x, key)
        y = 1
        for val in value:
            sheet.write(y, x, val)
            y += 1
        book.save('./{}.xls'.format(file_name))
        x += 1


# 解析净利润数据
def get_pfinance_data(url):
    html = download(url)

    '''
    净利润数据
    '''
    profit_data = {}
    # 获取每个指标字段
    categorys = html.xpath('//div[@class="col_l"]//tbody//td/text()')

    # 获取表格中的每一行数据
    trs = html.xpath('//div[@class="col_r"]//tr')
    for index, tr in enumerate(trs):
        if index == 0:
            profit_data['日期'] = tr.xpath('./th/text()')
        else:
            profit_data[categorys[index - 1]] = tr.xpath('./td/text()')
    save_data(profit_data, '净利润')

    '''
    盈利能力数据
    '''
    profitability_data = {}

    # 获取每个指标字段
    categorys = html.xpath('/html/body/div[2]/div[4]/div[3]/div[4]/table//td[@class="td_1"]/text()')

    # 获取表格中的每一行数据
    trs = html.xpath('/html/body/div[2]/div[4]/div[3]/div[4]/table//tr')
    for index, tr in enumerate(trs):
        if index == 0:
            profitability_data['日期'] = tr.xpath('./th/text()')
        else:
            profitability_data[categorys[index - 1]] = tr.xpath('./td/text()')[1:]
    save_data(profitability_data, '盈利能力')

    '''
    偿还能力数据
    '''
    repaying_capability_data = {}

    # 获取每个指标字段
    categorys = html.xpath('/html/body/div[2]/div[4]/div[5]/div[4]/table//td[@class="td_1"]/text()')

    # 获取表格中的每一行数据
    trs = html.xpath('/html/body/div[2]/div[4]/div[5]/div[4]/table//tr')
    for index, tr in enumerate(trs):
        if index == 0:
            repaying_capability_data['日期'] = tr.xpath('./th/text()')
        else:
            repaying_capability_data[categorys[index - 1]] = tr.xpath('./td/text()')[1:]
    save_data(repaying_capability_data, '偿还能力')

    '''
      成长能力数据
    '''
    growth_ability_data = {}

    # 获取每个指标字段
    categorys = html.xpath('/html/body/div[2]/div[4]/div[7]/div[4]/table//td[@class="td_1"]/text()')

    # 获取表格中的每一行数据
    trs = html.xpath('/html/body/div[2]/div[4]/div[7]/div[4]/table//tr')
    for index, tr in enumerate(trs):
        if index == 0:
            growth_ability_data['日期'] = tr.xpath('./th/text()')
        else:
            growth_ability_data[categorys[index - 1]] = tr.xpath('./td/text()')[1:]
    save_data(growth_ability_data, '成长能力')

    '''
      营运能力数据
    '''
    operation_ability_data = {}

    # 获取每个指标字段
    categorys = html.xpath('/html/body/div[2]/div[4]/div[9]/div[4]/table//td[@class="td_1"]/text()')

    # 获取表格中的每一行数据
    trs = html.xpath('/html/body/div[2]/div[4]/div[9]/div[4]/table//tr')
    for index, tr in enumerate(trs):
        if index == 0:
            operation_ability_data['日期'] = tr.xpath('./th/text()')
        else:
            operation_ability_data[categorys[index - 1]] = tr.xpath('./td/text()')[1:]
    save_data(operation_ability_data, '营运能力')


# 获取 财务报表摘要 数据
def get_abstract_data(url):
    html = download(url)

    '''
        财务报表摘要数据
    '''
    abstract_data = {}
    # 获取每个指标字段
    categorys = html.xpath('//td[@class="td_1"]//text()')

    # 获取表格中的每一行数据
    trs = html.xpath('//div[@class="col_r"]//tr')
    for index, tr in enumerate(trs):
        if index == 0:
            abstract_data['日期'] = tr.xpath('./th/text()')
        if index in [1, 9, 20]:
            pass
        else:
            abstract_data[categorys[index - 1]] = tr.xpath('./td/text()')
    save_data(abstract_data, '财务报表摘要')


# 获取 资产负债表 数据
def get_debt_data(url):
    html = download(url)

    '''
        资产负债表数据
    '''
    debt_data = {}
    # 获取每个指标字段
    categorys = html.xpath('//td[@class="td_1"]//text()')

    # 获取表格中的每一行数据
    trs = html.xpath('//div[@class="col_r"]//tr')
    for index, tr in enumerate(trs):
        if index == 0:
            debt_data['日期'] = tr.xpath('./th/text()')
        if index in [0, 1, 27, 55, 56, 89, 100]:
            pass
        else:
            debt_data[categorys[index - 1]] = tr.xpath('./td/text()')
    save_data(debt_data, '资产负债表')


# 获取 利润表 数据
def get_profit_data(url):
    html = download(url)

    '''
        利润表
    '''
    profit_data = {}
    # 获取每个指标字段
    categorys = html.xpath('//td[@class="td_1"]//text()')

    # 获取表格中的每一行数据
    trs = html.xpath('//div[@class="col_r"]//tr')
    for index, tr in enumerate(trs):
        if index == 0:
            profit_data['日期'] = tr.xpath('./th/text()')
        if index in [0, 8, 33, 40, 44]:
            pass
        else:
            profit_data[categorys[index - 1]] = tr.xpath('./td/text()')
    save_data(profit_data, '利润表')


# 获取 现金流量表 数据
def get_flows_data(url):
    html = download(url)

    '''
        现金流量表
    '''
    flows_data = {}
    # 获取每个指标字段
    categorys = html.xpath('//td[@class="td_1"]//text()')

    # 获取表格中的每一行数据
    trs = html.xpath('//div[@class="col_r"]//tr')
    for index, tr in enumerate(trs):
        # print(len(tr.xpath('./th/text()')))
        if index == 0:
            flows_data['日期'] = tr.xpath('./th/text()')
        if index in [0, 1, 27, 43, 56, 58, 63, 89, 93]:
            pass
        else:
            flows_data[categorys[index - 1]] = tr.xpath('./td/text()')

    save_data(flows_data, '现金流量表')


def get_data(stock_code):
    # 调用获取 主要财务指标 数据的方法
    url = 'http://quotes.money.163.com/f10/zycwzb_{}.html#01c02'.format(stock_code)
    get_pfinance_data(url)

    # 调用获取 财务报表摘要 数据的方法
    url = 'http://quotes.money.163.com/f10/cwbbzy_{}.html#01c04'.format(stock_code)
    get_abstract_data(url)

    # 调用获取 资产负债表 数据的方法
    url = 'http://quotes.money.163.com/f10/zcfzb_{}.html#01c05'.format(stock_code)
    get_debt_data(url)

    # 调用获取 利润表 数据的方法
    url = 'http://quotes.money.163.com/f10/lrb_{}.html#01c06'.format(stock_code)
    get_profit_data(url)

    # 调用获取 现金流量表 数据的方法
    url = 'http://quotes.money.163.com/f10/xjllb_{}.html#01c07'.format(stock_code)
    get_flows_data(url)


if __name__ == '__main__':
    stock_code = 600795
    get_data(stock_code)
