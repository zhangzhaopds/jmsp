from bs4 import BeautifulSoup
import requests
from django.http import HttpResponse
from  pymongo import MongoClient
from django.core.mail import EmailMessage
import json
import re
import random
import time
import os
from qiniu import Auth, put_file, etag, BucketManager
from django.shortcuts import render, get_object_or_404, get_list_or_404
import smtplib
from email.mime.text import MIMEText

# Create your views here.

def index(request):
    return render(request, 'unknown/index.html')

# 获取验证码： authCode
def authCode(request):
    loginName = request.POST.get('loginName', '')
    print(loginName)
    if re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', loginName):
        # 发送验证码
        i = 0
        num = 0
        while i < 4:
            n = random.randint(1, 9)
            i = i + 1
            num = n * 10 ** (4 - i) + num
        print("验证码为：{0}".format(num))
        message = '\n'.join([
            u'Your verification code：{0}'.format(num),
        ])
        # 写入数据到USERS表
        dir = 'mongodb://unknownadmin:unknown123456@ds051645.mlab.com:51645/unknown'
        USERS = MongoClient(dir).unknown.USERS
        result = USERS.find({'loginName': loginName})
        if result.count() > 0:
            # 老用户更新
            USERS.update({'loginName': loginName}, {'$set': {'authCode': '{0}'.format(num)}})
            print('老用户更新')
        else:
            data = {
                'loginName': loginName,
                'isActivate': False,
                'authCode': '{0}'.format(num),
                'joinTime': time.strftime('%Y/%m/%d %H:%M:%S %Z', time.localtime(time.time())),
                'userName': 'So What',
                'backgroundPicture': 'http://7xoz39.com1.z0.glb.clouddn.com/lvyevr_default_bgImage.JPG',
                'sex': '1', # 默认1 男， 2 女
                'phone': '',
                'avatar': 'http://7xoz39.com1.z0.glb.clouddn.com/default_avatar.png',
                'address': '',
                'profession': '',
                'description': 'Say something to introduce yourself',
                'lastLoginTime': '',
                'isLogin': False,
                'userID': 'vr' + str(int(time.time()))
            }
            # 新用户加入
            USERS.insert(data)
            print('新用户加入')
        print("将要发送邮件")

        _user = "736694109@qq.com"
        _pwd = "blzfqwgcyiwjbbej"
        _to = loginName

        msg = MIMEText(message)
        msg["Subject"] = "LvyeVR"
        msg["From"] = _user
        msg["To"] = _to

        try:
            s = smtplib.SMTP_SSL("smtp.qq.com", 465)
            s.login(_user, _pwd)
            s.sendmail(_user, _to, msg.as_string())
            s.quit()
            print("邮件发送成功")
            msg = {"isSuccess": True,
                   "msg": 'Verification code sent successfully'}
            return HttpResponse(json.dumps(msg), content_type='application/json')
        except smtplib.SMTPException:
            print("邮件发送异常")
            msg = {"isSuccess": False,
                   "msg": 'Verification code sent failure'}
            return HttpResponse(json.dumps(msg), content_type='application/json')
    else:
        msg = {"isSuccess": False,
               "msg": 'Email address is invalid'}
        return HttpResponse(json.dumps(msg), content_type='application/json')



# 注册/重置密码： loginName + authCode + password
def register(request):
    loginName = request.POST.get('loginName', '')
    code = request.POST.get('authCode', '')
    password = request.POST.get('password', '')

    if loginName == '' or code == '' or password == '':
        msg = {"isSuccess": False,
               "msg": 'Parameter is not correct'}
        return HttpResponse(json.dumps(msg), content_type='application/json')

    # USERS表
    dir = 'mongodb://unknownadmin:unknown123456@ds051645.mlab.com:51645/unknown'
    USERS = MongoClient(dir).unknown.USERS
    result = USERS.find({'loginName': loginName, 'authCode': code})
    if result.count() > 0:
        data = {
            'isActivate': True,
            'password': password,
            'authCode': ''
        }
        USERS.update({'loginName': loginName}, {'$set': data})
        msg = {"isSuccess": True,
               "msg": 'successful'}
        return HttpResponse(json.dumps(msg), content_type='application/json')
    else:
        msg = {"isSuccess": False,
               "msg": 'Login name or verification code is wrong'}
        return HttpResponse(json.dumps(msg), content_type='application/json')


