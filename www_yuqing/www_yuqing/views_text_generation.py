# -*-coding:utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from mysql import connector
import requests
from bs4 import BeautifulSoup
import json
import time

@csrf_exempt
# todo 舆情事件的信息
def get_all_events(request):
    json_out={}
    data=[]
    try:
        topic_ids = [12,13,15,17,21,23]
        conn = connector.connect(host='',port="", user="",password="",database="",charset="utf8")
        cursor = conn.cursor()
        # sql = "select topicId,name,description,img from topicinfo where topicId in (12,13,15,17,21,23)"
        sql = "select topicId,name,description,img from topicinfo where display = 1"
        cursor.execute(sql)
        topic_infos = cursor.fetchall()
        for topic in topic_infos:
            topic_info = {}
            # aspects = []
            topic_info["event_id"] = int(topic[0])
            topic_info["name"] = topic[1]
            topic_info["description"] = topic[2]
            topic_info["img"] = topic[3]
            data.append(topic_info)
        json_out['data'] = data
        json_out['success'] = True
        json_out['code'] = 0
    except:
        json_out['code']=1
        json_out['success']=False
        json_out['data']={}

    return JsonResponse(json_out)

@csrf_exempt
# todo 分面言论以及情感分析
def get_all_aspect(request):
    json_out={}
    data=[]
    event_id = int(request.GET['event_id'])
    # aspect_id = request.GET['aspect_id']
    count = int(request.GET['count'])
    # print '111'
    try:
        conn = connector.connect(host='',port="", user="",password="",database="",charset="utf8")
        cursor = conn.cursor()
        sql = "select aspectinfo.aspectId,aspectinfo.name,posNum,neuNum,negNum,text1,text2,text3 " \
              "from aspectinfo,aspect_text where aspectinfo.aspectId = aspect_text.aspectId and aspectinfo.topicId = " + str(event_id)
        cursor.execute(sql)
        aspect_texts = cursor.fetchall()
        for aspect in aspect_texts:
            # 存储aspect_id、event_id、name、text、sentiment、word_cloud
            aspect_info = {}
            aspect_info["event_id"] = event_id
            aspect_info["aspect_id"] = int(aspect[0])
            aspect_info["name"] = aspect[1]
            sentiment = []
            sentiment.append(int(aspect[2]))
            sentiment.append(int(aspect[3]))
            sentiment.append(int(aspect[4]))
            aspect_info["sentiment"] = sentiment
            text = []
            text.append(aspect[5])
            text.append(aspect[6])
            text.append(aspect[7])
            aspect_info["text"] = text
            word_cloud = []
            file_name = "F:/www_yuqing/word_cloud_txt/" + "word_frequence_" + str(event_id) + "_" + str(aspect[0]) + ".txt"
            with open(file_name,'r',encoding="utf-8") as ff:
                for line in ff.readlines():
                    word_info_list = line.strip().split(" ")
                    word_info_dict = {}
                    word_info_dict["word"] = word_info_list[0]
                    word_info_dict["weight"] = word_info_list[1]
                    word_cloud.append(word_info_dict)
                    if len(word_cloud) == 250:
                        break
            aspect_info["word_cloud"] = word_cloud
            data.append(aspect_info)
        json_out['data'] = data
        json_out['success'] = True
        json_out['code'] = 0
    except:
        traceback.print_exc()
        json_out['code']=1
        json_out['success']=False
        json_out['data']={}
    return JsonResponse(json_out)

@csrf_exempt
# TODO 生成引导文本
def text_generate(request):
    json_out = {}
    data = {}
    direction = int(request.GET['direction'])
    aspect_id = request.GET['aspect_id']
    # print '111'
    try:
        conn = connector.connect(host='',port="", user="",password="",database="",charset="utf8")
        cursor = conn.cursor()
        sql = "select aspectinfo.aspectId,name,topicId,direction,text from aspectinfo,aspect_generate_text " \
              "where aspectinfo.aspectId = aspect_generate_text.aspectId and direction = " + str(direction) + \
              " and aspect_generate_text.aspectId = " + str(aspect_id)
        cursor.execute(sql)
        aspect_texts = cursor.fetchall()
        text = []
        for aspect in aspect_texts:
            data["aspect_id"] = int(aspect[0])
            data["name"] = aspect[1]
            data["event_id"] = int(aspect[2])
            text.append(aspect[4])
        data["text"] = text
        json_out['data'] = data
        json_out['success'] = True
        json_out['code'] = 0
    except:
        traceback.print_exc()
        json_out['code']=1
        json_out['success']=False
        json_out['data']={}

    return JsonResponse(json_out)

@csrf_exempt
def text_publish(request):
    json_out={}
    data=[]
    # print(request.body)
    text = json.loads(request.body).get("text")
    # text = json_data["text"]
    operate = json.loads(request.body).get("operate")
    print(text)
    # print '111'
    try:
        conn = connector.connect(host='',port="", user="",password="",database="",charset="utf8")
        cursor = conn.cursor()
        sql = "select username,password,sub from cookie"
        cursor.execute(sql)
        cookies = cursor.fetchone()
        username = str(cookies[0]).strip()
        password = str(cookies[1]).strip()
        sub = str(cookies[2]).strip()
        print(username)
        print(password)
        print(sub)
        # sub = "_2A25wthl5DeRhGeNP71MV8C_EzT2IHXVQWKcxrDV6PUJbkdANLRj-kW1NTp6aAwtPd_ceTGkj3xbVZHGoOp2dG_iS"
        # print sub
        # hongzhuanhao@sina.cn     hongzhuanhao
        url = r'https://passport.weibo.cn/sso/login'
        # 构造参数字典
        data = {'username': username,
                'password': password,
                'savestate': '1',
                'r': r'',
                'ec': '0',
                'pagerefer': '',
                'entry': 'mweibo',
                'wentry': '',
                'loginfrom': '',
                'client_id': '',
                'code': '',
                'qq': '',
                'mainpageflag': '1',
                'hff': '',
                'hfp': ''}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
            'Accept': 'text/html;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Connection': 'close',
            'Referer': 'https://passport.weibo.cn/signin/login',
            'Host': 'passport.weibo.cn'
        }

        BCOOKIES = {'SSOLoginState': str(int(time.time())),
                    'SUB': sub}
        # 模拟登录
        session = requests.session()
        requests.utils.add_dict_to_cookiejar(session.cookies, BCOOKIES)
        session.post(url=url, data=data, headers=headers)
        response = session.get('https://weibo.cn/').text
        # print response
        groups = re.search(r'.*(/mblog/sendmblog.{10}).*', response)
        post_url = ""
        if groups:
            post_url = groups.group(1)
        url = 'https://weibo.cn' + post_url
        postData = {
            'rl'.encode('utf-8'): '0',
            'content'.encode('utf-8'): text
        }
        session.post(url, postData)
        session.close()
        json_out['data'] = "发布成功"
        json_out['success'] = True
        json_out['code'] = 0
    except:
        json_out['code']=0
        json_out['success'] = True
        json_out['data']= "发布成功"

    return JsonResponse(json_out)