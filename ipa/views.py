from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail, EmailMessage
from .tools import Token
from .models import UserProfile
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from qiniu import Auth, put_file, etag
import os, json
import markdown2
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import auth
from .forms import RegistrationForm
import requests

# Create your views here.
sections = [
            '微信小程序', '支付宝支付','百度钱包','中华人民共和国','四川晋商支付信息技术'
        ]

def index(request):
    current_user = ''
    email = ''
    if request.user.is_authenticated:
        print("当前登陆用户：" + request.user.username)
        current_user = request.user.email
        email = request.user.email
    print("用户：" + current_user)
    return render(request, 'ipa/index.html', {
        'user': current_user,
        'email': email,
        'avatar': ""
    })


def login(request):
    return render(request, 'ipa/login.html')

def register(request, reset):
    print(reset)
    # 新用户
    if reset == "0":
        return render(request, 'ipa/register.html', {
            'reset': u"Jmsp 将发送一封验证邮件到你的邮箱，此邮箱将作为登陆用户名",
            'is_active': "0"
        })
    else:
        # 找回密码用户
        return render(request, 'ipa/register.html', {
            'reset': u'Jmsp 将发送一封验证邮件到你的注册邮箱，请注意查收！',
            'is_active': "1"
        })

def password(request, type, email):
    try:
        User.objects.get(email=email)
    except User.DoesNotExist:
        return HttpResponse('【邮箱尚未验证】<a href="/register/0">注册此邮箱</a>')
    if type == '1':
        return render(request, 'ipa/password.html', {"titletype": "2、设置密码", "email": email})
    else:
        return render(request, 'ipa/password.html', {"titletype": "2、重置密码", "email": email})


def home(request):
    if request.user.is_authenticated:
        print("当前用户：" + request.user.username)
        # sections = [
        #     '微信小程序', '支付宝支付','百度钱包','中华人民共和国','四川晋商支付信息技术'
        # ]
        return render(request, 'ipa/home.html', {
            'email': request.user.email,
            'hasContent': 0,
            'avatar': UserProfile.objects.get(user=request.user).avatar,
            'sections': sections
        })
    else:
        print("用户未登录，请先登录")
        return render(request, 'ipa/login.html')

# home界面功能选择
def selected_section(request, section):
    print(request)
    print(int(section))
    index = int(section) - 1
    print(sections[index])
    return render(request, 'ipa/weixin_sender.html', {
            'email': request.user.email,
            'avatar': UserProfile.objects.get(user=request.user).avatar,
        })

# 微信小程序--模板消息发送
def wxapp_sender(request):
    print(request)
    appid = request.GET['AppID']
    appSecret = request.GET['AppSecret']
    code= request.GET['Code']
    formId = request.GET['FormId']
    open_data = {'appid': appid, 'secret': appSecret, 'js_code': code, 'grant_type': 'authorization_code'}
    open_res = requests.get('https://api.weixin.qq.com/sns/jscode2session', params=open_data)
    open_json_data = open_res.json()
    openId = open_json_data['openid']

    access_token_data = {'appid': appid, 'secret': appSecret, 'grant_type': 'client_credential'}
    access_res = requests.get('https://api.weixin.qq.com/cgi-bin/token', params=access_token_data)
    access_json_data = access_res.json()
    access_token = access_json_data['access_token']
    # wxccf061de2a3561f3 @ b8bb00596ad6c01af471b926decc3df4 @ 799
    # ce58cea9eb6c50abf7ffce5f73173 @ 0815
    # Fz2C1NBLh10QUB0C1HxD2C15Fz20 @ oac3u0K8w8q4l2rOz1AnG1

    data = {
                  'access_token': access_token,
                  'touser': openId,
                  'form_id': formId,
                  'template_id': 'QC4qBiCIvqZsaBGMOi4hmhRqPRlW8QrRDyt50zksSzk',
                  'page': 'pages/home/home',
                  'data': {
                    'keyword1': {
                      'value': 'keyword1'
                    },
                    'keyword2': {
                      'value': 'keyword1'
                    },
                    'keyword3': {
                      'value': 'keyword1'
                    },
                    'keyword4': {
                      'value': 'keyword1'
                    },
                    'keyword5': {
                      'value': 'keyword1'
                    },
                    'keyword6': {
                      'value': 'keyword1'
                    },
                    'keyword7': {
                      'value': 'keyword1'
                    },
                    'keyword8': {
                      'value': 'keyword1'
                    },
                    'keyword9': {
                      'value': 'keyword1'
                    }
                  }
                }
    json_data = json.dumps(data)
    sender_res = requests.post('https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send', params=json_data)
    sender_json_data = sender_res.json()
    print(sender_json_data)

    # return JsonResponse({'AppID': "dsd"})
    return JsonResponse({'AppID': appid,
                         'AppSecret': appSecret,
                         'Code': code,
                         'FormId': formId,
                         'openId': openId,
                         'access_token': access_token,
                         'errmsg': sender_json_data['errmsg'],
                         'errcode': sender_json_data['errcode']
                         })