# 登陆： loginName + password
def login(request):
    loginName = request.POST.get('loginName', '')
    password = request.POST.get('password', '')
    if loginName == '' and password == '':
        msg = {"isSuccess": False,
               "msg": 'Parameter is not correct'}
        return HttpResponse(json.dumps(msg), content_type='application/json')

    # USERS表
    dir = 'mongodb://unknownadmin:unknown123456@ds051645.mlab.com:51645/unknown'
    USERS = MongoClient(dir).unknown.USERS
    result = USERS.find({'loginName': loginName, 'password': password})
    if result.count() > 0:
        # 登陆成功： 更新登陆时间 登陆状态
        currentTime = time.strftime('%Y/%m/%d %H:%M:%S %Z', time.localtime(time.time()))
        USERS.update({'loginName': loginName},
                     {'$set': {'lastLoginTime': currentTime,
                               'isLogin': True}})
        user = USERS.find_one({'loginName': loginName, 'password': password})
        print(user)
        userInfo = {
            'userName': user['userName'],
            'backgroundPicture': user['backgroundPicture'],
            'sex': user['sex'],
            'phone': user['phone'],
            'avatar': user['avatar'],
            'address': user['address'],
            'profession': user['profession'],
            'description': user['description'],
            'joinTime': user['joinTime'],
            'loginName': user['loginName'],
            'lastLoginTime': user['lastLoginTime'],
            'isLogin': user['isLogin'],
            'userID': user['userID']
        }
        msg = {"isSuccess": True,
               'userInfo': userInfo,
               "msg": 'Login successfully'}
        return HttpResponse(json.dumps(msg), content_type='application/json')
    else:
        msg = {"isSuccess": False,
               "msg": 'Account or password is wrong'}
        return HttpResponse(json.dumps(msg), content_type='application/json')

# 退出登录: loginName + password
def logout(request):
    loginName = request.POST.get('loginName', '')
    password = request.POST.get('password', '')
    if loginName == '' and password == '':
        msg = {"isSuccess": False,
               "msg": 'Parameter is not correct'}
        return HttpResponse(json.dumps(msg), content_type='application/json')

    # USERS表
    dir = 'mongodb://unknownadmin:unknown123456@ds051645.mlab.com:51645/unknown'
    USERS = MongoClient(dir).unknown.USERS
    result = USERS.find({'loginName': loginName, 'password': password})
    if result.count() > 0:
        # 退出成功： 更新登陆状态
        USERS.update({'loginName': loginName},
                     {'$set': {'isLogin': False}})
        user = USERS.find_one({'loginName': loginName, 'password': password})
        print(user)
        msg = {"isSuccess": True,
               "msg": 'Logout successfully'}
        return HttpResponse(json.dumps(msg), content_type='application/json')
    else:
        msg = {"isSuccess": False,
               "msg": 'Account or password is wrong'}
        return HttpResponse(json.dumps(msg), content_type='application/json')

