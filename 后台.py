#-*- coding: utf-8 -*-
from flask import Flask, request, render_template, jsonify, json,send_file,make_response,url_for,redirect
from sqlalchemy import text
from sqlalchemy import or_,and_
from sqlalchemy.sql.expression import func
from flask_sqlalchemy  import SQLAlchemy
from flask_paginate import Pagination,get_page_parameter
from sqlalchemy.orm import sessionmaker
import matplotlib.pyplot as plt
import matplotlib
import numpy as np 
from io import BytesIO
import pymysql
import random
import jieba
from collections import Counter
from scipy.misc import imread
import jieba.analyse as analyse
from wordcloud import WordCloud
import numpy as np
import matplotlib.image as img
import time
import os
import pymysql
from werkzeug.utils import secure_filename
from werkzeug.utils import redirect
import uuid
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['font.family']='sans-serif'
pymysql.install_as_MySQLdb()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost:3306/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
db = SQLAlchemy(app)
class session(db.Model):
      __tablename__ = 'legal_instrument'
      ID = db.Column(db.String(45), primary_key = True)
      title = db.Column(db.String(100))  #标题
      region = db.Column(db.String(100)) #地区
      court = db.Column(db.String(100))  #法院
      document_Type = db.Column(db.String(100)) #文书类型
      year = db.Column(db.String(100))  #年份
      document_number = db.Column(db.String(100))  #文书编号
      information_people = db.Column(db.String(100))  #当事人
      text_part = db.Column(db.String(100))  #正文
      referee_part = db.Column(db.String(100))  #裁判部分
      other = db.Column(db.String(100))  #其他
      keyword = db.Column(db.VARCHAR(300))  #关键字

@app.route('/',methods=['POST','GET'])
def menu():
      return render_template('主页.html')

@app.route('/法律要素检索',methods=['POST','GET'])
def search():
      return render_template('检索页面.html')

@app.route('/法律要素检索/keyword',methods=['POST','GET'])
def keyword():
      keyword=request.form['keyword']
      result = session.query.filter(session.keyword.like('%'+ keyword +'%')).all()
      court = session.query.with_entities(session.court).distinct().all()
      region = session.query.with_entities(session.region).distinct().all()
      document_Type = session.query.with_entities(session.document_Type).distinct().all()
      '''
      #result = session.query.filter(session.keyword.like('%'+ '离婚' +'%')).all()
      per_page=10
      total=session.query.filter(session.keyword.like('%'+ keyword +'%')).count()
      #total=len(result)
      page=request.args.get(get_page_parameter(),type=int,default=1)
      start=(page-1)*per_page
      end=start+per_page
      pagination=Pagination(bs_version=3,page=page,total=total)
      result = session.query.filter(session.keyword.like('%'+ keyword +'%')).slice(start,end)
      '''
      #if not result :
            #return render_template('index.html',dT="error")
      return render_template('检索内容展示.html',court=court,region=region,document_Type=document_Type,result=result)

@app.route('/法律要素检索/<court1>',methods=['POST','GET'])
def court1(court1):
      result = session.query.filter(or_(session.court==court1,session.region==court1,session.document_Type==court1)).all()
      court = session.query.with_entities(session.court).distinct().all()
      region = session.query.with_entities(session.region).distinct().all()
      document_Type = session.query.with_entities(session.document_Type).distinct().all()
      return render_template('检索内容展示.html',court=court,region=region,document_Type=document_Type,result=result)

@app.route('/法律要素检索/文本展示/<title>',methods=['POST','GET'])
def title(title):
      result = session.query.filter(session.title==title).first()
      return render_template('文本展示.html',result=result)

