import pandas as pd
import requests
from bs4 import BeautifulSoup


def add_country(text, country):
    soup = BeautifulSoup(text, 'html.parser')
    header = soup.find('tr')
    new_header_column = soup.new_tag('th', width="100")
    new_header_column.string = "国家"
    header.append(new_header_column)
    rows = soup.select('tbody tr')
    for row in rows:
        new_column = soup.new_tag('td')
        new_column.string = country
        row.append(new_column)
    return str(soup)


url = "https://jichang.hao86.com"
response1 = requests.get(url, timeout=10)
response1.encoding = "utf-8"
hrefs = []
tables = []
dfs = []
count = 0
if response1.ok:
    soup1 = BeautifulSoup(response1.text, "html.parser")
    div_elements = soup1.find("div", class_='new_jichangindex2tab magtop12')
    a_elements = div_elements.find_all("a")
    hrefs = [a.get('href') for a in a_elements]
    print("----------获取{}个国家信息----------".format(len(hrefs)))
for href in hrefs:
    uh = url + href
    response2 = requests.get(uh, timeout=10)
    response2.encoding = "utf-8"
    if response2.ok:
        soup2 = BeautifulSoup(response2.text, 'html.parser')
        size = len(soup2.find_all("li", class_='page-item')) if len(soup2.find_all("li", class_='page-item')) > 0 else 1
        for i in range(size):
            print("----------开始读取{}第{}页数据----------".format(href, i + 1))
            page = uh + "?page=" + str(i + 1)
            try:
                response3 = requests.get(page, timeout=10)
                response3.encoding = "utf-8"
                soup3 = BeautifulSoup(response3.text, 'html.parser')
                add_content = add_country(str(soup3.find("table")), href.strip("/"))
                tables.append(add_content)
                print("----------读取{}第{}页数据完成----------".format(href, i + 1))
            except requests.exceptions.RequestException as e:
                print("----------读取{}第{}页数据异常:{}----------".format(href, i + 1, e))

print("----------开始合并所有数据存入Excel文件----------")
dfs = [pd.read_html(str(html), flavor='bs4')[0] for html in tables]
result_df = pd.concat(dfs, ignore_index=True)

# 将结果写入 Excel 文件的同一个工作表
excel_filename = "output_merged_tables.xlsx"
result_df.to_excel(excel_filename, index=False)
print("----------所有数据存入Excel文件完成----------")