# 更新/获取用户信息：
# 必须：loginName + password
# 可选：userName、backgroundPicture、sex、phone、avatar、address、profession、description
def userInfo(request):
    loginName = request.POST.get('loginName', '')
    password = request.POST.get('password', '')
    if loginName == '' or password == '':
        msg = {"isSuccess": False,
               "msg": 'Parameter is not correct'}
        return HttpResponse(json.dumps(msg), content_type='application/json')

    # USERS表
    dir = 'mongodb://unknownadmin:unknown123456@ds051645.mlab.com:51645/unknown'
    USERS = MongoClient(dir).unknown.USERS
    result = USERS.find({'loginName': loginName, 'password': password})
    if result.count() > 0:
        # 账号密码验证成功
        data = {}
        if request.POST.get('userName', '') != '':
            data['userName'] = request.POST.get('userName', '')
        if request.POST.get('backgroundPicture', '') != '':
            data['backgroundPicture'] = request.POST.get('backgroundPicture', '')
        if request.POST.get('sex', '') != '':
            data['sex'] = request.POST.get('sex', '')
        if request.POST.get('phone', '') != '':
            data['phone'] = request.POST.get('phone', '')
        if request.POST.get('avatar', '') != '':
            data['avatar'] = request.POST.get('avatar', '')
        if request.POST.get('address', '') != '':
            data['address'] = request.POST.get('address', '')
        if request.POST.get('profession', '') != '':
            data['profession'] = request.POST.get('profession', '')
        if request.POST.get('description', '') != '':
            data['description'] = request.POST.get('description', '')
        print('更新的数据：')
        print(data)
        if data != {}:
            USERS.update({'loginName': loginName, 'password': password},
                         {'$set': data})
        user = USERS.find_one({'loginName': loginName, 'password': password})
        print('用户最新数据：')
        print(user)
        userInfo = {
            'userName': user['userName'],
            'backgroundPicture': user['backgroundPicture'],
            'sex': user['sex'],
            'phone': user['phone'],
            'avatar': user['avatar'],
            'address': user['address'],
            'profession': user['profession'],
            'description': user['description'],
            'joinTime': user['joinTime'],
            'loginName': user['loginName'],
            'lastLoginTime': user['lastLoginTime'],
            'isLogin': user['isLogin'],
            'userID': user['userID']
        }
        msg = {"isSuccess": True,
               'userInfo': userInfo,
               "msg": 'Update successfully'}
        return HttpResponse(json.dumps(msg), content_type='application/json')
    else:
        # 账号密码验证失败
        msg = {"isSuccess": False,
               "msg": 'Account or password is wrong'}
        return HttpResponse(json.dumps(msg), content_type='application/json')

# 照片上传 POST: loginName + password + file
# 可选 isPanorama: 等于"1"为true,其他均为false
# isAavatar: "1" 用户头像更新
# isUserBgImage: "1" 用户背景照片

def upload(request):
    print("图片上传upload")
    loginName = request.POST.get('loginName', None)
    password = request.POST.get('password', None)
    myFile = request.FILES.get("file", None)
    isPanorama = request.POST.get('isPanorama', False)
    isAavatar = request.POST.get('isAavatar', False)
    isUserBgImage = request.POST.get('isUserBgImage', False)
    if loginName == None or password == None or myFile == None:
        msg = {"isSuccess": False,
               "msg": 'Parameter is not correct'}
        return HttpResponse(json.dumps(msg), content_type='application/json')

    # USERS表
    dir = 'mongodb://unknownadmin:unknown123456@ds051645.mlab.com:51645/unknown'
    USERS = MongoClient(dir).unknown.USERS
    result = USERS.find({'loginName': loginName, 'password': password})
    if result.count() == 0:
        msg = {"isSuccess": False,
               "msg": 'Account or password is wrong'}
        return HttpResponse(json.dumps(msg), content_type='application/json')
    user = USERS.find_one({'loginName': loginName, 'password': password})
    userID = user['userID']

    if isPanorama != False and isPanorama == "1":
        isPanorama = True
    else:
        isPanorama = False

    if isAavatar != False and isAavatar == "1":
        isAavatar = True
    else:
        isAavatar = False

    if isUserBgImage != False and isUserBgImage == "1":
        isUserBgImage = True
    else:
        isUserBgImage = False

    # 上传到七牛
    qiniu = updateImageToQiNiu(userID=userID, file=myFile)

    updateDate = qiniu[1]
    avatar = qiniu[0]
    postDate = str(int(time.time()))

    if isAavatar or isUserBgImage:
        if isAavatar:
            print("头像上传")
            # USERS表
            dir = 'mongodb://unknownadmin:unknown123456@ds051645.mlab.com:51645/unknown'
            USERS = MongoClient(dir).unknown.USERS
            USERS.update({'loginName': loginName, 'password': password},
                         {'$set': {'avatar': avatar}})
            msg = {"isSuccess": True,
                   'data': {
                       "userID": userID,
                       "url": avatar,
                   },
                   "msg": 'Upload successfully'}
            return HttpResponse(json.dumps(msg), content_type='application/json')
        else:
            print("背景照片上传")
            # USERS表
            dir = 'mongodb://unknownadmin:unknown123456@ds051645.mlab.com:51645/unknown'
            USERS = MongoClient(dir).unknown.USERS
            USERS.update({'loginName': loginName, 'password': password},
                         {'$set': {'backgroundPicture': avatar}})
            msg = {"isSuccess": True,
                   'data': {
                       "userID": userID,
                       "url": avatar,
                   },
                   "msg": 'Upload successfully'}
            return HttpResponse(json.dumps(msg), content_type='application/json')

    else:
        # 写入数据库表PHOTOS
        print("普通照片上传")
        imgInfo = addImageToPHOTOS(userID=userID, postDate=postDate, updateDate=updateDate, url=avatar, isPanorama=isPanorama)
        msg = {"isSuccess": True,
           'data': {
               "userID": userID,
               "postDate": postDate,
               "updateDate": updateDate,
               "url": avatar,
               'tempURL': avatar + "?imageView2/0/w/500",
               "isPanorama": isPanorama,
               'width': imgInfo['width'],
               'height': imgInfo['height'],
               'size': imgInfo['size'],
               'format': imgInfo['format'],
           },
           "msg": 'Upload successfully'}
        return HttpResponse(json.dumps(msg), content_type='application/json')



