from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from . import tools
from .models import UserInfo
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse


# Create your views here.

def index(request):
    return render(request, 'ipa/index.html', {'user': '大王'})

def login(request):
    return render(request, 'ipa/login.html')

def register(request):
    return render(request, 'ipa/register.html')

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



# 提交邮箱验证
def signup(request):
    if request.method == 'POST':
        print(request.POST['email'])
        email = request.POST['email']
        try:
            user = UserInfo.objects.get(email=email)
            return HttpResponse("用户已存在,可直接登陆")
        except:
            user = UserInfo.objects.create(username='', password='', email=email, is_active=0)
            user.save()
            token = tools.Token().generate_validate_token(key=email)
            print(token)
            print(tools.Token().confirm_validate_token(token=token))
            print(request.path)
            print(request.get_host())
            print(request.get_full_path())
            message = "\n".join([
                u'{0},欢迎您的加入'.format(request.POST['email']),
                u'请访问该链接，完成用户验证:',
                'http://' + request.get_host() + '/signup?token=' + token
            ])
            print(message)
            # send_mail(u'注册用户验证信息', message, "tongxingpay2016@163.com", [email])
            return HttpResponse('已发送验证邮件到你的邮箱，请查看。')
    else:
        try:
            email = tools.Token().confirm_validate_token(request.GET['token'])
            print("验证：" + email)
        except:
            return HttpResponse(u'对不起，验证链接已经过期')
        print(UserInfo.objects.all())
        for us in UserInfo.objects.all():
            print(us.email)
        user = UserInfo.objects.get(email=email)
        # print(user.email)
        # try:
        #     print("查询结果：" + UserInfo.objects.get(email=email))
        #     user = UserInfo.objects.get(email=email)
        #     # print("查询结果：" + UserInfo.objects.get(email=email))
        # except:
        #     return HttpResponse(u'用户不存在，请重新注册！')
        user.is_active = 1
        user.save()
        return HttpResponseRedirect(reverse('ipa:password', args=(1, email,)))

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
            return HttpResponse('密码不能为空')
        if second == "":
            return HttpResponse('密码不能为空')
        if first == second:
            user = get_object_or_404(UserInfo, email=email)
            user.password = second
            user.save()
            # render(request, 'ipa/login.html')
            return HttpResponseRedirect(reverse('ipa:login', args=(None)))
        else:
            return HttpResponse('两次密码不一致')


# 登陆验证
def checklogin(request):
    u_name = request.POST['email']
    u_psw = request.POST['password']
    try:
        user = UserInfo.objects.get(email=u_name)
    except UserInfo.DoesNotExist:
        return HttpResponse('用户不存在')
    if user.is_active == 0:
        return HttpResponse('尚未验证用户邮箱，请点击验证邮件中的链接或者重新注册')
    if user.password != u_psw:
        return HttpResponse('密码错误')
    print(u_name)
    print(u_psw)
    return HttpResponse('登陆成功')


# token验证
def active_user(request, token):
    return render(request)