from PyQt5.QtWidgets import QApplication, QMessageBox,QWidget,QLineEdit
from PyQt5.QtGui import  QIcon
from PyQt5 import uic
from time import sleep
import requests
import os
import pandas as pd
import re
import sys
import csv
import argparse
import webbrowser
from math import ceil  #数学计算库
from json import dumps
from pathlib import Path 
from requests_html import HTMLSession 
from requests.utils import cookiejar_from_dict 

class Stats:

    def __init__(self):

        # 从文件中加载UI定义
        self.now_path = os.getcwd()
        self.cookies = self.now_path + '/data/cookie.txt'
        self.sessd_jct = self.now_path + '/data/sessd_jct.txt'
        self.ui = uic.loadUi("./image/Biliapi.ui")
        self.ui.setStyleSheet("background-image:url(./image/backdrop.png)")
        self.ui.setMinimumSize(463,512)
        self.ui.setMaximumSize(463,512)
        self.dicts = []
        self.ui.setWindowIcon(QIcon('./image/logo.png'))
        self.ui.log_in.clicked.connect(self.log_ins)
        self.ui.download.clicked.connect(self.downloads)
        self.ui.upload.clicked.connect(self.uploads)
        self.ui.auto_start.clicked.connect(self.auto_starts)

    
    def log_ins(self):
        #从gui文本框中获取cookie、sessdata、bili_jct的值
        try:
            data = []
            jct = self.ui.bili_jct.text()
            sessd = self.ui.bili_sessd.text()
            cookie = self.ui.weibo_cookie.text()
            if  len(cookie) == 0:
                self.ui.text_end.append('请输入cookie')
            elif len(sessd) == 0:
                self.ui.text_end.append('请输入sessd')
            elif len(jct) == 0:
                self.ui.text_end.append('请输入jcd')
            else:    
                if len(jct) > 0 and len(sessd) > 0 and len(cookie) > 0:
                    data.append(cookie)
                    data.append(sessd)
                    data.append(jct)
  

                    if not os.path.exists('./data'):

                        os.mkdir('./data')

                    new_data = data[1]+'\n'+data[2]


                    with open(self.cookies,'w+') as cook:                            
                        cook.write(data[0])
                    cook.close()

                    with open(self.sessd_jct,'w+') as f:                            
                        f.write(new_data)
                    f.close()

                    self.ui.text_end.append('登陆成功')
        except:
            return

    def downloads(self):
        #下载微博视频
        try:
            weibo_ = Weiboapi(self.data_cookies()[0])
            weibo_.start_download()
            self.ui.text_end.append('开始下载')

        except:
            self.ui.text_end.append('未登录')

    def uploads(self):
        #B站上传视频

        res_t = Biliapi(sessdata=self.data_sessd()[0],bili_jct=self.data_sessd()[1])

        file_names = self.seek_file_name()

        titles,https = res_t.get_title_http()

        self.ui.text_end.append('开始上传')

        for i in range(0,len(file_names)):
            res_t.pubish_video(
                video_path=file_names[i],
                video_title=titles[i]+ '---',
                video_description='-',
                video_source=https[i],
                video_type=138,
                )
                #上传完毕后自动删除
            self.ui.text_end.append('%s上传成功'%titles[i])   
            os.remove(file_names[i])
            sleep(60) 


    def auto_starts(self):
        try:
            if not os.path.exists('./data/data.txt'):
                self.ui.text_end.append('请先登陆')
            if os.path.exists('./data/data.txt') == True:
                self.downloads()
                self.uploads()

        except:
            return


    def data_sessd(self):
        #获取data文件夹下的sessdata、bili_jct
        try:
            data_len = []
            datads = open(self.sessd_jct,'r')

            for i in datads.readlines():
                data_len.append(i.strip())
            datads.close()    
            return data_len
        except:
            return 

    def data_cookies(self):
        #获取data文件夹下的cookie
        try:
            data_cookie_s = []
            datad_s = open(self.cookies,'r')

            for i in datad_s.readlines():
                data_cookie_s.append(i.strip())
            datad_s.close()    
            return data_cookie_s
        except:
            return 


    def seek_file_name(self):
        # root 表示当前正在访问的文件夹路径
        # dirs 表示该文件夹下的子目录名list
        # files 表示该文件夹下的文件list
        #遍历文件名

        video_path = self.now_path +'/video'
        for paths,dirs,flist, in os.walk(video_path):
            #获取文件名
            for files in flist:
                self.dicts.append(os.path.join(paths, files))
        print(self.dicts)
        return self.dicts