# 新增照片到表PHOTOS
def addImageToPHOTOS(userID, postDate, updateDate, url, isPanorama):
    print("---开始新增照片到表PHOTOS---")
    print("userID=" + userID, "postDate=" + postDate, "updateDate=" + updateDate, "url=" + url, "isPanorama=" + str(isPanorama))
    # 写入数据到PHOTOS表
    dir = 'mongodb://unknownadmin:unknown123456@ds051645.mlab.com:51645/unknown'
    PHOTOS = MongoClient(dir).unknown.PHOTOS
    res = requests.get(url + '?imageInfo')
    try:
        data = {
            "userID": userID,
            "postDate": postDate,
            "updateDate": updateDate,
            "url": url,
            'tempURL': url + "?imageView2/0/w/500",
            "isPanorama": isPanorama,
            'width': res.json()['width'],
            'height': res.json()['height'],
            'size': res.json()['size'],
            'format': res.json()['format'],
            "thumbupCount": 0
        }
    except:
        data = {
            "userID": userID,
            "postDate": postDate,
            "updateDate": updateDate,
            "url": url,
            'tempURL': url + "?imageView2/0/w/500",
            "isPanorama": isPanorama,
            'width': 0,
            'height': 0,
            'size': 0,
            'format': '',
            "thumbupCount": 0
        }
    PHOTOS.insert(data)
    print("----PHOTOS表写入数据结束-----")
    return data

# 图片上传到七牛
def updateImageToQiNiu(userID, file):
    print("----开始图片上传到七牛----")
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(BASE_DIR, 'unknown/')
    localfile = os.path.join(path, file.name)
    destination = open(localfile, 'wb+')  # 打开特定的文件进行二进制的写操作
    for chunk in file.chunks():  # 分块写入文件
        destination.write(chunk)
    destination.close()

    # 密钥
    access_key = 'CfEmsrk8eSKQtZ8OY5NHUPWJ3VKfoGHEP1fzYStf'
    secretKey = 'cdxPmlWXpkAGUeGRZkhocGMYfVnqdEa-otwer9Ma'

    # 鉴权
    a = Auth(access_key, secret_key=secretKey)

    # 空间名
    bucket_name = 'jmspvu'

    # 文件保存名
    now = int(time.time())
    key = "vr/" + userID + "/" + str(now)

    # 不能出现 http://  或者 https:// 字样，否则heroku中出错
    base = 'opu0gas3t.bkt.clouddn.com/'

    # 生成上传 Token，可以指定过期时间等
    token = a.upload_token(bucket_name, key, 3600)

    ret, info = put_file(token, key, localfile)
    assert ret['key'] == key
    assert ret['hash'] == etag(localfile)

    avatar = 'http://' + base + key
    os.remove(localfile)
    print('上传完毕' + avatar)
    return (avatar, str(now))

