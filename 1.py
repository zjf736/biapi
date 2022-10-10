import requests
import re

def exist_video(self,video_title):

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
            break  
    return '存在'

sss = exist_video(video_title='当代女性图签')   
print(sss)     