class Weiboapi(Stats):


    def __init__(self,cookie,):
        super(Weiboapi, self).__init__()
        self.video_oid=[]
        self.cookie=cookie
        self.video_page=[]
        self.allman = []
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
            'referer':'https://weibo.com/tv/hot',
            'origin': 'https://weibo.com',
            'page-referer': '/tv/show/1034:4609930964172879'
        }

    def exist_video(self,video_title):

        #验证B站是否在这个视频
        try:
            url = 'https://api.bilibili.com/x/web-interface/search/type?'

            params = {
                'context' : '',
                'search_type' : 'video',
                'page' : 1,
                'order' : '',
                'keyword' : video_title,
                'duration' : '',
                'category_id': '',
                'tids_1': '',
                'tids_2': '',
                '__refresh__': 'true',
                '_extra': '',
                'highlight': 1,
                'single_column' : 0,}

            res = requests.get(url,headers={'TE': 'Trailers'},params=params).json()
            lists=res['data']['result']
            for i in range(0,len(lists)):
                trues_video = re.sub(r'[\[\]【】<em class="keyword">\/]','',lists[i]['title'])
                if video_title == trues_video:
                    return '存在'
                    break  
        except:            
            return '不存在'

    def get_videolist(self):
        #返回所有视频的请求头信息的列表
        url = 'https://weibo.com/tv/api/component'
        
        self.headers.update({'cookie':self.cookie})
        
        data = {'data': '{"Component_Billboard_Billboardlist":{"cid":"4418219809678869","count":20}}'}

        params = {'page': '/tv/subbillboard/4418219809678869'}

        res = requests.post(url, headers=self.headers, params = params, data=data).json()

        videosdata = res['data']['Component_Billboard_Billboardlist']['list']

        for void in videosdata:
            oid = void['oid']
            page = '/tv/show/' + oid
            datainfo = '{"Component_Play_Playinfo":{"oid":"'+oid+'"}}'
            self.video_oid.append(page)
            self.video_page.append(datainfo) 
        


    def parsevideo(self,page, datainfo, allman):
        #解析视频地址并下载视频
        person = []
        url = 'https://weibo.com/tv/api/component'
        params = {'page': page}
        data = {'data': datainfo}

        try:

            res = requests.post(url, headers=self.headers, params=params, data=data).json()
            title1 = res['data']['Component_Play_Playinfo']['title']
            title = title1.replace(' ', '').replace('/', ',')
               
        except Exception:
         
            self.ui.text_end.append('%s此视频无法下载'%title)
            return 
        verifys = self.exist_video(video_title=title)

        if '不存在' == verifys :        
            
            if '高清 1080P' in res['data']['Component_Play_Playinfo']['urls']:          
                videourl = res['data']['Component_Play_Playinfo']['urls']['高清 1080P']
        
            elif '高清 720P' in res['data']['Component_Play_Playinfo']['urls']:              
                videourl = res['data']['Component_Play_Playinfo']['urls']['高清 720P']
        
            else:
                videourl = res['data']['Component_Play_Playinfo']['urls']['标清 480P']

           
            videourl = 'http:' + videourl
            person.append(title1)
            person.append(videourl)
            allman.append(person)
            item = requests.get(videourl, headers = self.headers).content
            self.mkdir()
            self.videowrite(title, item)
            sleep(0.5)
            return
        else:
            return    
        


    def videowrite(self,name, item):
        #保存文件
        try:
            with open(f'./video/{name}.mp4', 'wb') as f:
                f.write(item)
                self.ui.text.append('%s已下载'%name)
        except Exception:
            pass


    def mkdir(self):
        #判断当前路径有没有video这个文件夹，没有就创建
        if not os.path.exists('./video'):
            os.mkdir('./video')


    def start_download(self):

        self.get_videolist()
        works = []

        for i in range(0,20):
            print('c')
            sleep(1.5)
            works_end = self.parsevideo(self.video_oid[i],self.video_page[i],self.allman)
            works.append(works_end)        
            sleep(1.5)      

        dataframe = pd.DataFrame(self.allman)
        dataframe.to_csv('./data/weibovideo.csv', mode='a+', index=False, header=False, encoding='utf_8_sig')
        self.ui.text_end.append('所有视频下载完成')