# 删除照片
# 必要：loginName password
# 条件： updateDate
def deletePhoto(request):
    print("删除照片")
    loginName = request.POST.get('loginName', None)
    password = request.POST.get('password', None)
    updateDate = request.POST.get('updateDate', None)
    userID = request.POST.get('userID', None)
    if loginName == None or password == None or userID == None or updateDate == None:
        msg = {"isSuccess": False,
               "msg": 'Parameter is not correct'}
        return HttpResponse(json.dumps(msg), content_type='application/json')

    # 身份验证
    print("数据库USERS连接")
    dir = 'mongodb://unknownadmin:unknown123456@ds051645.mlab.com:51645/unknown'
    USERS = MongoClient(dir).unknown.USERS
    print("查询")
    result = USERS.find({'loginName': loginName, 'password': password})
    print("用户验证结束", result)
    if result.count() == 0:
        msg = {"isSuccess": False,
               "msg": 'Account or password is wrong'}
        return HttpResponse(json.dumps(msg), content_type='application/json')

    print("数据库PHOTOS连接")
    # 图片查找
    dir = 'mongodb://unknownadmin:unknown123456@ds051645.mlab.com:51645/unknown'
    PHOTOS = MongoClient(dir).unknown.PHOTOS
    PHOTOS.remove({"updateDate": updateDate})

    print("照片数据库删除")

    # 七牛删除
    access_key = 'CfEmsrk8eSKQtZ8OY5NHUPWJ3VKfoGHEP1fzYStf'
    secretKey = 'cdxPmlWXpkAGUeGRZkhocGMYfVnqdEa-otwer9Ma'
    # 初始化Auth状态
    q = Auth(access_key, secretKey)
    # 初始化BucketManager
    bucket = BucketManager(q)
    # 你要测试的空间， 并且这个key在你空间中存在
    bucket_name = 'jmspvu'
    key = 'vr/' + userID + "/" + str(updateDate)
    print(key)
    # 删除bucket_name 中的文件 key
    ret, info = bucket.delete(bucket_name, key)
    print(info)
    print(ret)
    if ret != None:
        msg = {"isSuccess": True,
           "msg": 'successful'}
        print('删除结果', msg)
        return HttpResponse(json.dumps(msg), content_type='application/json')
    else:
        msg = {"isSuccess": False,
               "msg": 'fail'}
        print('删除结果', msg)
        return HttpResponse(json.dumps(msg), content_type='application/json')



# 查询图片
# 条件： userID    isPanorama   postDate    updateDate
# userID + isShowThumbup    同时存在（isShowThumbup == "1"）时，显示userID对应用户是否对照片点赞
def userPhotos(request):
    print("获取用户照片")
    userID = request.POST.get('userID', None)
    isPanorama = request.POST.get('isPanorama', None)
    postDate = request.POST.get('postDate', None)
    updateDate = request.POST.get('updateDate', None)
    page = request.POST.get('page', 0)

    isShowThumbup = request.POST.get('isShowThumbup', None)

    #身份验证
    dir = 'mongodb://unknownadmin:unknown123456@ds051645.mlab.com:51645/unknown'
    USERS = MongoClient(dir).unknown.USERS

    # 图片
    PHOTOS = MongoClient(dir).unknown.PHOTOS

    # 点赞
    THUMBUP = MongoClient(dir).unknown.THUMBUP

    # 查询条件
    conditions = {}

    # 显示userID对应用户是否对照片点赞
    isShow = False

    # userID不为空 + isShowThumbup为空 = userID作为筛选条件
    if userID != None:
        if isShowThumbup != None:
            if isShowThumbup == "1":
                isShow = True
        else:
            conditions['userID'] = userID
    if isPanorama != None:
        if isPanorama == "1":
            conditions['isPanorama'] = True
        else:
            conditions['isPanorama'] = False
    if postDate != None:
        conditions['postDate'] = postDate
    if updateDate != None:
        conditions['updateDate'] = updateDate

    page = int(page)
    num = 20

    print('查询条件：', conditions)

    photos = PHOTOS.find(conditions)
    if photos != None:
        # 倒序
        photos = list(photos)
        photos.reverse()
    else:
        print("无数据")
        msg = {"isSuccess": False,
               "msg": 'no data'}
        return HttpResponse(json.dumps(msg), content_type='application/json')
    if len(photos) > 0:
        datas = []
        sum = len(photos)
        cur = num * (page + 1)
        sumPages = 0
        if len(photos) % num > 0:
            sumPages = len(photos) // num + 1
        else:
            sumPages = len(photos) // num

        print("数据" , str(len(photos)), str(sumPages) , str(page + 1))
        if page + 1 > sumPages:
            print("页码超出")
            msg = {"isSuccess": False,
                   "msg": 'no data'}
            return HttpResponse(json.dumps(msg), content_type='application/json')

        if cur > sum:
            cur = sum
        for i in range(page * num, cur):
            photo = photos[i]
            photo.pop('_id')
            dic = json.loads(json.dumps(photo))
            user = USERS.find_one({'userID': photo['userID']})
            dic['userAvatar'] = user['avatar']
            dic['userName'] = user['userName']
            dic['userBgImage'] = user['backgroundPicture']
            dic['userDesc'] = user['description']

            # 点赞数
            thumup = THUMBUP.find({'updateDate': photo['updateDate']})
            isCurThumbup = False
            if isShow:
                isCurThumbup = THUMBUP.find_one({'userID': userID, 'updateDate': photo['updateDate']}) != None

            # 当前用户是否点在此照片
            dic['isCurThumbup'] = isCurThumbup
            if thumup == None:
                dic['thumbupCount'] = 0
            else:
                dic['thumbupCount'] = thumup.count()

            datas.append(dic)
        msg = {"isSuccess": True,
               'totalPages': sumPages,
                'currentPage': page + 1,
               "data":  datas,
               "msg": 'successful'}
        print('查询结果', msg)
        return HttpResponse(json.dumps(msg), content_type='application/json')
    else:
        print("无数据")
        msg = {"isSuccess": False,
               "msg": 'no data'}
        return HttpResponse(json.dumps(msg), content_type='application/json')



