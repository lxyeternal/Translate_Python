from config import *
import urllib.request
import pymysql
from HandleJs import Py4Js

START_ID = 1000001              #  数据库连接
COUNT = 0
SQL_Q = "select content from forums where id = %d"
SQL_I = "update forums set content = %s where id = %d"

connect = pymysql.connect(

    host = MYSQL_HOST,
    port = MYSQL_PORT,
    user = MYSQL_USER,
    passwd = MYSQL_PASSWD,
    db = MYSQL_DBNAME,
    charset = MYSQL_CHARSET
)

def query_content(count):           # 数据查询

    cursor = connect.cursor()
    id = START_ID + count
    mysql = SQL_Q % (id)
    cursor.execute(mysql)
    result = cursor.fetchone()
    content_ru = result[0]
    return content_ru,id

def insert_content(content,id):     # 翻译后的数据更新

    cursor = connect.cursor()
    mysql = SQL_I % (content,id)
    cursor.execute(mysql)
    connect.commit()

def open_url(url):                  # 语句请求翻译

    headers = HEADER
    req = urllib.request.Request(url=url, headers=headers)
    response = urllib.request.urlopen(req)
    data = response.read().decode('utf-8')
    return data

def trans_en(ori_content):          # 构造url，进行翻译

    content = urllib.parse.quote(ori_content)
    js = Py4Js()
    tk = js.getTk(ori_content)
    url = "https://translate.google.cn/translate_a/single?client=webapp&sl=auto&tl=en&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&dt=gt&clearbtn=1&otf=1&pc=1&ssel=3&tsel=0&kc=2&tk=%s&q=%s" % (tk, content)
    en_content = open_url(url)
    end = en_content.find("\",")
    if end > 4:
        end_content = en_content[4:end]    #  最终翻译的结果
        return end_content

def content_deal(content):          # 超长字符处理，这里定义google最大支持翻译字符串长度为4900

    if len(content) <= 4900:
        en_contant = trans_en(content).strip()

    else:     #  超长字符串处理
        len_num = int(len(content)/4900)
        content_list = []
        trans_content = ''
        for k in range(len_num + 1):
            temp = content[4900*k:4900*(k+1) + 1]
            content_list.append(temp)

        for str in content_list:
            trans_content  = trans_content + trans_en(str)

        en_contant = trans_content.strip()

    return en_contant

if __name__ == "__main__":

    for num in range(3599):

        count = num + COUNT
        content_ru, id = query_content(count)
        en_contant = content_deal(content_ru)
        print(en_contant)
        print(id)
        # insert_content(en_contant,id)



