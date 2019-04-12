from config import *
import pymysql
import urllib.parse
import urllib.request
import http.client
import hashlib
import json

START_ID = 1000001              #  数据库连接
COUNT = 0
appid = '20190410000286677'     # 百度的翻译接口，需要自己填
secretKey = '1Sizz2cmcYlRg3hw51QX'
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
    content_ru = result[0].strip()
    return content_ru,id

def insert_content(content,id):     # 翻译后的数据更新

    cursor = connect.cursor()
    mysql = SQL_I % (content,id)
    cursor.execute(mysql)
    connect.commit()

def trans_en(ori_content):          # 构造url，进行翻译
    httpClient = None
    myurl = '/api/trans/vip/translate'
    q = ori_content
    fromLang = 'auto'
    toLang = 'en'
    salt = random.randint(32768, 65536)
    sign = appid + q + str(salt) + secretKey
    sign = sign.encode('UTF-8')
    m1 = hashlib.md5()
    m1.update(sign)
    sign = m1.hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
        q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)
        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result = response.read().decode("utf-8")
        target = json.loads(result)
        src = target["trans_result"][0]["dst"]
        return src
    except Exception as e:
        return e
    finally:
        if httpClient:
            httpClient.close()

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
        en_contant = trans_en(content_ru)
        print(id)
        print(content_ru)
        print(en_contant)
        # insert_content(en_contant,id)