# 点赞查询
# updateDate  userID 二选一
def getThumbupCount():
    # 点赞表 THUMBUP
    dir = 'mongodb://unknownadmin:unknown123456@ds051645.mlab.com:51645/unknown'
    THUMBUP = MongoClient(dir).unknown.THUMBUP
    result = THUMBUP.find()
    return result.count()

def getThumbupCountByUserID(userID):
    # 点赞表 THUMBUP
    dir = 'mongodb://unknownadmin:unknown123456@ds051645.mlab.com:51645/unknown'
    THUMBUP = MongoClient(dir).unknown.THUMBUP
    result = THUMBUP.find({'userID': userID})
    #THUMBUP.insert({'updateDate': updateDate, 'userID': userID})
    data = []
    if result.count() > 0:
        for res in iter(result):
            data.append(res['updateDate'])
    print("查询userID结果", data)
    return data

def getThumbupCountByUpdateDate(updateDate):
    data = []
    # 点赞表 THUMBUP
    dir = 'mongodb://unknownadmin:unknown123456@ds051645.mlab.com:51645/unknown'
    THUMBUP = MongoClient(dir).unknown.THUMBUP
    result = THUMBUP.find({'updateDate': updateDate})
    if result.count() > 0:
        for res in iter(result):
            data.append(res['userID'])
    print("查询updateDate结果", data)
    return data

# 是否点赞
def isCurrentUserThumbup(updateDate, userID):
    # 点赞表 THUMBUP
    dir = 'mongodb://unknownadmin:unknown123456@ds051645.mlab.com:51645/unknown'
    THUMBUP = MongoClient(dir).unknown.THUMBUP
    result = THUMBUP.find_one({'userID': userID, 'updateDate': updateDate})
    return result.count() > 0


