from django.http import HttpResponse
from  pymongo import MongoClient
from django.core.mail import EmailMessage
import json
import re
import random
import time

from django.core.mail import send_mail
from smtplib import SMTPException

# Create your views here.

# 获取验证码： authCode
def authCode(request):
    loginName = request.GET.get('loginName', '')
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
            u'您的验证码为：{0}'.format(num),
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
                'userName': '',
                'backgroundPicture': '',
                'sex': '',
                'phone': '',
                'avatar': '',
                'address': '',
                'profession': '',
                'description': '',
                'lastLoginTime': '',
                'isLogin': False
            }
            # 新用户加入
            USERS.insert(data)
            print('新用户加入')
        try:
            sendEmail = EmailMessage('用户注册', message, to=[loginName])
            sendEmail.send()
            print(loginName)
            # send_mail(
            #     subject=u"xxxxxxxxxx", message=u"通知：xxxxxxxxxx",
            #     from_email='picturewall@163.com', recipient_list=[loginName, ], fail_silently=False,
            # )
            msg = {"isSuccess": True,
                   "msg": 'Verification code sent successfully'}
            return HttpResponse(json.dumps(msg), content_type='application/json')
        except:
            msg = {"isSuccess": False,
                   "msg": 'Verification code sent failure'}
            return HttpResponse(json.dumps(msg), content_type='application/json')
    else:
        msg = {"isSuccess": False,
               "msg": 'Email address is invalid'}
        return HttpResponse(json.dumps(msg), content_type='application/json')



# 注册/重置密码： loginName + authCode + password
def register(request):
    loginName = request.GET.get('loginName', '')
    code = request.GET.get('authCode', '')
    password = request.GET.get('password', '')

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
               "msg": 'Password successfully'}
        return HttpResponse(json.dumps(msg), content_type='application/json')
    else:
        msg = {"isSuccess": False,
               "msg": 'Login name or verification code is wrong'}
        return HttpResponse(json.dumps(msg), content_type='application/json')


# 登陆： loginName + password
def login(request):
    loginName = request.GET.get('loginName', '')
    password = request.GET.get('password', '')
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
        msg = {"isSuccess": True,
               "msg": 'Login successfully'}
        return HttpResponse(json.dumps(msg), content_type='application/json')
    else:
        msg = {"isSuccess": False,
               "msg": 'Account or password is wrong'}
        return HttpResponse(json.dumps(msg), content_type='application/json')

# 退出登录: loginName + password
def logout(request):
    loginName = request.GET.get('loginName', '')
    password = request.GET.get('password', '')
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
    loginName = request.GET.get('loginName', '')
    password = request.GET.get('password', '')
    if loginName == '' and password == '':
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
        if request.GET.get('userName', '') != '':
            data['userName'] = request.GET.get('userName', '')
        if request.GET.get('backgroundPicture', '') != '':
            data['backgroundPicture'] = request.GET.get('backgroundPicture', '')
        if request.GET.get('sex', '') != '':
            data['sex'] = request.GET.get('sex', '')
        if request.GET.get('phone', '') != '':
            data['phone'] = request.GET.get('phone', '')
        if request.GET.get('avatar', '') != '':
            data['avatar'] = request.GET.get('avatar', '')
        if request.GET.get('address', '') != '':
            data['address'] = request.GET.get('address', '')
        if request.GET.get('profession', '') != '':
            data['profession'] = request.GET.get('profession', '')
        if request.GET.get('description', '') != '':
            data['description'] = request.GET.get('description', '')
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
            'isLogin': user['isLogin']
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