class Biliapi(Stats):
    ua={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74',}
    headers={'TE':'Trailers'}
 
    #初始化
    def __init__(self,sessdata,bili_jct):
        super(Biliapi, self).__init__()
        self.SESSDATA = sessdata
        self.bili_jct = bili_jct
        self.now_path = os.getcwd()
        self.auth_cookies = {'SESSDATA':sessdata,
            'bii_jct':bili_jct}
        self.video_csv = self.now_path + '/data/weibovideo.csv'
        self.session = HTMLSession()
        self.session.cookies = cookiejar_from_dict(self.auth_cookies)
        self.session.headers = self.ua
        self.dicts = []
        self.title = []
        self.http = []
  
    #预上传
    def preupload(self,video_name,video_size):
        """
        video_name 视频的名称
        video_size 视频字节
        """
        #请求地址
        url = 'https://member.bilibili.com/preupload'
        #请求需要的参数
        params = {
            'name':video_name,
            'size':video_size,
            'r': 'upos',
            'profile': 'ugcupos/bup',
            'ssl': '0',
            'version': '2.8.12',
            'build': '2081200',
            'upcdn': 'qn',
            'probe_version': '20200810',}
        res_json = self.session.get(url,params=params,headers=self.headers).json()
        #assert res_json['ok'] == 1
        
        return res_json


    def pubish_video(self,video_path,video_description,video_source,video_type=None,video_title=None,video_tags=None,copyrightsd=2):
        #video_path:视频地址
        #video_title:视频标题
        #video_description:视频描述，简介
        #copyright:视频版权  1:自制，2:转载 
        #video_source:视频来源（视频链接）
        #video_type:视频分区 int类型
        #video_tags:视频标签 字符串逗号分隔
        price=2   #迭代用的值，以作记录每周打卡的数
        iteration=1  #迭代用的值，以作记录每周打卡的次数
        #获取视频
        try:
            video_paths = Path(video_path)
            assert video_paths.exists(),f'不存在文件{video_paths}'
            # 文件名，带后缀
            full_video_name = video_paths.name
            # 文件名，不包含后缀
            no_full_video_name = video_title or video_paths.stem
            #视频大小
            video_size = video_paths.stat().st_size
            #print(f'视频名称:{}'.format(no_full_video_name))
            sleep(1.5)

            #调用函数 返回的是一个字典
            res_up_video=self.preupload(video_paths,video_size)
            upos_uri=res_up_video['upos_uri'].split('//')[-1]
            auth = res_up_video['auth']
            biz_id = res_up_video['biz_id']
            chunk_size = res_up_video['chunk_size']
            #计算批次
            chunks = ceil(video_size/chunk_size)
            
            res_up_video_two = self.upload_post(upos_uri=upos_uri, auth=auth)
            upload_id = res_up_video_two['upload_id']
            key = res_up_video_two['key']
            # 存于bilibili的视频文件名(无后缀)
            bili_name = re.search(r'/(.*)\.', key).group(1)
            
            fileio = video_paths.open(mode = 'rb')
            #开始
            self.upload_put(
                upos_uri = upos_uri,
                auth = auth,
                upload_id = upload_id,
                fileio = fileio,
                filesize = video_size,
                chunk_size = chunk_size,
                chunks = chunks)
            fileio.close()
            #进行
            self.upload_finish(
                upos_uri = upos_uri,
                auth = auth, 
                filename = full_video_name,
                upload_id = upload_id, 
                biz_id = biz_id, 
                chunks = chunks)
            #选择分区                   
            typeid = video_type or self.choose_type(
                title = video_paths, 
                bfilestem = bili_name, 
                typeid = video_type,
                desc = video_description,)[0]
            #选择标签    
            if not video_tags:
                tags = self.choose_tags(
                    title = video_paths, 
                    bfilestem=bili_name, 
                    typeid=video_type, 
                    desc=video_description)
                #前面两个视频选择标签带打卡记录    

            else:
                tags_text = video_tags
            #获取视频封面
            cover_urlsd = self.choose_cover(bfilestem=bili_name)[0]
            #上传
            self.pre_add()
            
            res_adds=self.adds(
                copyrights=copyrightsd,
                covers=cover_urlsd,
                descs=video_description,
                sources=video_source,
                tags=tags_text,
                tids=video_type,
                titles=video_title,
                biz_ids=biz_id,
                filenames=bili_name,
                )                                          
            
        except:
            
            self.ui.text_end.append('%s上传失败'%video_title)


    def upload_finish(self, upos_uri, auth, filename, upload_id, biz_id, chunks):
        """
        通知视频已上传完毕
        upos_uri: preupload返回值
        auth: preupload返回值
        filename: 视频文件名，带后缀
        upload_id: upload_post返回值
        biz_id: preupload返回值
        chunks:批次
        """
        url = f'https://upos-sz-upcdnbda2.bilivideo.com/{upos_uri}'
        params = {
            'output':	'json',
            'name':	filename,
            'profile'	: 'ugcupos/bup',
            'uploadId':	upload_id,
            'biz_id':	biz_id
        }
        data = {"parts": [{"partNumber": i, "eTag": "etag"}

                          for i in range(chunks, 1)]}
        res_json = self.session.post(url, params=params, json=data,
                                     headers={'X-Upos-Auth': auth}).json()
        

    def choose_cover(self, *, bfilestem, wait_sec=15):
        """
        轮询等待封面获取

        bfilestem: 存于bilibili的视频文件名(无后缀)
        wait_sec: 等待秒数
        """
        url = f'https://member.bilibili.com/x/web/archive/recovers?fns={bfilestem}'
        while True:
            res_json = self.session.get(
                url, headers={'TE': 'Trailers'}).json()
            allow_covers = res_json['data']
            if allow_covers:
                #print(allow_covers)
                return allow_covers
            sleep(wait_sec)
            

    def upload_post(self,upos_uri,auth):
        """
        上传视频前的准备工作
        upos_uri: preupload返回值
        auth: preupload返回值
        """
        url = f'https://upos-sz-upcdnbda2.bilivideo.com/{upos_uri}?uploads&output=json'
        res_json = self.session.post(url, headers={'X-Upos-Auth': auth}).json()
        
        return res_json


    def upload_put(self, *, upos_uri, auth, upload_id, fileio, filesize, chunk_size, chunks):
        """
        分批上传视频

        upos_uri: preupload返回值
        auth: preupload返回值
        upload_id: upload_post返回值
        fileio: 视频文件的io流
        filesize: 视频文件大小
        chunk_size: 一个批次上传多大字节的视频，preupload返回值
        chunks: 计算得出的该分多少批次上传
        """
        url = f'https://upos-sz-upcdnbda2.bilivideo.com/{upos_uri}'
        params = {
            'partNumber': None,  # 1开始
            'uploadId':	upload_id,
            'chunk':	None,  # 0开始
            'chunks':	chunks,
            'size':	None,  # 当前批次size
            'start':	None,
            'end':	None,
            'total':	filesize,
        }
        for batchno in range(chunks):
            start = fileio.tell()
            batchbytes = fileio.read(chunk_size)
            params['partNumber'] = batchno + 1
            params['chunk'] = batchno
            params['size'] = len(batchbytes)
            params['start'] = start
            params['end'] = fileio.tell()
            res = self.session.put(url, params=params, data=batchbytes, headers={
                                   'X-Upos-Auth': auth})
            #assert res.status_code == 200
            

    def choose_tags(self, title, bfilestem, typeid, desc, limit=10):
        """
        选择标签
        title: 视频标题
        desc:视频简介
        bfilestem: 存于bilibili的视频文件名(无后缀)
        typeid: 分区id
        limit: 10个标签，B站允许最多10个标签
        """
        url = 'https://member.bilibili.com/x/web/archive/tags'
        params = {
            'typeid':typeid,  # TODO:添加分区貌似有问题，先为空
            'title': title,
            'filename':	bfilestem,
            'desc': desc,
            'cover': '',
            'groupid': 0,
            'vfea': ''
        }
        res_json = self.session.get(url, params=params,  headers={
                                    'TE': 'Trailers'}).json()
        # print(dumps(res_json, ensure_ascii=False), end='\n'+'-'*50+'\n')
        tags = [i['tag'] for i in res_json['data']]
        if limit:
            tags = tags[:limit]
        return tags
    

    def choose_type(self, title, bfilestem, desc):
        """
        选择分区
        title: 视频标题
        bfilestem: 存于bilibili的视频文件名(无后缀)
        desc: 视频简介
        """
        url = 'https://member.bilibili.com/x/web/archive/typeid'
        params = {
            'title': title,
            'filename':	bfilestem,
            'desc': desc,  # 视频简介
            'cover': '',
            'groupid': '0',  # 暂不清楚用处
            'vfea': ''
        }
        res_json = self.session.get(url, params=params, headers={'TE': 'Trailers'}).json()
        best_type = [(i['id'], i['name']) for i in res_json['data']][0]
        return best_type


    def adds(self,copyrights,covers,descs,sources,tags,tids,titles,biz_ids,filenames):
        url = f'https://member.bilibili.com/x/vu/web/add?csrf={self.bili_jct}'
        data={
            'copyright':copyrights,                                                 #版权  1自制  2转载
            'cover':  covers,                                                      #视频封面
            'desc':  descs,                                                        #视频简介
            'desc_format_id':32,                                              #
            'dynamic':'' ,                                                      #动态
            'source': sources,                                                        #视频来源（转载地址）
            'subtitle':{'lan':'zh-CN','open':0},
            'tag': tags,                                                          #视频标签
            'tid':    tids,                                                       #视频分区
            'title': titles,                                                        #视频标题
            'up_close_danmu':False,
            'up_close_reply':False,
            'videos':[{
                'cid':biz_ids, 
                'desc':'',
                'filename':filenames,
                'title':titles,
                }]
        }
        if copyrights != 2:
            del data['source']
            data['copyright'] = 1
            data['interactive'] = 0
            data['no_reprint'] = 1

        res_json = self.session.post(url, json=data, headers={'TE': 'Trailers'}).json()

        return res_json


    def get_title_http(self):
        #获取title和http

        title_name = csv.reader(open(self.video_csv,'r',encoding='UTF-8'))
        for i in title_name:
            self.title.append(i[0])
            self.http.append(i[1])
        return self.title,self.http

    def pre_add(self):
        url = 'https://member.bilibili.com/x/geetest/pre/add'
        self.session.get(url, headers={'TE': 'Trailers'})



app = QApplication([])
stats = Stats()
stats.ui.show()
app.exec_()
