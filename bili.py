# -*- coding: utf-8 -*-
# 这里参考了https://blog.csdn.net/qq_18303993/article/details/114481841
import qrcode
from threading import Thread
import time
import requests
import tkinter as tk
from io import BytesIO
import http.cookiejar as cookielib
from PIL import Image, ImageTk
import os
import pandas as pd
from pandas.api.types import CategoricalDtype
import webbrowser
import xlwt
import matplotlib.pyplot as plt 
import matplotlib.cm as cm 
from webdav4.client import Client

def get_key(val, dict):
    for key, value in dict.items():
         if val in value:
             return key

def linspace(start, stop, num):
    step = (stop - start) / (num - 1)
    return [start + i * step for i in range(num)]

def get_index(val, cate, keys_cate, dict):
    index = 0
    if cate == '番剧':
        index = 104
    elif cate == '电影':
        index = 105
    elif cate == '电视剧':
        index = 106
    elif cate == '纪录片':
        index = 107
    elif cate == '国创':
        index = 108
    elif cate == '综艺':
        index = 109
    elif cate in keys_cate:
        t = keys_cate.index(cate)
        for i in range(t):
            index = index + len(dict[keys_cate[i]])
        list_tmp = dict[cate]
        index = index + list_tmp.index(val) + 1
    else:
        index = 110
    return index

requests.packages.urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36', 'Referer': "https://www.bilibili.com/"}
headerss = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',  'Host': 'passport.bilibili.com','Referer': "https://passport.bilibili.com/login"}

class showpng(Thread):
    def __init__(self, data):
        Thread.__init__(self)
        self.data = data

    def run(self):
        img = Image.open(BytesIO(self.data))
        w = tk.Tk()

        photo = ImageTk.PhotoImage(img)
        image_Label = tk.Label(w, image=photo)
        image_Label.pack()

        w.attributes('-topmost', 1)
        # 给主窗口起一个名字，也就是窗口的名字
        w.title('请用b站app扫码登录')
        w.mainloop()

def bzlogin():
    if not os.path.exists('bzcookies.txt'):
        with open("bzcookies.txt", 'w') as f:
            f.write("")
    session = requests.session()
    session.cookies = cookielib.LWPCookieJar(filename='bzcookies.txt')

    getlogin = session.get('https://passport.bilibili.com/x/passport-login/web/qrcode/generate', headers=headers).json()
    loginurl = requests.get(getlogin['data']['url'], headers=headers).url
    qrcode_key = getlogin['data']['qrcode_key']
    qr = qrcode.QRCode()
    qr.add_data(loginurl)
    img = qr.make_image()
    a = BytesIO()
    img.save(a, 'png')
    png = a.getvalue()
    a.close()
    t = showpng(png)
    t.start()
    tokenurl = 'https://passport.bilibili.com/x/passport-login/web/qrcode/poll'
    while 1:
        url = tokenurl + '?qrcode_key=' + qrcode_key
        qrcodedata = session.get(url, headers=headerss).json()
        # print(qrcodedata)
        if qrcodedata['data']['code'] == 86090:
            print('已扫码，请确认！')
        elif qrcodedata['data']['code'] == 86038:
            print('二维码已失效，请重新运行！')
            session = ''
            break
        elif qrcodedata['data']['code'] == 0:
            print('已确认，登入成功！')
            session.get(qrcodedata['data']['url'], headers=headers)
            break
        time.sleep(1)
    session.cookies.save()

    return session

def get_input():
    global id
    id = E1.get()
    root_window.destroy()