@app.route('/法律案情统计分析',methods=['GET', 'POST'])
def count():
      Court = session.query.with_entities(session.court).distinct().all()
      Region = session.query.with_entities(session.region).distinct().all()
      document_Type = session.query.with_entities(session.document_Type).distinct().all()
      '''
      number = np.arange(8)
      for i in range(8):
            result = session.query.filter(session.document_Type==document_Type[i].document_Type).count()
            number[i]=result
      plt.style.use("ggplot")
      # 创建一个点数为 8 x 6 的窗口, 并设置分辨率为 80像素/每英寸 
      plt.figure(figsize=(25, 20), dpi=500) 
      # 再创建一个规格为 1 x 1 的子图 
      plt.subplot(1, 1, 1) 
      # 柱子总数
      labels = '民事判决书', '民事裁定书', '执行裁定书', '刑事裁定书', '刑事判决书', '行政裁定书', '刑事附带民事裁定书', '刑事附带民事判决书'
      sizes = [number[0]/351,number[1]/351,number[2]/351,number[3]/351,number[4]/351,number[5]/351,number[6]/351,number[7]/351] 
      plt.pie(sizes,autopct='%1.1f%%',shadow=False,startangle=90,textprops={'fontsize':30, 'color':'k'},counterclock = False) #startangle表示饼图的起始角度
      plt.legend()
      plt.savefig("static/"+"案件类型统计1.jpg")     
      '''
      return render_template('统计.html',court=Court,region=Region,document_Type=document_Type)

@app.route('/法律案情统计分析/<DT>',methods=['POST','GET'])
def DT(DT):
      Court = session.query.with_entities(session.court).distinct().all()
      Region = session.query.with_entities(session.region).distinct().all()
      document_Type = session.query.with_entities(session.document_Type).distinct().all()
      results = session.query.filter(DT==session.document_Type).all()
      if not results:
            return render_template('词云统计.html',court=Court,region=Region,document_Type=document_Type)
      num=random.randint(0,10000)
      H='关键字/'
      char_txt=H+str(num)+".txt"

      for row in results[0].keyword:
            fname1=row[0]
            #print(fname1)    
            m=open(char_txt,'a')
            m.write(str(fname1))
      santi_text = open(char_txt,'rb').read()
      fe='|'.join(jieba.cut(santi_text))
      santi_words = [x for x in jieba.cut(fe) if len(x) >= 2]
      jieba.disable_parallel()
      c = Counter(santi_words).most_common(1000)
      f=open(char_txt,"w")
      word=['']
      for word in c:
            if word[0].isdigit():
                  del word
            else:
                  f.write(str(word))
      f.close()
      

      m=open(char_txt,'r').read()
      #词云制作

      font='HYQiHei-55J.ttf'                  #选择字体路径，这里使用了黑体
      color_mask = imread("photo.jpg")        #读取模板图片，这里使用了一张五角星图片
      cloud = WordCloud(font_path=font,background_color='white',mask=color_mask,max_words=100,max_font_size=50,width=5000,height=5000)#设置词云参数，字体，模板，背景白色，最大词量100个，最大字体尺寸100
      #word_cloud = cloud.generate(fe)  
      word_cloud2=cloud.generate(str(m))              # 产生词云数据 word_cloud
      # wcould="分词词云_"
      # cy=wcould+str(num)+".jpg"
      # word_cloud.to_file(cy)                                           #词云保存为图片w_cloud.jpg
      #print ("词云成功...")
      wcould2="词云"
      img=wcould2+".jpg"
      l='static/keyword'
      word_cloud2.to_file(l+'/'+img)
      return render_template('词云统计.html',court=Court,region=Region,document_Type=document_Type,val1=time.time())