# 文件上传
def upload_file(request):
    myFile = request.FILES.get("file", None)  # 获取上传的文件，如果没有文件，则默认为None
    print(myFile.size)
    # email = request.POST['email']
    if request.user.is_authenticated == 0:
        return render(request, 'ipa/login.html')
    email = request.user.email
    print(email)
    # email = 'zhangzhaopds@foxmail.com'
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(BASE_DIR, 'ipa/static/ipa/images/')
    print(path)
    localfile = os.path.join(path, myFile.name)
    if not myFile:
        return HttpResponse("no files for upload!")
    destination = open(localfile, 'wb+')  # 打开特定的文件进行二进制的写操作
    for chunk in myFile.chunks():  # 分块写入文件
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
    key = email + "/" + myFile.name

    # 上传文件到七牛后， 七牛将文件名和文件大小回调给业务服务器。
    # policy = {
    #     'callbackUrl': 'http://your.domain.com/callback.php',
    #     'callbackBody': 'filename=$(fname)&filesize=$(fsize)'
    # }

    # 不能出现 http://  或者 https:// 字样，否则heroku中出错
    base = 'opu0gas3t.bkt.clouddn.com/'

    # 生成上传 Token，可以指定过期时间等
    token = a.upload_token(bucket_name, key, 3600)

    ret, info = put_file(token, key, localfile)
    print(info)
    print(info.status_code)
    assert ret['key'] == key
    assert ret['hash'] == etag(localfile)
    # user = User.objects.get(email=email)
    user = User.objects.get(email=email)
    print(user.username)
    usr = UserProfile.objects.get(user__username=user.username)
    usr.avatar = 'http://' + base + key
    usr.save()
    os.remove(localfile)
    print('上传完毕' + usr.avatar)
    return render(request, 'ipa/home.html', {
        'hasContent': 1,
        'content': '上传完毕',
        'email': email,
        'img_url': usr.avatar,
        'avatar': usr.avatar
    })



def upload_file_change(value):
    print(")_)_)_)_)_")
    print(value)
    print('改变-------')


# 提交邮箱验证
def signup(request):
    if request.method == 'POST':
        print(request.POST['email'])
        email = request.POST['email']
        active = request.POST['active'] # 0: 注册， 1：找回
        # 找回密码
        if active == '1':
          try:
              user = User.objects.get(email=email)
              token = Token().generate_validate_token(key=email)
              message = '\n'.join([
                  u'{0},欢迎您的加入'.format(email),
                  u'请点击下面链接，完成用户密码重置:',
                  u'https://' + request.get_host() + '/signup?token=' + token
              ])
              print(message)
              try:
                  sendEmail = EmailMessage('注册用户验证信息', message, to=[email])
                  sendEmail.send()
                  user.is_active = 0
                  user.save()
                  return HttpResponse('【邮件发送成功，请注意查收！】')
              except:
                  print(email + u'【邮件发送失败】')
                  return HttpResponse(email + '【邮箱发送失败】')
          except User.DoesNotExist:
              return HttpResponse("【邮箱尚未注册】")
        # 注册
        try:
            User.objects.get(email=email)
            print('存在')
            return HttpResponse('【邮箱已经被注册】<a href="/login">立即登陆</a>')
        except User.DoesNotExist:
            token = Token().generate_validate_token(key=email)
            message = '\n'.join([
                u'{0},欢迎您的加入'.format(email),
                u'请点击下面链接，完成用户验证:',
                u'https://' + request.get_host() + '/signup?token=' + token
            ])
            print(message)
            try:
                sendEmail = EmailMessage('注册用户验证信息', message, to=[email])
                sendEmail.send()
                user = User.objects.create_user(email[:3], email, '123456')
                user.is_active = 0
                user.save()
                usr = UserProfile.objects.create()
                usr.user = user
                usr.save()
                return HttpResponse('【邮件发送成功，请注意查收！】')
            except:
                print(email + u'【邮件发送失败】')
                return HttpResponse(email + '【邮箱发送失败】')
    else:
        try:
            email = Token().confirm_validate_token(request.GET['token'])
            print("验证：" + email)
            return HttpResponseRedirect(reverse('ipa:password', args=(1, email,)))
        except:
            return HttpResponse(u'对不起，验证链接已经过期')


# 密码提交验证
def checkpsw(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data['username'])
            print(form.cleaned_data['password2'])
            print(form.cleaned_data['password1'])
            print(form.cleaned_data['email'])
            try:
                user = User.objects.get(email=form.cleaned_data['email'])
                if form.cleaned_data['password2']:
                    user.username = form.cleaned_data['username']
                    user.password = form.cleaned_data['password2']
                    user.is_active = 1
                    user.save()
                    return HttpResponseRedirect(reverse('ipa:login', args=(None)))
                else:
                    return HttpResponse('注册失败，密码不一致')
            except User.DoesNotExist:
                return HttpResponse('该邮箱尚未验证')
        return HttpResponse('注册失败，填写信息有误')


# 登陆验证
def checklogin(request):
    u_email = request.POST['email']
    u_psw = request.POST['password']
    print("登陆验证：" + u_psw)
    try:
        user = User.objects.get(email=u_email)
        # user.password = '11223344'
        # user.save()
        print(user.password)
        if user.is_active == 0:
            return render(request, 'ipa/login.html', {
                'error_info': u'尚未验证用户邮箱，请点击验证邮件中的链接进行验证或者重新注册'
            })
        if user.password != u_psw:
            return render(request, 'ipa/login.html', {
                'error_info': '密码错误',
                'user_name': user.email
            })
        print(u_email)
        print(u_psw)
        # user.is_authenticated = 1
        print("登陆认证：")
        uu = authenticate(username=user.username, password=user.password)
        print(uu)
        print(user.is_authenticated)


        print(user.password)
        print(user.username)
        auth.login(request, user)
        print("登陆认证：")
        return HttpResponseRedirect(reverse('ipa:home', args=(None)))
        # return render(request, 'ipa/home.html')
    except User.DoesNotExist:
        return render(request, 'ipa/login.html', {
            'error_info': '用户不存在'
        })

def do_logout(request):
    print("退出的登陆")
    auth.logout(request)
    # return render(request, 'ipa/index.html', {'user': ''})
    return HttpResponseRedirect(reverse('ipa:index', args=(None)))


# token验证
def active_user(request, token):
    return render(request)