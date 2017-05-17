from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail, EmailMessage
from . import tools
from .models import UserInfo
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from qiniu import Auth, put_file, etag
import os
import markdown2


# Create your views here.

def index(request):
    return render(request, 'ipa/index.html', {'user': '大王'})

def login(request):
    return render(request, 'ipa/login.html')

def register(request, reset):
    print(reset)
    if reset == "0":
        return render(request, 'ipa/register.html', {
            'reset': u"Jmsp 将发送一封验证邮件到你的邮箱，此邮箱将作为登陆用户名",
            'is_active': 1
        })
    else:
        return render(request, 'ipa/register.html', {
            'reset': u'Jmsp 将发送一封验证邮件到你的注册邮箱，请注意查收！',
            'is_active': 0
        })

def password(request, type, email):
    print(type)
    print(email)
    try:
        UserInfo.objects.get(email=email)
    except UserInfo.DoesNotExist:
        return HttpResponse('用户不存在')
    if type == '1':
        return render(request, 'ipa/password.html', {"titletype": "2、设置密码", "email": email})
    else:
        return render(request, 'ipa/password.html', {"titletype": "2、重置密码", "email": email})


def home(request, email):
    print(email)

    return render(request, 'ipa/home.html', {
        'email': email,
        'hasContent': 0,
        'upload_file_change': upload_file_change(email)
    })

# 文件上传
def upload_file(request):
    myFile = request.FILES.get("file", None)  # 获取上传的文件，如果没有文件，则默认为None
    print(myFile.size)
    # email = request.POST['email']
    email = 'zhangzhaopds@foxmail.com'
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

    base = 'http://opu0gas3t.bkt.clouddn.com/'

    # 生成上传 Token，可以指定过期时间等
    token = a.upload_token(bucket_name, key, 3600)

    ret, info = put_file(token, key, localfile)
    print(info)
    print(info.status_code)
    assert ret['key'] == key
    assert ret['hash'] == etag(localfile)
    user = get_object_or_404(UserInfo, email=email)
    user.username = base + key
    user.save()
    os.remove(localfile)
    print('上传完毕')
    return render(request, 'ipa/home.html', {
        'hasContent': 1,
        'content': '上传完毕',
        'img_url': user.username
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
        active = request.POST['active'] # 1: 注册， 0：找回


        # 注册与找回  都删除重建
        UserInfo.objects.filter(email=email).delete()

        token = tools.Token().generate_validate_token(key=email)

        message = "\n".join([
            u'{0},欢迎您的加入'.format(request.POST['email']),
            u'请访问该链接，完成用户验证:',
            'https://' + request.get_host() + '/signup?token=' + token
        ])
        print(message)
        try:
            emails = EmailMessage('注册用户验证信息', message, to=[email])
            emails.send()
            user = UserInfo.objects.create(username='', password='', email=email, is_active=0)
            user.save()
            return HttpResponse('已发送验证邮件到你的邮箱，请查看。')
        except:
            return HttpResponse('邮件发送失败')

    else:
        try:
            email = tools.Token().confirm_validate_token(request.GET['token'])
            print("验证：" + email)
            return HttpResponseRedirect(reverse('ipa:password', args=(1, email,)))
        except:
            return HttpResponse(u'对不起，验证链接已经过期')


# 密码提交验证
def checkpsw(request):
    if request.method == "POST":
        first = request.POST['first_input']
        second = request.POST['second_input']
        email = request.POST['email']
        print(request.POST['first_input'])
        print(request.POST['second_input'])
        print(email)
        if first == "":
            return render(request, 'ipa/password.html', {
                'error_info': '密码不能为空',
                "titletype": "2、设置密码",
                "email": email
            })
        if second == "":
            return render(request, 'ipa/password.html', {
                'error_info': '密码不能为空',
                "titletype": "2、设置密码",
                "email": email
            })
        if first == second:
            user = get_object_or_404(UserInfo, email=email)
            user.password = second
            user.is_active = 1
            user.save()
            # render(request, 'ipa/login.html')
            return HttpResponseRedirect(reverse('ipa:login', args=(None)))
        else:
            return render(request, 'ipa/password.html', {
                'error_info': '密码不一致',
                "titletype": "2、设置密码",
                "email": email
            })




# 登陆验证
def checklogin(request):
    u_name = request.POST['email']
    u_psw = request.POST['password']
    try:
        user = UserInfo.objects.get(email=u_name)
    except UserInfo.DoesNotExist:
        return render(request, 'ipa/login.html', {
            'error_info': '用户不存在'
        })
    if user.is_active == 0:
        return render(request, 'ipa/login.html', {
            'error_info': u'尚未验证用户邮箱，请点击验证邮件中的链接进行验证或者重新注册'
        })
    if user.password != u_psw:
        return render(request, 'ipa/login.html', {
            'error_info': '密码错误',
            'user_name': u_name
        })
    print(u_name)
    print(u_psw)
    return HttpResponseRedirect(reverse('ipa:home', args=(u_name,)))


# token验证
def active_user(request, token):
    return render(request)