@app.route('/法律案情统计分析/涉案人员统计',methods=['POST','GET'])
def keyword1():
      keyword=request.form['keyword1']
      Court = session.query.with_entities(session.court).distinct().all()
      Region = session.query.with_entities(session.region).distinct().all()
      document_Type = session.query.with_entities(session.document_Type).distinct().all()
      number = np.arange(8)
      for i in range(8):
            result = session.query.filter(and_(session.information_people.like('%'+ keyword +'%'),session.document_Type==document_Type[i].document_Type)).count()
            number[i]=result
      font = {'family' : 'sans-serif','weight' : 'normal','size' : 23}
      print (plt.style.available)
      plt.style.use("ggplot")
      # 创建一个点数为 8 x 6 的窗口, 并设置分辨率为 80像素/每英寸 
      plt.figure(figsize=(25, 20), dpi=500) 
      # 再创建一个规格为 1 x 1 的子图 
      plt.subplot(1, 1, 1) 
      # 柱子总数
      N = 8 
      # 包含每个柱子对应值的序列
      values = number
      # 包含每个柱子下标的序列 
      index = np.arange(N) 
      # 柱子的宽度 
      width = 0.35 
      # 绘制柱状图, 每根柱子的颜色为紫罗兰色 
      p2 = plt.bar(index, values, tick_label=number,label="rainfall",color="#87CEFA") 
      # 设置横轴标签 
      plt.xlabel('案件类型',font) 
      # 设置纵轴标签 
      plt.ylabel('数量 (个)',font) 
      # 添加标题 
      plt.title('"'+keyword+'"'+'所对应的案件类型数量直方图',fontsize=50,color="purple") 
      # 添加纵横轴的刻度 
      plt.xticks(index, ('民事判决书', '民事裁定书', '执行裁定书', '刑事裁定书', '刑事判决书', '行政裁定书', '刑事附带民事裁定书', '刑事附带民事判决书'),fontsize="16")
      plt.yticks(np.arange(0, max(number)+5, int((max(number)+5)/10+1)),fontsize=23) 
      '''
      for rect in p2: 
            height = rect.get_height() 
            plt.text(rect.get_x() + rect.get_width() / 2, height+1, str(height), ha="center", va="bottom",size=20)
      '''
      # 添加图例 
      plt.savefig("static/统计/"+"统计.jpg")
      plt.close()
      return render_template('关键字统计.html',court=Court,region=Region,document_Type=document_Type,val1=time.time())

@app.route('/法律案情统计分析/地区统计/<region>',methods=['POST','GET'])
def region(region):
      Court = session.query.with_entities(session.court).distinct().all()
      Region = session.query.with_entities(session.region).distinct().all()
      document_Type = session.query.with_entities(session.document_Type).distinct().all()
      number = np.arange(8)
      for i in range(8):
            result = session.query.filter(and_(session.region==region,session.document_Type==document_Type[i].document_Type)).count()
            number[i]=result
      font = {'family' : 'sans-serif','weight' : 'normal','size' : 23}
      plt.style.use("ggplot")
      # 创建一个点数为 8 x 6 的窗口, 并设置分辨率为 80像素/每英寸 
      plt.figure(figsize=(25, 20), dpi=500) 
      # 再创建一个规格为 1 x 1 的子图 
      plt.subplot(1, 1, 1) 
      # 柱子总数
      N = 8 
      # 包含每个柱子对应值的序列
      values = number
      # 包含每个柱子下标的序列 
      index = np.arange(N) 
      # 柱子的宽度 
      width = 0.35 
      # 绘制柱状图, 每根柱子的颜色为紫罗兰色 
      p2 = plt.bar(index, values, label="rainfall", color="#87CEFA",tick_label=number) 
      # 设置横轴标签 
      plt.xlabel('案件类型',font) 
      # 设置纵轴标签 
      plt.ylabel('数量 (个)',font) 
      # 添加标题 
      plt.title('"'+region+'"'+'所对应的案件类型数量直方图',fontsize=50,color="purple") 
      # 添加纵横轴的刻度 
      plt.xticks(index, ('民事判决书', '民事裁定书', '执行裁定书', '刑事裁定书', '刑事判决书', '行政裁定书', '刑事附带民事裁定书', '刑事附带民事判决书'),fontsize="16")
      plt.yticks(np.arange(0, max(number)+5, 1),fontsize=23) 
      '''
      for rect in p2: 
            height = rect.get_height() 
            plt.text(rect.get_x() + rect.get_width() / 2, height+1, str(height), ha="center", va="bottom",size=20)
      '''
      # 添加图例 
      plt.savefig("static/统计/"+"统计.jpg")
      plt.close()
      return render_template('地区统计.html',court=Court,region=Region,document_Type=document_Type,val1=time.time())