# 图片点赞/取消点赞
# 必要： updateDate  userID
def doThumbup(request):
    print("-----点赞doThumbup-----")
    updateDate = request.POST.get('updateDate', None)
    userID = request.POST.get('userID', None)
    if updateDate == None or userID == None:
        msg = {"isSuccess": False,
               "msg": 'Parameter is not correct'}
        return HttpResponse(json.dumps(msg), content_type='application/json')

    # 点赞表 THUMBUP
    dir = 'mongodb://unknownadmin:unknown123456@ds051645.mlab.com:51645/unknown'
    THUMBUP = MongoClient(dir).unknown.THUMBUP

    result = THUMBUP.find_one({'updateDate': updateDate, 'userID': userID})
    if result != None:
        THUMBUP.remove({'updateDate': updateDate, 'userID': userID})
        res = THUMBUP.find()
        msg = {"isSuccess": True,
               "data": {
                   'thumbupCount': res.count(),
                   'isCurrentUserThumbup': result == None
               },
               "msg": 'successful'}
        print('取消点赞', msg)
        return HttpResponse(json.dumps(msg), content_type='application/json')
    else:
        THUMBUP.insert({'updateDate': updateDate, 'userID': userID})
        res = THUMBUP.find()
        msg = {"isSuccess": True,
               "data": {
                   'thumbupCount': res.count(),
                   'isCurrentUserThumbup': result == None
               },
               "msg": 'successful'}
        print("点赞", msg)
        return HttpResponse(json.dumps(msg), content_type='application/json')



# 主页背景照片
def homeBgImg(request):
    pexel = 'https://www.pexels.com'
    req = requests.get(pexel)
    soup = BeautifulSoup(req.text)
    bgImg = soup.find_all(name='style')
    sub = bgImg[0].string.split('(')
    large = pexel + sub[1].rstrip(');}@media ')
    small = pexel + sub[len(sub) - 1].rstrip(');}}')
    json_str = json.dumps({
        'homeBgImages': {'large': large,
                         'small': small}
    })
    return HttpResponse(json_str, content_type='application/json')

# 搜索标签
def searchTags(request):
    pexel = 'https://www.pexels.com'
    req = requests.get(pexel)
    soup = BeautifulSoup(req.text)
    search__tags = soup.find_all(class_='search__tags')
    results = []
    for tag in search__tags[0]:
        if tag.name == 'li':
            results.append({
                'searchTagName': tag.a.string,
                'searchTagHref': tag.a['href']
            })
    json_str = json.dumps(results)
    return HttpResponse(json_str, content_type='application/json')

# 分类搜索: page
def popularSearches(request):
    page = request.GET.get('page', '1')
    pexel = 'https://www.pexels.com/popular-searches/?page=' + page
    req = requests.get(pexel)
    soup = BeautifulSoup(req.text)
    search_medium = soup.find_all(class_='search-medium__link')
    results = []
    for tag in search_medium:
        print(tag['href'])
        print(tag.h4.string)
        print(tag.img['src'])
        results.append({
            'searchMediumHref': tag['href'],
            'searchMediumText': tag.h4.string,
            'searchMediumSrc': tag.img['src']
        })
    json_str = json.dumps(results)
    return HttpResponse(json_str, content_type='application/json')

# 照片： 搜索、主页、流行
# 搜索板块： href = '/search/job/'
# 用户空间： /u/eberhardgross/
# Popular Photos： 过去三十天 href = '/popular-photos/'
# Popular Photos： 所有      href = '/popular-photos/all-time/'
# 首页100张高质量照片：      href = ''
def photos(request):
    href = request.GET.get('href', '')
    page = '?page=' + request.GET.get('page', '1')
    pexel = 'https://www.pexels.com' + href + page
    post_data = {'page': page}
    req = requests.get(pexel, data=post_data)
    soup = BeautifulSoup(req.text)
    photos = soup.find_all(name='article')
    results = []
    for photo in photos:
        style = photo.img['style'][15:].rstrip(')')
        results.append({'href': photo.a['href'],
                        'alt': photo.img['alt'],
                        'data-pin-media': photo.img['data-pin-media'],
                        'src': photo.img['src'],
                        'height': photo.img['height'],
                        'width': photo.img['width'],
                        'style': style})
    json_str = json.dumps(results)
    return HttpResponse(json_str, content_type='application/json')

# 发现模块，筛选条件
def selected(tag):
    if tag.name == 'section':
        if tag['class'] == ['photo-row'] or tag['class'] == ['photo-row', 'photo-row--user']:
            return True