def cookie_analyse(session):
    # 这里参考了https://blog.csdn.net/qq_38316655/article/details/121190002
    cookies_dict = requests.utils.dict_from_cookiejar(session.cookies)

    session = requests.Session()
    response = session.get('https://api.bilibili.com/x/web-interface/history/cursor', cookies=cookies_dict, headers=headers)

    history_list = []
    cur_list = response.json()['data']['list']
    while cur_list:
        view_at = cur_list[0].get('view_at')
        strftime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(view_at))
        title = cur_list[0].get('title')
        #print(strftime, title)
        history_list += cur_list
        cursor = response.json()['data']['cursor']
        url = 'https://api.bilibili.com/x/web-interface/history/cursor?max={}&view_at={}&business=archive'.format(cursor['max'], cursor['view_at'])
        response = session.get(url, cookies=cookies_dict, headers=headers)
        cur_list = response.json()['data']['list']
    print('正在生成历史观看报告')

    df_history = pd.DataFrame(history_list)
    strftime = time.strftime('%Y-%m-%d', time.localtime())
    fpath = os.path.join(os.getcwd(), f'bili_history_{id}_{strftime}.xlsx')
    df_history.to_excel(fpath, index=False)
    client = Client(base_url='https://dav.jianguoyun.com/dav/',
                auth=('sherlockchiang@gmail.com', 'key')) # 此处请自行修改
    # client.upload_file(from_path=fpath, to_path='/benji/'+f'bili_history_{id}_{strftime}.xlsx', overwrite=False)
    # 从包含bili_history的excel文件导入数据
    df = pd.DataFrame()
    df = df._append(pd.read_excel(fpath))
    
    # 数据预处理
    df.drop_duplicates(inplace=True)
    df = df.astype({'tag_name': 'string', 'author_name': 'string'})
    df['date'] = pd.to_datetime(df['view_at'],unit='s',origin=pd.Timestamp('1970-01-01 08:00:00'))
    df['date'] = df['date'].dt.strftime("%Y-%m-%d")
    df = df.fillna({"tag_name":"无"})

    category = {
    '动画': ['MAD·AMV', 'MMD·3D', '综合', '短片·手书·配音', '手办·模玩', '特摄', '动漫杂谈'],
    '鬼畜': ['鬼畜调教', '音MAD', '人力VOCALOID', '鬼畜剧场', '教程演示'],
    '舞蹈': ['宅舞', '舞蹈综合', '舞蹈教程', '街舞', '明星舞蹈', '中国舞', '国风舞蹈', '手势·网红舞'],
    '娱乐': ['综艺', '明星综合', '娱乐杂谈','粉丝创作'],
    '科技': ['数码', '软件应用', '计算机技术', '科工机械', '极客DIY'],
    '美食': ['美食制作', '美食侦探', '美食测评', '田园美食', '美食记录'],
    '汽车': ['汽车生活', '赛车','改装玩车','新能源车','房车','摩托车','购车攻略'],
    '运动': ['篮球','足球','健身', '竞技体育', '运动文化', '运动综合'],
    '游戏': ['单机游戏', '网络游戏', '手机游戏', '电子竞技', '桌游棋牌', '音游', 'GMV', 'Mugen', '游戏赛事'],
    '音乐': ['音乐综合', '音乐现场', '演奏', '翻唱', 'MV', 'VOCALOID·UTAU', '电音', '原创音乐', '乐评盘点', '音乐教学', '说唱'],
    '影视': ['小剧场', '影视杂谈', '影视剪辑', '预告·资讯'],
    '知识': ['科学科普', '社科·法律·心理', '人文历史', '财经商业', '校园学习', '职业职场', '设计·创意', '野生技能协会'],
    '资讯': ['热点','环球','社会','综合'],
    '生活': ['搞笑','亲子','出行','三农','家居房产','手工','绘画','日常'],
    '时尚': ['美妆护肤', '穿搭', '时尚潮流', '仿妆cos'],
    '动物圈': ['喵星人', '汪星人', '野生动物', '爬宠', '大熊猫', '动物综合', '小宠异宠', '动物二创'],
    '番剧': ['资讯', '官方延伸','连载动画','完结动画', '新番时间表','番剧索引'],
    '电影': ['其他国家', '欧美电影', '日本电影', '国产电影'],
    '电视剧': ['国产剧', '海外剧'],
    '纪录片': ['人文·历史', '科学·探索·自然', '军事', '社会·美食·旅行'],
    '国创': ['国产动画', '国产原创相关', '布袋戏', '资讯', '动态漫·广播剧','新番时间表','国产动画索引'],
    '综艺': ['免费','大会员'],
    }

    tmp = []
    tag_lists = df['tag_name'].tolist()
    badge_lists = df['badge'].tolist()
    num = len(tag_lists)
    badge_false = pd.isnull(df["badge"])
    badge_false = badge_false.tolist()
    for i in range(num):
        if badge_false[i]:
            tmp.append(get_key(tag_lists[i],category))
        else:
            if '播' in str(badge_lists[i]):
                tmp.append('直播')
            else:
                tmp.append(badge_lists[i])

    df['category'] = tmp

    # 按序排序
    category_list = category.keys()
    cat_size_order = CategoricalDtype(
        category_list, 
        ordered=True
    )
    df['category'] = df['category'].astype(cat_size_order)

    df2 = pd.DataFrame() 
    df2 = df['category'].sort_values().value_counts(sort=False)

    # get index
    indexes = [0] * 110
    for i in range(num):
        indexes[get_index(tag_lists[i],tmp[i],list(category_list),category)-1] += 1

    workbook = xlwt.Workbook(encoding = 'utf-8')
    worksheet = workbook.add_sheet('sheet1')
    ii = 0
    for i in indexes:
        worksheet.write(0,ii,i)
        ii+=1
    tensor_filename = str(id) + time.strftime('_%Y%m%d_%H%M%S', time.localtime()) + '.xls'
    workbook.save(tensor_filename)
    client.upload_file(from_path=tensor_filename, to_path='/benji/'+tensor_filename, overwrite=False)

    os.remove(fpath)
    os.remove('bzcookies.txt')

    df2 = df2.sort_values()
    colors = cm.RdYlGn(linspace(0,1,len(df2)))
    df2.plot(kind='barh', color=colors) 
    plt.title('您近三个月中的b站浏览视频类型分析')
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.show() 

if __name__ == '__main__':
    root_window =tk.Tk()
    root_window.attributes('-topmost', 1)
    root_window.title('实验程序')

    screenWidth = root_window.winfo_screenwidth() 
    screenHeight = root_window.winfo_screenheight()
    width = 300
    height = 100
    left = (screenWidth - width) / 2
    top = (screenHeight - height) / 2

    root_window.geometry("%dx%d+%d+%d" % (width, height, left, top))

    L1 = tk.Label(root_window, text="请输入您的被试编号/手机号")
    L1.pack()
    E1 = tk.Entry(root_window, bd =5)
    E1.pack()
    confirm_button = tk.Button(root_window, text="确认输入", command=get_input)
    confirm_button.pack()
    root_window.mainloop()

    webbrowser.open('https://www.wjx.cn/vm/Y5kqFOX.aspx')
    
    session = bzlogin()
    if session == '':
        print('请重新运行！')
    else:
        cookie_analyse(session)