@app.route('/法律案情统计分析/法院统计/<court2>',methods=['POST','GET'])
def court2(court2):
      Court = session.query.with_entities(session.court).distinct().all()
      Region = session.query.with_entities(session.region).distinct().all()
      document_Type = session.query.with_entities(session.document_Type).distinct().all()
      number = np.arange(8)
      for i in range(8):
            result = session.query.filter(and_(session.court==court2,session.document_Type==document_Type[i].document_Type)).count()
            number[i]=result
      font = {'family' : 'sans-serif','weight' : 'normal','size' : 23}
      plt.style.use("ggplot")
      # 创建一个点数为 8 x 6 的窗口, 并设置分辨率为 80像素/每英寸 
      plt.figure(figsize=(25, 20), dpi=500, facecolor='y', edgecolor='g') 
      # 再创建一个规格为 1 x 1 的子图 
      plt.subplot(111) 
      # 柱子总数
      N = 8 
      # 包含每个柱子对应值的序列
      values = number
      # 包含每个柱子下标的序列 
      index = np.arange(N) 
      # 柱子的宽度 
      width = 0.35 
      # 绘制柱状图, 每根柱子的颜色为紫罗兰色 
      p2 = plt.bar(index, values, label="rainfall", color="#87CEFA",tick_label=number) 
      # 设置横轴标签 
      plt.xlabel('案件类型',font) 
      # 设置纵轴标签 
      plt.ylabel('数量 (个)',font) 
      # 添加标题 
      plt.title('"'+court2+'"'+'所对应的案件类型数量直方图',fontsize=50,color="purple") 
      # 添加纵横轴的刻度 
      plt.xticks(index, ('民事判决书', '民事裁定书', '执行裁定书', '刑事裁定书', '刑事判决书', '行政裁定书', '刑事附带民事裁定书', '刑事附带民事判决书'),fontsize="16")
      plt.yticks(np.arange(0, max(number)+5, 1),fontsize=23)
      '''
      for rect in p2: 
            height = rect.get_height() 
            plt.text(rect.get_x() + rect.get_width() / 2, height+1, str(height), ha="center", va="bottom",size=20)
      '''
      plt.savefig("static/统计/"+"统计.jpg")
      plt.close()
      return render_template('法院统计.html',court=Court,region=Region,document_Type=document_Type,val1=time.time())

@app.route('/相似案件推荐',methods=['GET', 'POST'])
def like():
      return render_template('相似案件推荐首页.html')

@app.route('/相似案件推荐/keyword',methods=['POST','GET'])
def type():
     keyword1=request.form['keyword']
     region=request.form['region']
     des=request.form['des']
     print(keyword1)
     print(region)
     #print(des)
     result = session.query.filter(session.document_Type.like('%'+keyword1+'%')).filter(session.region.like('%'+region+'%')).all()
     
     
     if not result :
            return render_template('无相似案件推荐.html',result=result)
     return render_template('相似案件推荐文本展示.html',result=result)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/后台管理')
def houtai():
    return render_template('houtai.html')

@app.route('/后台管理/user')
def user():
    return render_template('user.html')

@app.route('/后台管理/anjian')
def anjian():
    return render_template('anjian.html')