# 发现: page
def discover(request):
    page = request.GET.get('page', '1')
    pexel = 'https://www.pexels.com/discover/?page=' + page
    req = requests.get(pexel)
    soup = BeautifulSoup(req.text)
    sections = soup.find_all(selected)
    print(len(sections))
    results = []
    for section in sections:
        section_href = ''
        section_title = ''
        imgs = []
        for content in section.contents:
            if content.name == 'header':
                section_href = content.h2.a['href']
                for title in content.h2.a.stripped_strings:
                    section_title = title
            if content.name == 'div':
                for article in content.div.contents:
                    if article.name == 'article':
                        imgs.append({
                            'href': article.a['href'],
                            'alt': article.a.img['alt'],
                            'width': article.a.img['width'],
                            'height': article.a.img['height'],
                            'data-pin-media': article.a.img['data-pin-media'],
                            'src': article.a.img['src'],
                            'style': article.a.img['style'][15:].rstrip(')')
                        })
        if len(imgs) > 0:
            results.append({
                'section_href': section_href,
                'section_title': section_title,
                'imgs': imgs
            })
    json_str = json.dumps(results)
    return HttpResponse(json_str, content_type='application/json')

# Leaderboard: href = ''    href = 'all-time/'
def leaderboard(request):
    href = request.GET.get('href', '')
    page = '?page=' + request.GET.get('page', '1')
    pexel = 'https://www.pexels.com/leaderboard/' + href + page
    req = requests.get(pexel)
    soup = BeautifulSoup(req.text)
    articles = soup.find_all(class_='leaderboard')
    results = []
    for article in articles:
        profile_number = 0  # 排行
        profile_downTimes = 0  # 下载量
        profile_href = ''
        profile_name = ''
        profile_site = ''
        profile_site_name = ''
        profile_avatar = ''
        leaderboard__photos = []
        for cont in article.contents:
            if cont.name == 'div':
                if cont['class'] == ['mini-profile', 'leaderboard__profile']:
                    for profile in cont.contents:
                        if profile.name == 'div':
                            if profile['class'] == ['leaderboard__place']:
                                for num in [profile.contents[1]][0].stripped_strings:
                                    profile_number = num
                                for num in [profile.contents[3]][0].stripped_strings:
                                    profile_downTimes = num
                            if profile['class'] == ['leaderboard__profile-information']:
                                for link in profile.contents:
                                    if link.name == 'h3':
                                        profile_href = profile.h3.a['href']
                                        profile_name = profile.h3.a.string
                                    if link.name == 'a':
                                        profile_site = link['href']
                                        profile_site_name = link.string
                        if profile.name == 'a':
                            profile_avatar = profile.img['src']

                if cont['class'] == ['leaderboard__photos']:
                    for photo in cont.contents:
                        if photo.name == 'a':
                            if photo['class'] == ['leaderboard__photo']:
                                leaderboard__photos.append({
                                    'href': photo['href'],
                                    'src': photo.img['src'],
                                    'height': photo.img['height'],
                                    'width': photo.img['width']
                                })
        leaderboard__profile = {
            'number': profile_number,
            'downTimes': profile_downTimes,
            'href': profile_href,
            'name': profile_name,
            'site': profile_site,
            'siteName': profile_site_name,
            'avatar': profile_avatar
        }
        results.append({
            'leaderboard_profile': leaderboard__profile,
            'leaderboard__photos': leaderboard__photos
        })
    json_str = json.dumps(results)
    return HttpResponse(json_str, content_type='application/json')

# 单张图片预览、下载
# href = '/photo/desktop-wallpaper-hd-wallpaper-hdr-hdr-photography-542385/'
def image(request):
    href = request.GET.get('href', '')
    pexel = 'https://www.pexels.com' + href
    print(pexel)
    req = requests.get(pexel)
    soup = BeautifulSoup(req.text, "html.parser")

    # 2017-10-11 修改： pexel网站节点类名变化，导致解析失败
    # 修改前
    # sections = soup.find_all(class_=['photo-modal__container', 'js-insert-featured-badge'])
    # img = sections[0].a.picture.source.source.img

    # 修改后
    sections = soup.find_all(class_=['photo-modal', 'js-insert-featured-badge'])
    img = sections[0].picture.source.source.img

    style = img['style'][16:].rstrip(')')
    json_str = json.dumps({'href': href,
                           'src': sections[0].a['href'],
                           'style': style})
    return HttpResponse(json_str, content_type='application/json')
