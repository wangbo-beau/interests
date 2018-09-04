#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/24 20:10
# @Author  : wangbo
# @File    : netflow.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup

# 启动浏览器驱动
browser = webdriver.PhantomJS(executable_path='phantomjs.exe',service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
# browser = webdriver.Firefox()
# 设置等待时间
wait = WebDriverWait(browser, 10)
# 查询流量余额首先需要登录的页面
query_url = "http://auth.xjtu.edu.cn/"
# 查询流量的页面
current_url = 'http://auth.xjtu.edu.cn/current.aspx'
# 连接上网的登录页面
auth_url = 'http://10.6.8.2'

class XJTUNetflow():

    def __init__(self):
        self.infos = {}
        self.sorted_infos = []

    # 从user.conf配置文件中读取各个用户名和密码
    def get_userinfos(self):
        try:
            with open('user.conf',mode='r',encoding='utf-8') as ff:
                lines = ff.readlines()
                for line in lines:
                    info = line.split(',')
                    # 去除后面的换行符
                    self.infos[info[0]] = info[1].strip()
        except FileNotFoundError:
            print('找不到user.conf文件，请检查！')
            exit()
        if(len(self.infos)==0):
            print('无用户信息，请检查！')
            exit()

    # 得到各个用户的流量使用情况并排序
    def get_sorted_infos(self):
        for username, passwd in self.infos.items():
            info = self.query_login(username,passwd)
            self.sorted_infos.append(info)
        self.sorted_infos = sorted(self.sorted_infos, key=lambda x: float(x['入流量']) + float(x['出流量']))
        with open('currentInfos.txt',mode='w',encoding='utf-8') as ff:
            ff.write("用户名,入流量,出流量,ip,费用,时间\n")
            for info in self.sorted_infos:
                ff.write(info['用户名']+","+str(info['入流量'])+","+str(info['出流量'])+","+info['ip']+","+info['费用']+","+info['时间']+"\n")

    # 用剩余流量最多的用户登录
    def auth_login(self):
        min_username = self.sorted_infos[0]['用户名']
        min_passwd = self.infos[min_username]
        old_username = ''
        # 如果之前有登录记录，则得到之前的登录信息，然后先注销，再换新号登录
        # 如果不存在登录记录，则old_username还为空
        try:
            with open('login_log.txt',mode='r',encoding='utf-8') as ff:
                old_username = ff.readline()
        except FileNotFoundError:
            print('login_log.txt不存在，将创建该文件')
        # 如果存在登录记录，在进行以下操作，否则可以直接登录
        if old_username:
            # 如果用户名相同则说明不必再换号
            # if min_username == old_username:
            #     return
            # 否则需要先注销再登录
            # 注销
            old_passwd = self.infos[old_username]
            self.auth_logout(old_username, old_passwd)
        # 登录
        self._auth_login(min_username, min_passwd)
        # 写入登录信息
        with open('login_log.txt',mode='w',encoding='utf-8') as ff:
            ff.write(min_username)

    # 注销功能
    def auth_logout(self,username,passwd):
        browser.get(auth_url)
        # 分别获取用户名、密码和注销节点
        username_input = wait.until(EC.presence_of_element_located((By.NAME,'username')))
        passwd_input = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
        logout_button = wait.until(EC.presence_of_element_located((By.XPATH, '//img[@alt="注销"]')))
        username_input.clear()
        username_input.send_keys(username)
        passwd_input.clear()
        passwd_input.send_keys(passwd)
        logout_button.click()

    # 登录功能
    def _auth_login(self,username,passwd):
        browser.get(auth_url)
        # 分别获取用户名、密码和注销节点
        username_input = wait.until(EC.presence_of_element_located((By.NAME, 'username')))
        passwd_input = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
        login_button = wait.until(EC.presence_of_element_located((By.ID, 'button')))
        username_input.clear()
        username_input.send_keys(username)
        passwd_input.clear()
        passwd_input.send_keys(passwd)
        login_button.click()

    # 登录query_url
    def query_login(self,username,passwd):
        browser.get(query_url)
        browser.maximize_window()
        username_input = wait.until(EC.presence_of_element_located((By.ID,'TB_userName')))
        passwd_input = wait.until(EC.presence_of_element_located((By.ID, 'TB_password')))
        # 清空当前文本框内容
        username_input.clear()
        username_input.send_keys(username)
        passwd_input.clear()
        passwd_input.send_keys(passwd)
        # 登录按钮
        submit = wait.until(EC.element_to_be_clickable((By.ID, 'Button1')))
        submit.click()
        # 等待直到本月流量信息出现
        wait.until(EC.presence_of_element_located((By.XPATH,'//td/a[contains(text(), "本月流量信息")]')))
        browser.get(current_url)
        wait.until(EC.presence_of_element_located((By.ID, 'ctl00_mainContent_DetailsView1')))
        return self.get_info(username)

    # 查询流量使用情况
    def get_info(self,username):
        html_cont = browser.page_source
        # 使用beautifulsoup解析
        soup = BeautifulSoup(html_cont, 'html.parser', from_encoding='gb2312')
        table_node = soup.find('table',id='ctl00_mainContent_DetailsView1')
        tr_nodes = table_node.find_all('tr')
        info = {'用户名':username,'入流量':0,'出流量':0,'ip':'','费用':'','时间':''}
        for tr in tr_nodes:
            temp_list = []
            for td in tr.find_all('td'):
                text = td.get_text()
                # 统一换算成GB为单位
                if text.endswith('MB'):
                    text = round(float(text[0:-2])/1024,3)
                elif text.endswith('GB'):
                    text = float(text[0:-2])
                elif text.endswith('KB'):
                    text = round(float(text[0:-2])/(1024*1024), 3)
                temp_list.append(text)
            info[temp_list[0]] = temp_list[1]
        return info

if __name__=="__main__":
    xjtu = XJTUNetflow()
    # 先得到user.conf里面的账户密码信息
    xjtu.get_userinfos()
    # 查询流量余额并排序
    xjtu.get_sorted_infos()
    # 登录剩余流量最多的用户
    xjtu.auth_login()