@app.route('/后台管理/import_file',methods=['GET','POST'])
def import_file():
    slash = "\\"
    UPLOAD_FOLDER = "static/upload"
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    if request.method =='POST':
        #获取post过来的文件名称，从name=file参数中获取
        file = request.files['file']
        if file:
            # secure_filename方法会去掉文件名中的中文
            filename = secure_filename(file.filename)
            #因为上次的文件可能有重名，因此使用uuid保存文件
            file_name = filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],file_name))
            base_path = os.getcwd()
            file_path = base_path + slash + app.config['UPLOAD_FOLDER'] + slash + file_name
            print(file_path)
    """
    if request.method=='GET':
        return render_template('import_file.html')
    else:
        data_1 = request.form.get('Filepath')
        data_2 = request.form.get('Filepath_1')
    print(data_1)
    print(data_2)
    """

    for info in os.listdir("C:/Users/admin/Desktop/法律服务平台/static/upload"): #(data_1)
        domain = os.path.abspath("C:/Users/admin/Desktop/法律服务平台/static/upload") #(data_1)
        file_string = os.path.join(domain,info)
        read_data = open(file_string,'r',encoding='utf-8')
        char = "new_"
        char_txt = "C:/Users/admin/Desktop/法律服务平台/static/upload_mid/"+char+info+".json" #data_2+char+info+".json"
        write_data = open(char_txt,'w',encoding="gb18030")
        RB_buffer = read_data.read()
        oldlist = ['']
        json_dictory = {}


        oldlist = list(RB_buffer)

        #去除干扰项，保留index所指位置
        index = 1
        """
        while oldlist[index] == " ":
            index += 1
        """
        flag = index

        #print("****************001*******************")

        #取标题
        while oldlist[index] != "书":
            index += 1
        tmp = "".join(oldlist[flag:index+1])
        tmp = tmp.replace('\t','')
        tmp = tmp.replace(' ','')
        json_dictory["标题"] = tmp

        #print("***************002*******************")

        #去除干扰项，保留index所指位置
        #while oldlist[index] == " ":
        index += 1
        flag = index
        #取法院，文书标号等
        while oldlist[index] != '号':
            index += 1

        #细化分割
        sublist = oldlist[flag:index+1]
        index_1 = 0
        flag_1 = 0
        while sublist[index_1] != '市' and sublist[index_1] != '县' and sublist[index_1] != '旗':
            index_1 += 1
        tmp_0 = "".join(sublist[flag_1:index_1+1])
        tmp_0 = tmp_0.replace('\t','')
        tmp_0 = tmp_0.replace(' ','')
        while True:
            index_1 += 1
            if "".join(sublist[index_1:index_1+2]) in ["民事","刑事","行政","赔偿","执行"]:
                break
            if "".join(sublist[index_1:index_1+3]) in ["民 事","刑 事","行 政","赔 偿","执 行"]:
                break
        tmp_1 = "".join(sublist[flag_1:index_1])
        tmp_1 = tmp_1.replace('\t','')
        tmp_1 = tmp_1.replace(' ','')
        flag_1 = index_1
        while True:
            index_1 += 1
            if sublist[index_1] == '（' or sublist[index_1] == '(' or sublist[index_1] == '[':
                break
        tmp_2 = "".join(sublist[flag_1:index_1])
        tmp_2 = tmp_2.replace('\t','')
        tmp_2 = tmp_2.replace(' ','')
        flag_1 = index_1
        while True:
            index_1 += 1
            if sublist[index_1] == '）' or sublist[index_1] == ')' or sublist[index_1] == ']':
                break
        tmp_3 = "".join(sublist[flag_1+1:index_1])
        tmp_3 = tmp_3.replace('\t','')
        tmp_3 = tmp_3.replace(' ','')
        tmp_4 = "".join(sublist[flag_1:index+1])
        tmp_4 = tmp_4.replace('\t','')
        tmp_4 = tmp_4.replace(' ','')

        json_dictory["地区"] = tmp_0
        json_dictory["法院"] = tmp_1
        json_dictory["文书类型"] = tmp_2
        json_dictory["年份"] = tmp_3
        json_dictory["文书编号"] = tmp_4
        
        #tmp = "".join(oldlist[flag:index+1])
        #json_dictory["法院及文书编号"] = tmp

        #print("****************003******************")

        #取涉案人员信息
        flag = index+1
        while True:
            index += 1    
            if ("".join(oldlist[index:index+2])) == "本院":
                break
        tmp = "".join(oldlist[flag:index])
        tmp = tmp.replace('\t','')
        tmp = tmp.replace(' ','')
        json_dictory["涉案人员信息"] = tmp

        #print("****************004******************")

        """
        #正文
        flag = index
        while True:
            index += 1
            if ("".join(oldlist[index:index+2])) == "综上":
                if "综上，本院认定如下事实" in "".join(oldlist[index:index+20]):
                    break
        tmp = "".join(oldlist[flag:index])
        write_data.write(tmp)
        write_data.write("\n\n")
        """

        #print("*****************005*****************")

        #取涉案人员到判决依据之间的信息
        flag = index
        while index < len(oldlist):
            index += 1
            #if oldlist[index] == "依":
            if '依据' in "".join(oldlist[index:index+2]) or '依照' in "".join(oldlist[index:index+2]) or '根据' in "".join(oldlist[index:index+2]):
                if "《中华人民共和国" in "".join(oldlist[index:index+30]): 
                    if "判决如下" in "".join(oldlist[index:index+100]) or "裁定如下" in "".join(oldlist[index:index+100]):
                        break
        """
        while True:
            index += 1
            if "".join(oldlist[index:index+2]) == '依据' or "".join(oldlist[index:index+2]) == '依照':
                if "《中华人民共和国" in "".join(oldlist[index:index+30]) and ( "判决如下" in "".join(oldlist[index:index+50]) or "裁定如下" in "".join(oldlist[index:index+100])):
                    break
        """
        tmp = "".join(oldlist[flag:index])
        tmp = tmp.replace('\t','')
        tmp = tmp.replace(' ','')
        json_dictory["正文"] = tmp

        #print("****************006******************")

        #判决部分（含法律依据）
        flag = index
        label = 0
        while index < len(oldlist):
            index += 1
            if ("".join(oldlist[index:index+3])) == "审判长" or ("".join(oldlist[index:index+3])) == "审判员":
                break
            if ("".join(oldlist[index:index+5])) == "代理审判长" or ("".join(oldlist[index:index+5])) == "代理审判员":
                break
            if ("".join(oldlist[index:index+5])) == "审　判　长":
                break

                """
                elif ("".join(oldlist[index:index+6])) == "代理审判":
                    break 
                elif ("".join(oldlist[index:index+6])) == "审　判　":
                    break
                """
        tmp = "".join(oldlist[flag:index])
        tmp = tmp.replace('\t','')
        tmp = tmp.replace(' ','')
        json_dictory["判决部分"] = tmp

        #print("*****************007*****************")

        #其他
        flag = index
        while index<len(oldlist):
            index += 1
            if ("".join(oldlist[index:index+1])) == "，":
                break
        tmp = "".join(oldlist[flag:index])
        tmp = tmp.replace('\t','')
        tmp = tmp.replace(' ','')
        json_dictory["其他"] = tmp

        flag = index
        while index < len(oldlist):
            index += 1
        tmp = "".join(oldlist[flag:index+1])
        tmp = tmp.replace('\t','')
        tmp = tmp.replace(' ','')
        json_dictory["关键字"] = tmp

        #print(json_dictory)
        json.dump(json_dictory,write_data,ensure_ascii=False)

        #print("*****************008*****************")

        read_data.close()
        write_data.close()

    #连接数据库
    db=pymysql.connect(host='localhost',
                            user='root',
                            port=3306,
                            password='123456',
                            db='test',
                            charset='utf8')

    cursor = db.cursor()
    cursor.execute("SELECT VERSION()")
    data = cursor.fetchone()
    print("Database version : %s " % data) # 结果表明已经连接成功      

    num = 10
    #从文本文件中提取json数据
    for info in os.listdir("C:/Users/admin/Desktop/法律服务平台/static/upload_mid/"):
        domain = os.path.abspath("C:/Users/admin/Desktop/法律服务平台/static/upload_mid/")
        file_string = os.path.join(domain,info)
        print('...............')
        print(file_string)
        read_data = open(file_string,'r').read()
        if read_data=="":
            num+=1
            print(" read_data is empty")
        else:
            #if RB.startswith(u'\ufeff'):
            #RB = RB.encode('ANSI')[3:].decode('ANSI')
            RB_json = json.loads(read_data)         #RB_json为字典
            #print(type(RB_json))
            #print(RB_json)
            #print(read_data)
            
            result = (RB_json["标题"],RB_json["地区"],RB_json["法院"],RB_json["文书类型"],RB_json["年份"],RB_json["文书编号"],RB_json["涉案人员信息"],RB_json["正文"],RB_json["判决部分"],RB_json["其他"],RB_json["关键字"])
            inesrt_re = "insert into new_table1(标题,地区,法院,wenshutype,年份,文书编号,涉案人员信息,正文,判决部分,其他,关键字) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%result
            cursor.execute(inesrt_re)
            db.commit()
            print("success")
            num = num + 1
    cursor.close()
    db.close()

    return render_template('import_file.html')

if __name__ == '__main__':
      app.run(host='127.0.0.1', port = 8083, debug=True)